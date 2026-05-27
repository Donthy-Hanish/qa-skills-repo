# Authentication Patterns for Contract Runner

Configure auth in `contract_runner.py` by replacing the `authenticate()` function with the pattern that matches the user's API.

---

## Pattern A: Two-Step JWT (Login → Token Exchange)

Used when: enterprise/multi-tenant APIs where a basic login token must be upgraded to a privileged one.

```python
LOGIN_URL = "https://your-auth-service.com/api/v1/login"
TOKEN_EXCHANGE_URL = "https://your-api.com/api/v1/token/generateAuthorizationToken"
APP_KEY = "your-application-key-uuid"

LOGIN_PAYLOAD = {
    "emailAddress": "test@yourcompany.com",
    "password": "your-password",
    "rememberMe": False
}

def authenticate():
    login_resp = requests.post(
        LOGIN_URL,
        json=LOGIN_PAYLOAD,
        headers={"application-key": APP_KEY},
        verify=SSL_VERIFY
    )
    if login_resp.status_code != 200:
        print(f"Login failed: {login_resp.status_code} {login_resp.text}")
        sys.exit(1)
    lobby_token = login_resp.json()["data"]["token"]
    print("Step 1: lobby token acquired")

    exch_resp = requests.post(
        TOKEN_EXCHANGE_URL,
        json={"tenantId": 2, "roleId": None},
        headers={
            "authorization-token": lobby_token,
            "Content-Type": "application/json"
        },
        verify=SSL_VERIFY
    )
    if exch_resp.status_code != 200:
        print(f"Token exchange failed: {exch_resp.status_code} {exch_resp.text}")
        sys.exit(1)

    data = exch_resp.json()
    master_token = (
        data.get("data", {}).get("authorizationToken")
        or data.get("data", {}).get("token")
        or data.get("authorizationToken")
        or data.get("token")
        or exch_resp.text.strip('"')
    )
    if not str(master_token).startswith("eyJ"):
        print(f"Invalid JWT extracted. Raw response: {exch_resp.text[:200]}")
        sys.exit(1)

    print("Step 2: master token acquired")
    return {"authorization-token": str(master_token)}
```

---

## Pattern B: Single Bearer Token Login

Used when: standard JWT API with a single login endpoint.

```python
LOGIN_URL = "https://your-api.com/auth/login"

def authenticate():
    resp = requests.post(
        LOGIN_URL,
        json={"username": "test@yourcompany.com", "password": "your-password"},
        verify=SSL_VERIFY
    )
    if resp.status_code != 200:
        print(f"Login failed: {resp.status_code}")
        sys.exit(1)
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

---

## Pattern C: Static API Key

Used when: the API uses a fixed key passed in a header.

```python
API_KEY = "your-static-api-key"

def authenticate():
    return {"X-API-Key": API_KEY}
```

---

## Pattern D: OAuth2 Client Credentials

Used when: machine-to-machine auth with an OAuth2 token endpoint.

```python
TOKEN_URL = "https://auth.yourcompany.com/oauth/token"
CLIENT_ID = "your-client-id"
CLIENT_SECRET = "your-client-secret"

def authenticate():
    resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        verify=SSL_VERIFY
    )
    if resp.status_code != 200:
        print(f"OAuth2 token request failed: {resp.status_code}")
        sys.exit(1)
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

---

## Diagnosing Auth Issues

If unsure which pattern applies, ask the user to:
1. Open the app in a browser and log in
2. Open DevTools → Network tab → find the login request
3. Share: the URL it calls, the request body shape, and where the token appears in the response

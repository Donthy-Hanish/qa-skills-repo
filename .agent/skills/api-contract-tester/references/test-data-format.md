# Writing test_data.csv

## Format

Each row is one test scenario.

```
Endpoint,Method,Scenario,Expected Status,Payload
```

| Column | Description |
|--------|-------------|
| `Endpoint` | The path from the Swagger spec, e.g. `/api/v1/jobs` |
| `Method` | `GET`, `POST`, `PUT`, `PATCH`, or `DELETE` (uppercase) |
| `Scenario` | A human-readable name that will appear in the report |
| `Expected Status` | The HTTP status code you expect back (200, 201, 400, 404, etc.) |
| `Payload` | JSON object as a string. Use `{}` for GET. Double up inner quotes: `""field""` |

---

## Payload Quoting

CSV requires that a JSON object containing commas be wrapped in outer quotes, and that internal double-quotes be doubled:

```csv
/api/v1/jobs,POST,Valid Job Creation,200,"{""title"": ""Registered Nurse"", ""facilityId"": 101}"
```

Most editors (Excel, Google Sheets) handle this automatically if you type the payload in a cell.

---

## Recommended Coverage Per Endpoint

### POST / PUT (write operations)
```csv
/api/v1/jobs,POST,Happy path - all valid fields,200,"{""title"": ""Nurse"", ""facilityId"": 101}"
/api/v1/jobs,POST,Missing required title,400,"{""facilityId"": 101}"
/api/v1/jobs,POST,Duplicate creation,409,"{""title"": ""Existing Job"", ""facilityId"": 101}"
```

### GET (read operations)
```csv
/api/v1/jobs,GET,Fetch all jobs,200,{}
/api/v1/jobs/42,GET,Fetch existing job by ID,200,{}
/api/v1/jobs/99999,GET,Fetch non-existent job,404,{}
```

---

## Priority Rules

- CSV scenarios run **first** and take **priority** over auto-generated Swagger tests
- Endpoints not in the CSV still get auto-generated smoke tests from the Swagger spec
- Only write CSV rows where you want specific payload control

---

## Tips

- Use realistic IDs that actually exist in the staging database for 200-expected GET tests
- For 400 tests, remove one required field at a time to isolate which validation triggers
- Add a `Scenario` name that describes the intent clearly — it's the label you'll search for in the report

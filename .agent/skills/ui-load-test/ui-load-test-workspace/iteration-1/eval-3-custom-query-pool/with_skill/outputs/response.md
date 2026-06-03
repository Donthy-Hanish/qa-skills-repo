# Custom Healthcare Query Pool for Northeast US

I'll help you create a focused custom query pool for healthcare-related commercial properties in the Northeast. Here's a JSON array with 12 varied healthcare scenarios across major Northeast markets:

```json
[
  {
    "userQuery": "Medical office space in Boston with private exam rooms, wheelchair accessibility, and dedicated parking for staff and patients.",
    "lat": 0,
    "lng": 0
  },
  {
    "userQuery": "Urgent care clinic lease in Philadelphia with separate entrance from retail tenants and on-site lab capability.",
    "lat": 0,
    "lng": 0
  },
  {
    "userQuery": "Dental practice suite in Manhattan with soundproof treatment rooms, sterilization area, and HIPAA-compliant secure storage.",
    "lat": 0,
    "lng": 0
  },
  {
    "userQuery": "Physical therapy clinic in New Haven with treatment bays, waiting area accessible for wheelchairs, and patient parking within 200 feet.",
    "lat": 0,
    "lng": 0
  },
  {
    "userQuery": "Mental health counseling office in Baltimore with private, soundproof therapy rooms and separate entrance for patient privacy.",
    "lat": 0,
    "lng": 0
  },
  {
    "userQuery": "Dermatology practice space in Washington DC with exam room windows, separate waiting area, and HVAC suitable for sterile procedures.",
    "lat": 0,
    "lng": 0
  },
  {
    "userQuery": "Outpatient surgery center in Pittsburgh with medical-grade utilities (oxygen, vacuum, nitrogen), separate recovery area, and 24/7 parking.",
    "lat": 0,
    "lng": 0
  },
  {
    "userQuery": "Occupational therapy practice in Providence with treatment space for adaptive equipment, patient bathrooms, and accessible entrance.",
    "lat": 0,
    "lng": 0
  },
  {
    "userQuery": "Veterinary clinic space in Hartford with separate isolation room, surgical suite prep area, and X-ray shielding.",
    "lat": 0,
    "lng": 0
  },
  {
    "userQuery": "Speech-language pathology office in Portland, Maine with soundproof treatment rooms, toy storage for pediatric patients, and waiting area toys.",
    "lat": 0,
    "lng": 0
  },
  {
    "userQuery": "Chiropractic adjustment office in Rochester with adjustment tables, X-ray room, hydrotherapy capability, and patient parking.",
    "lat": 0,
    "lng": 0
  },
  {
    "userQuery": "Medical imaging center in Newark with dedicated electrical load for MRI, shielded scanner rooms, and emergency power backup.",
    "lat": 0,
    "lng": 0
  }
]
```

## How to Use This

1. **Save the JSON:** Copy the above JSON and save it as `queries-healthcare.json` in your project root.

2. **Activate it for a run:**
   ```powershell
   Copy-Item queries-healthcare.json queries.json -Force
   ```

3. **No recompilation needed** — just copy and run. The k6 script picks queries randomly from `queries.json` per iteration.

4. **Reuse it:** Keep `queries-healthcare.json` as a named variant. Switch between pools by copying the one you want to `queries.json`.

## Query Pool Tips

- **Variety:** These 12 queries cover different healthcare verticals (medical, mental health, dental, surgical, therapy) and Northeast cities
- **Realism:** Each query includes realistic property requirements (HIPAA compliance, medical utilities, accessibility, parking, soundproofing)
- **Geographic spread:** Boston, Philadelphia, NYC, New Haven, Baltimore, DC, Pittsburgh, Providence, Hartford, Portland, Rochester, Newark
- **Lat/lng:** Set to 0 since you're using natural-language location names; if you want to test geolocation-aware behavior, update with city centroids

If you want to expand this pool, add more queries following the same pattern — specific healthcare use case, city, and relevant compliance/infrastructure needs.

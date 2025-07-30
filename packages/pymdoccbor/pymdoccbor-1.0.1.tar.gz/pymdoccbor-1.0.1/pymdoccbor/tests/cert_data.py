from datetime import datetime, timezone, timedelta

CERT_DATA ={
    "country_name": "US",
    "state_or_province_name": "California",
    "locality_name": "San Francisco",
    "organization_name": "Micov",
    "common_name": "My Company",
    "san_url": "mysite.com",
    "not_valid_before": datetime.now(timezone.utc) - timedelta(days=1),
    "not_valid_after": datetime.now(timezone.utc) + timedelta(days=10),
    "san_url": "https://credential-issuer.example.org"
}
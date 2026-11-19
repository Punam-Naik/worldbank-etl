import urllib.request
import json

URL = (
    "https://api.worldbank.org/v2/country/IND/indicator/SP.POP.TOTL"
    "?format=json&date=2000:2024&per_page=100"
)

with urllib.request.urlopen(URL, timeout=30) as response:
    print("HTTP Status:", response.status)
    data = json.loads(response.read().decode("utf-8"))

metadata = data[0]
records = data[1]

print("\nAPI METADATA")
print(json.dumps(metadata, indent=2))

print("\nRECORD COUNT:", len(records))

print("\nSAMPLE RECORDS")
for record in records[:5]:
    print({
        "country_code": record["countryiso3code"],
        "country": record["country"]["value"],
        "indicator_code": record["indicator"]["id"],
        "indicator": record["indicator"]["value"],
        "year": record["date"],
        "value": record["value"]
    })

print("\nNULL VALUES:", sum(r["value"] is None for r in records))
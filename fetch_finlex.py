import requests
import xmltodict
import json

# Finlexin API-endpoint (tarkista, että tämä URL toimii selaimessa!)
FINLEX_API_URL = "https://data.finlex.fi/eli/sd/2018/729/ajantasa"

# 1️⃣ Haetaan XML-data Finlexistä
response = requests.get(FINLEX_API_URL)

# Tarkistetaan, onnistuiko pyyntö
if response.status_code != 200:
    print(f"Virhe ladattaessa Finlex-dataa: HTTP {response.status_code}")
    print("Palautettu data:")
    print(response.text[:500])  # Tulostetaan 500 merkkiä saadusta vastauksesta
    exit(1)

xml_data = response.text

# 2️⃣ Muunnetaan XML JSON-muotoon
try:
    parsed_data = xmltodict.parse(xml_data)
except Exception as e:
    print("Virhe XML-datan käsittelyssä:", str(e))
    exit(1)

# 3️⃣ Poimitaan tärkeät osiot
try:
    law_data = {
        "name": parsed_data["akomaNtoso"]["act"]["meta"]["identification"]["FRBRWork"]["FRBRalias"]["@value"],
        "children": []
    }
except KeyError:
    print("XML-datasta ei löytynyt odotettua rakennetta. Tässä näyte saadusta XML:stä:")
    print(xml_data[:500])
    exit(1)

# 4️⃣ Tallennetaan JSON-muotoon
with open("finlex_data.json", "w", encoding="utf-8") as f:
    json.dump(law_data, f, ensure_ascii=False, indent=4)

print("Finlex-data päivitetty ja tallennettu JSON-muotoon!")

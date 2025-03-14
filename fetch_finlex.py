import requests
import xmltodict
import json

# Finlexin API-endpoint säädöslistalle
LISTA_URL = "https://api.finlex.fi/v0/eli/sd/list"

# 1️⃣ Haetaan lista säädöksistä
response = requests.get(LISTA_URL)

# Tarkistetaan, palauttiko API järkevää sisältöä
if response.status_code != 200:
    print(f"Virhe ladattaessa säädöslista: HTTP {response.status_code}")
    print("Palautettu data:")
    print(response.text[:500])  # Näytä ensimmäiset 500 merkkiä saadusta datasta
    exit(1)

# Tarkistetaan, onko vastaus tyhjä
if not response.text.strip():
    print("Virhe: Finlex API palautti tyhjän vastauksen!")
    exit(1)

try:
    laws_list = response.json()
except requests.exceptions.JSONDecodeError:
    print("Virhe: Finlex API ei palauttanut JSON-dataa! Vastaus:")
    print(response.text[:500])  # Näytä osa saadusta datasta
    exit(1)

# 2️⃣ Valitaan ensimmäinen säädös listalta
if "results" not in laws_list or len(laws_list["results"]) == 0:
    print("Ei löydetty säädöksiä Finlexistä!")
    exit(1)

first_law = laws_list["results"][0]
law_url = first_law.get("versions", {}).get("ajantasa")

if not law_url:
    print("Virhe: Ensimmäisellä säädöksellä ei ole ajantasaista versiota.")
    exit(1)

print(f"Ladataan laki osoitteesta: {law_url}")

# 3️⃣ Haetaan yksittäisen lain XML
response = requests.get(law_url)

if response.status_code != 200:
    print(f"Virhe ladattaessa lakiteksti: HTTP {response.status_code}")
    exit(1)

xml_data = response.text

# 4️⃣ Muunnetaan XML JSON-muotoon
try:
    parsed_data = xmltodict.parse(xml_data)
except Exception as e:
    print("Virhe XML-datan käsittelyssä:", str(e))
    exit(1)

# 5️⃣ Poimitaan tärkeät osiot
try:
    law_data = {
        "name": parsed_data["akomaNtoso"]["act"]["meta"]["identification"]["FRBRWork"]["FRBRalias"]["@value"],
        "children": []
    }
except KeyError:
    print("XML-datasta ei löytynyt odotettua rakennetta.")
    exit(1)

# 6️⃣ Tallennetaan JSON-muotoon
with open("finlex_data.json", "w", encoding="utf-8") as f:
    json.dump(law_data, f, ensure_ascii=False, indent=4)

print("Finlex-data päivitetty ja tallennettu JSON-muotoon!")

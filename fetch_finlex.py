import requests
import xmltodict
import json

# 1️⃣ Haetaan lista säädöksistä Finlexin API:sta
LISTA_URL = "https://api.finlex.fi/v0/eli/sd/list"

response = requests.get(LISTA_URL)
if response.status_code != 200:
    print(f"Virhe ladattaessa säädöslista: HTTP {response.status_code}")
    exit(1)

laws_list = response.json()

# 2️⃣ Valitaan ensimmäinen säädös (voit muuttaa logiikkaa valitsemaan tietyn lain)
if "results" not in laws_list or len(laws_list["results"]) == 0:
    print("Ei löydetty säädöksiä!")
    exit(1)

first_law = laws_list["results"][0]  # Ota ensimmäinen löydetty laki
law_url = first_law["versions"]["ajantasa"]  # Hae ajantasainen versio

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

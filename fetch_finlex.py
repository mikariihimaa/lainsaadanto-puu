import requests
import xmltodict
import json
import re
import time

# 🔗 Haetaan säädösluettelo Finlexin API:sta
FINLEX_API_LIST_URL = "https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute/list?format=json"

response = requests.get(FINLEX_API_LIST_URL)

if response.status_code != 200:
    print(f"❌ Virhe ladattaessa säädöslista: HTTP {response.status_code}")
    exit(1)

laws_list = response.json()

# 🛠️ Tulostetaan testimielessä 5 ensimmäistä säädöstä
print("\n🔍 API palautti seuraavat säädökset:")
for law in laws_list[:5]:
    print(f" - {law['akn_uri']} (tila: {law['status']})")

# Tarkistetaan, löytyykö säädöksiä
if not isinstance(laws_list, list) or len(laws_list) == 0:
    print("❌ Ei löydetty säädöksiä Finlexistä!")
    exit(1)

laws = {}

# 2️⃣ Haetaan yksittäisiä lakeja käyttäen `main.xml`-muotoa
for law in laws_list[:10]:  # Testataan 10 ensimmäistä
    if not law["akn_uri"].startswith("https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute/"):
        continue

    # Eristetään säädöksen vuosi ja numero
    parts = law["akn_uri"].split("/")
    if len(parts) < 10:
        continue

    year = parts[10]
    number = parts[11]

    # Uusi latausosoite (ajantasa XML)
    law_url = f"https://data.finlex.fi/eli/sd/{year}/{number}/ajantasa/main.xml"

    print(f"\n📥 Haetaan laki: {law_url}")

    xml_response = requests.get(law_url)
    time.sleep(1)

    if xml_response.status_code != 200:
        print(f"⚠️ Virhe ladattaessa lakia {law_url}: HTTP {xml_response.status_code}")
        continue

    xml_data = xml_response.text

    # 3️⃣ Etsitään lakitekstistä nimi (XML:stä)
    try:
        parsed_data = xmltodict.parse(xml_data)
        law_title = parsed_data["akomaNtoso"]["act"]["meta"]["identification"]["FRBRWork"]["FRBRalias"]["@value"]
    except (KeyError, TypeError):
        law_title = f"{year}/{number}"  # Oletusnimi, jos XML ei sisällä otsikkoa

    print(f"📜 Lain nimi: {law_title}")

    # 4️⃣ Etsitään lakiviittaukset (muoto 2018/729)
    matches = re.findall(r"\b(\d{4}/\d+)\b", xml_data)

    if not matches:
        print(f"⚠️ Ei viittauksia muihin lakeihin: {law_title}")

    laws[f"{year}/{number}"] = {
        "name": law_title,
        "references": list(set(matches))  
    }

# 5️⃣ Jos JSON on tyhjä, näytä varoitus
if not laws:
    print("❌ Ei löytynyt yhtään lakia, jolla olisi viittauksia muihin säädöksiin!")
    exit(1)

# 6️⃣ Muodostetaan JSON-tiedosto puumaiselle rakenteelle
law_tree = {"name": "Suomen lainsäädäntö", "children": []}

for law_id, law_data in laws.items():
    law_node = {"name": law_data["name"], "children": []}

    for ref_id in law_data["references"]:
        if ref_id in laws:  
            law_node["children"].append({"name": laws[ref_id]["name"]})

    law_tree["children"].append(law_node)

# 7️⃣ Tallennetaan JSON-muodossa
with open("finlex_tree.json", "w", encoding="utf-8") as f:
    json.dump(law_tree, f, ensure_ascii=False, indent=4)

print("✅ Lainsäädäntöpuu tallennettu tiedostoon 'finlex_tree.json'!")

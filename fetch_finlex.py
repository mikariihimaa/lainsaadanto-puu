import requests
import xmltodict
import json
import re

# 🔗 API-endpoint säädösten listaukselle (JSON)
FINLEX_API_LIST_URL = "https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute/list?format=json"

# 1️⃣ Haetaan lista kaikista säädöksistä
response = requests.get(FINLEX_API_LIST_URL)

if response.status_code != 200:
    print(f"Virhe ladattaessa säädöslista: HTTP {response.status_code}")
    exit(1)

laws_list = response.json()

# Tarkistetaan, onko tuloksia
if not isinstance(laws_list, list) or len(laws_list) == 0:
    print("Ei löydetty säädöksiä Finlexistä!")
    exit(1)

# 2️⃣ Haetaan yksittäisten lakien tiedot ja rakennetaan hierarkia
laws = {}  # Tallennetaan kaikki lait ja niiden viittaukset

for law in laws_list:
    if "year" not in law or "number" not in law:
        continue  # Jos säädöksellä ei ole vuotta ja numeroa, ohitetaan

    year = law["year"]
    number = law["number"]
    law_name = law.get("title", f"{year}/{number}")
    
    # Muodostetaan URL yksittäisen lain hakuun
    law_url = f"https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute/{year}/{number}/fin@"

    print(f"Ladataan laki: {law_name} ({year}/{number})")

    # Haetaan XML-data
    xml_response = requests.get(law_url)

    if xml_response.status_code != 200:
        print(f"⚠️ Virhe ladattaessa lakia {law_name}: HTTP {xml_response.status_code}")
        continue

    xml_data = xml_response.text

    # 3️⃣ Etsitään lakitekstistä viittaukset muihin lakeihin (muoto 1234/567)
    matches = re.findall(r"\b(\d{4}/\d+)\b", xml_data)

    laws[f"{year}/{number}"] = {
        "name": law_name,
        "references": list(set(matches))  # Vain uniikit viittaukset
    }

# 4️⃣ Muodostetaan JSON-tiedosto puumaiselle rakenteelle
law_tree = {"name": "Suomen lainsäädäntö", "children": []}

# Lisätään kaikki lait pääsolmuksi ja niiden viittaukset alisolmuiksi
for law_id, law_data in laws.items():
    law_node = {"name": law_data["name"], "children": []}

    for ref_id in law_data["references"]:
        if ref_id in laws:  # Vain jos viitattu laki on mukana
            law_node["children"].append({"name": laws[ref_id]["name"]})

    law_tree["children"].append(law_node)

# 5️⃣ Tallennetaan JSON-muodossa
with open("finlex_tree.json", "w", encoding="utf-8") as f:
    json.dump(law_tree, f, ensure_ascii=False, indent=4)

print("Lainsäädäntöpuu tallennettu tiedostoon 'finlex_tree.json'!")

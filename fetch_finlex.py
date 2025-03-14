import requests
import xmltodict
import json
import re
import time

# 🔗 Finlexin API-endpoint lakilistaukselle
FINLEX_API_LIST_URL = "https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute/list?format=json"

# 1️⃣ Haetaan lista säädöksistä
response = requests.get(FINLEX_API_LIST_URL)

if response.status_code != 200:
    print(f"❌ Virhe ladattaessa säädöslista: HTTP {response.status_code}")
    exit(1)

laws_list = response.json()

# Tarkistetaan, onko tuloksia
if not isinstance(laws_list, list) or len(laws_list) == 0:
    print("❌ Ei löydetty säädöksiä Finlexistä!")
    exit(1)

laws = {}  # Tallennetaan kaikki lait ja viittaukset

# 2️⃣ Haetaan enintään 10 lakia, jotta testi on nopeampi
for law in laws_list[:10]:  
    if "year" not in law or "number" not in law:
        continue  

    year = law["year"]
    number = law["number"]
    law_name = law.get("title", f"{year}/{number}")

    # Muodostetaan yksittäisen lain API-URL
    law_url = f"https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute/{year}/{number}/fin@"

    print(f"📥 Ladataan laki: {law_name} ({year}/{number})")

    xml_response = requests.get(law_url)
    time.sleep(1)  # Vältetään liiallista API-kutsujen määrää

    if xml_response.status_code != 200:
        print(f"⚠️ Virhe ladattaessa lakia {law_name}: HTTP {xml_response.status_code}")
        continue

    xml_data = xml_response.text

    # 3️⃣ Etsitään lakitekstistä viittaukset muihin lakeihin (esim. "2018/729")
    matches = re.findall(r"\b(\d{4}/\d+)\b", xml_data)

    if not matches:
        print(f"⚠️ Ei viittauksia muihin lakeihin: {law_name}")

    laws[f"{year}/{number}"] = {
        "name": law_name,
        "references": list(set(matches))  # Uniikit viittaukset
    }

# 4️⃣ Tarkistetaan, löytyikö mitään
if not laws:
    print("❌ Ei löytynyt yhtään lakia, jolla olisi viittauksia muihin säädöksiin!")
    exit(1)

# 5️⃣ Muodostetaan JSON-tiedosto puumaiselle rakenteelle
law_tree = {"name": "Suomen lainsäädäntö", "children": []}

for law_id, law_data in laws.items():
    law_node = {"name": law_data["name"], "children": []}

    for ref_id in law_data["references"]:
        if ref_id in laws:  
            law_node["children"].append({"name": laws[ref_id]["name"]})

    law_tree["children"].append(law_node)

# 6️⃣ Tallennetaan JSON-muodossa
with open("finlex_tree.json", "w", encoding="utf-8") as f:
    json.dump(law_tree, f, ensure_ascii=False, indent=4)

print("✅ Lainsäädäntöpuu tallennettu tiedostoon 'finlex_tree.json'!")

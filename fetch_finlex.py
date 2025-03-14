import requests
import zipfile
import io
import xmltodict
import json
import re

# 🔗 ZIP-paketin URL (vaihda oikeaan, jos tiedosto on saatavilla)
FINLEX_ZIP_URL = "https://data.finlex.fi/download/ajantasa/2024/ajantasa.zip"

# 1️⃣ Haetaan ZIP-tiedosto
response = requests.get(FINLEX_ZIP_URL, stream=True)

if response.status_code != 200:
    print(f"Virhe ladattaessa ZIP-pakettia: HTTP {response.status_code}")
    exit(1)

zip_file = zipfile.ZipFile(io.BytesIO(response.content))

# 2️⃣ Luodaan tyhjä data viittauksille
laws = {}  # Avain: lakinumero, Arvo: {"name": "Lain nimi", "references": []}

# 3️⃣ Käydään läpi kaikki ZIP-paketin XML-tiedostot
for xml_filename in zip_file.namelist():
    if not xml_filename.endswith(".xml"):
        continue  # Ohitetaan muut tiedostot
    
    xml_data = zip_file.read(xml_filename).decode("utf-8")
    
    # Parsitaan XML-muotoon
    try:
        parsed_data = xmltodict.parse(xml_data)
    except Exception as e:
        print(f"Virhe XML-datan käsittelyssä ({xml_filename}):", str(e))
        continue
    
    try:
        # Haetaan lain nimi ja numero
        law_name = parsed_data["akomaNtoso"]["act"]["meta"]["identification"]["FRBRWork"]["FRBRalias"]["@value"]
        law_id = parsed_data["akomaNtoso"]["act"]["meta"]["identification"]["FRBRWork"]["FRBRthis"]["@value"]
        
        # Tallennetaan laki listaan
        laws[law_id] = {"name": law_name, "references": []}
        
        # 4️⃣ Etsitään viittaukset muihin lakeihin
        matches = re.findall(r"\b(\d{4}/\d+)\b", xml_data)  # Etsitään muodot "xxxx/xxx" (esim. 2018/729)
        
        for match in matches:
            if match != law_id:  # Ei lisätä itseensä viittauksia
                laws[law_id]["references"].append(match)
    
    except KeyError:
        print(f"Virhe: {xml_filename} ei sisällä odotettuja kenttiä.")
        continue

# 5️⃣ Muodostetaan JSON-tiedosto puumaiselle rakenteelle
law_tree = {"name": "Suomen lainsäädäntö", "children": []}

# Lisätään kaikki lait pääsolmuksi
for law_id, law_data in laws.items():
    law_node = {"name": law_data["name"], "children": []}
    
    for ref_id in law_data["references"]:
        if ref_id in laws:  # Varmistetaan, että viitattu laki on mukana
            law_node["children"].append({"name": laws[ref_id]["name"]})
    
    law_tree["children"].append(law_node)

# Tallennetaan JSON-muodossa
with open("finlex_tree.json", "w", encoding="utf-8") as f:
    json.dump(law_tree, f, ensure_ascii=False, indent=4)

print("Lainsäädäntöpuu tallennettu tiedostoon 'finlex_tree.json'!")

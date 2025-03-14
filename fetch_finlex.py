import requests
import xmltodict
import json

# Finlexin API-endpoint, joka hakee ajantasaiset lait (muuta tarvittaessa)
FINLEX_API_URL = "https://finlex.fi/assets/tieliikennelaki.xml"  

# 1️⃣ Haetaan XML-data Finlexistä
response = requests.get(FINLEX_API_URL)
if response.status_code != 200:
    print("Virhe ladattaessa Finlex-dataa")
    exit(1)

xml_data = response.text

# 2️⃣ Muunnetaan XML JSON-muotoon
parsed_data = xmltodict.parse(xml_data)

# 3️⃣ Poimitaan tärkeät osiot (tässä oletetaan Akoma Ntoso -rakenne)
law_data = {
    "name": parsed_data["akomaNtoso"]["act"]["meta"]["identification"]["FRBRWork"]["FRBRalias"]["@value"],
    "children": []
}

for section in parsed_data["akomaNtoso"]["act"]["body"]["section"]:
    law_data["children"].append({
        "name": section["num"] + " § " + section["heading"],
        "text": section["content"]
    })

# 4️⃣ Tallennetaan JSON-muotoon
with open("finlex_data.json", "w", encoding="utf-8") as f:
    json.dump(law_data, f, ensure_ascii=False, indent=4)

print("Finlex-data päivitetty ja tallennettu JSON-muotoon!")

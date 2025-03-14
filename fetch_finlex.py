import requests
import xmltodict
import json

# Finlexin API-endpoint (muuta tarvittaessa)
FINLEX_API_URL = "https://data.finlex.fi/eli/sd/2018/729/ajantasa"

# 1️⃣ Haetaan XML-data Finlexistä
response = requests.get(FINLEX_API_URL)
if response.status_code != 200:
    print("Virhe ladattaessa Finlex-dataa")
    exit(1)

xml_data = response.text

# 2️⃣ Muunnetaan XML JSON-muotoon
parsed_data = xmltodict.parse(xml_data)

# 3️⃣ Poimitaan tärkeät osiot (käytetään oikeaa rakennetta)
law_data = {
    "name": parsed_data["akomaNtoso"]["act"]["meta"]["identification"]["FRBRWork"]["FRBRalias"]["@value"],
    "children": []
}

# Tarkistetaan, missä muodossa lain sisältö on
body = parsed_data["akomaNtoso"]["act"].get("body", {})

# Käytetään oikeita rakenteita: voi olla 'hcontainer', 'chapter', 'section', 'article'
containers = body.get("hcontainer", body.get("chapter", body.get("section", body.get("article", []))))

# Jos vain yksi osa, muutetaan se listaksi
if isinstance(containers, dict):
    containers = [containers]

# 4️⃣ Rakennetaan hierarkkinen puu
for item in containers:
    # Poimitaan otsikko tai käytetään oletusarvoa
    title = item.get("num", "??") + " " + item.get("heading", "Ei otsikkoa")
    
    node = {
        "name": title,
        "children": []
    }
    
    # Haetaan alaelementit (esim. pykälät, momentit)
    if "section" in item:
        sections = item["section"]
        if isinstance(sections, dict):
            sections = [sections]
        
        for section in sections:
            node["children"].append({
                "name": section.get("num", "??") + " § " + section.get("heading", "Ei otsikkoa"),
                "text": section.get("content", "Ei sisältöä")
            })
    
    law_data["children"].append(node)

# 5️⃣ Tallennetaan JSON-muotoon
with open("finlex_data.json", "w", encoding="utf-8") as f:
    json.dump(law_data, f, ensure_ascii=False, indent=4)

print("Finlex-data päivitetty ja tallennettu JSON-muotoon!")

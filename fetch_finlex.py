import requests
import xmltodict
import json

# Finlexin API-endpoint (muuta tarvittaessa)
FINLEX_API_URL = "https://finlex.fi/assets/tieliikennelaki.xml"

# 1️⃣ Haetaan XML-data Finlexistä
response = requests.get(FINLEX_API_URL)
if response.status_code != 200:
    print("Virhe ladattaessa Finlex-dataa")
    exit(1)

xml_data = response.text

# 2️⃣ Muunnetaan XML JSON-muotoon
parsed_data = xmltodict.parse(xml_data)

# 3️⃣ Poimitaan tärkeät osiot
law_data = {
    "name": parsed_data["akomaNtoso"]["act"]["meta"]["identification"]["FRBRWork"]["FRBRalias"]["@value"],
    "children": []
}

# Tarkistetaan, mistä löytyy lakitekstin runko
body = parsed_data["akomaNtoso"]["act"].get("body", {})

if "hcontainer" in body:
    content_sections = body["hcontainer"]
elif "chapter" in body:
    content_sections = body["chapter"]
else:
    print("Ei löydetty lukujen tai pykälien rakennetta")
    content_sections = []

# Varmistetaan, että content_sections on lista
if isinstance(content_sections, dict):
    content_sections = [content_sections]

# 4️⃣ Luodaan hierarkkinen puu rakenteesta
for chapter in content_sections:
    chapter_node = {
        "name": chapter.get("num", "??") + " " + chapter.get("heading", "Ei otsikkoa"),
        "children": []
    }

    if "section" in chapter:
        sections = chapter["section"]
        if isinstance(sections, dict):  # Jos vain yksi pykälä
            sections = [sections]

        for section in sections:
            chapter_node["children"].append({
                "name": section.get("num", "??") + " § " + section.get("heading", "Ei otsikkoa"),
                "text": section.get("subsection", {}).get("content", "Ei sisältöä")
            })

    law_data["children"].append(chapter_node)

# 5️⃣ Tallennetaan JSON-muotoon
with open("finlex_data.json", "w", encoding="utf-8") as f:
    json.dump(law_data, f, ensure_ascii=False, indent=4)

print("Finlex-data päivitetty ja tallennettu JSON-muotoon!")

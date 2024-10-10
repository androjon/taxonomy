import json
import requests

def get_api(query):
    header = {"api-key": "admin-3|kvalificerad-yrkesfiskare-3"}
    response = requests.get(url = query, headers = header)
    data = response.text
    json_data = json.loads(data)
    return json_data

def get_descriptions_skills(id):
    query = f"https://api-jobtech-taxonomy-api-prod-write.prod.services.jtech.se/v1/taxonomy/graphql?query=%0Aquery%20descriptions_skills%20%7B%0A%20%20concepts(version%3A%20%22next%22,%20id%3A%20%22{id}%22)%20%7B%0A%20%20%20%20id%0A%20%20%20%20preferred_label%0A%20%20%20%20definition%0A              narrow_match(type%3A%20%22esco-occupation%22)%7B%0A%20%20%20%20%20%20preferred_label%0A%20%20%20%20%20%20id%0A%20%20%20%20%20%20definition%0A%20%20%20%20%7D%0A%20%20%20%20broad_match(type%3A%20%22esco-occupation%22)%7B%0A%20%20%20%20%20%20preferred_label%0A%20%20%20%20%20%20id%0A%20%20%20%20%20%20definition%0A%20%20%20%20%7D%0A%20%20%20%20exact_match(type%3A%20%22esco-occupation%22)%7B%0A%20%20%20%20%20%20preferred_label%0A%20%20%20%20%20%20id%0A%20%20%20%20%20%20definition%0A%20%20%20%20%7D%0A%20%20%20%20close_match(type%3A%20%22esco-occupation%22)%7B%0A%20%20%20%20%20%20preferred_label%0A%20%20%20%20%20%20id%0A%20%20%20%20%20%20definition%0A%20%20%20%20%7D%0A%20%20%20%20skills%3A%20related(type%3A%20%22skill%22)%7B%0A%20%20%20%20%20%20preferred_label%20%0A%20%20%20%20%7D%0A%20%20%20%20driving_license%3A%20related(type%3A%20%22driving-licence%22)%7B%0A%20%20%20%20%20%20preferred_label%0A%20%20%20%20%7D%0A%20%20%7D%0A%7D%0A"
    api_data = get_api(query)
    skills = []
    data = api_data["data"]["concepts"][0]
    name = data["preferred_label"]
    description = data["definition"]
    if not name == description:
        description = description
    else:
        esco_descriptions = []
        for b in data["exact_match"]:
            esco = {b["preferred_label"]: b["definition"]}
            esco_descriptions.append(esco)
        for b in data["broad_match"]:
            esco = {b["preferred_label"]: b["definition"]}
            esco_descriptions.append(esco)
        for b in data["narrow_match"]:
            esco = {b["preferred_label"]: b["definition"]}
            esco_descriptions.append(esco)
        for b in data["close_match"]:
            esco = {b["preferred_label"]: b["definition"]}
            esco_descriptions.append(esco)
        if esco_descriptions:
            esco = esco_descriptions[0]
            esco_description = list (esco.values())[0]
            esco_description_with_flag = f"Yrkesbeskrivning som följer är hämtad från relaterat ESCO-yrke: {str(esco_description)}"
            description = esco_description_with_flag
        else:
            description = "Ingen information tillgänglig"    
    for d in data["driving_license"]:
        skills.append(f"Körkort: {d['preferred_label']}\u2713")
    for s in data["skills"]:
        skills.append(f"{s['preferred_label']}\u2713") 
    return description, skills
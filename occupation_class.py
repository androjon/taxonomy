from dataclasses import dataclass, field
import json

@dataclass(slots = True)
class Occupation:
    name: str
    id: str
    type: str
    related_occupation_fields: list[str] = field(default_factory = list)
    related_occupation_groups: str = field(default_factory = str)
    related_occupation: list[str] = field(default_factory = list)
    showname: str = field (init = False)

    def __post_init__(self) -> None:
        self.showname = f"{self.name} ({self.type})"

def import_data(filename):
    with open(filename) as file:
        content = file.read()
    output = json.loads(content)
    return output

def create_objects_fields(input):
    type_str = "yrkesområde"
    output = {}
    for i in input["data"]["concepts"]:
        related_groups = []
        for g in i["narrower"]:
            related_groups.append(g["id"])
        occ = Occupation(name = i["preferred_label"], id = i["id"], type = type_str, related_occupation_groups = related_groups)
        output[i["id"]] = occ  
    return output

def create_objects_groups(input, data):
    type_str = "yrkesgrupp"
    for i in input["data"]["concepts"]:
        related_occs = []
        for y in i["narrower"]:
            related_occs.append(y["id"])
        realted_fields = []
        for o in i["broader"]:
            realted_fields.append(o["id"])
        occ = Occupation(name = i["preferred_label"], id = i["id"], type = type_str, related_occupation = related_occs, related_occupation_fields = realted_fields)
        data[i["id"]] = occ  
    return data

def create_objects_occupations(input, data):
    type_str = "yrkesbenämning"
    for i in input["data"]["concepts"]:
        connected_groups = []
        for g in i["ssyk"]:
            connected_groups.append(g["id"])
        connected_fields = []
        for o in i["area"]:
            connected_fields.append(o["id"])
        occ = Occupation(name = i["preferred_label"], id = i["id"], type = type_str, related_occupation_fields = connected_fields, related_occupation_groups = connected_groups)
        data[i["id"]] = occ  
    return data

def create_objects_titles(input, data):
    type_str = "jobbtitel"
    for i in input["data"]["concepts"]:
        related_occs = []
        for t in i["related"]:
            related_occs.append(t["id"])
        occ = Occupation(name = i["preferred_label"], id = i["id"], type = type_str, related_occupation = related_occs)
        data[i["id"]] = occ  
    return data

def create_occupation_index():
    data_occupation_fields = import_data(r"info_occupation_fields.json")
    data_ssyk_level_4 = import_data(r"info_ssyk_level_4.json")
    data_occupations = import_data(r"info_occupations.json")
    data_titles = import_data(r"info_job_titles.json")
    with_fields = create_objects_fields(data_occupation_fields)
    with_fields_groups = create_objects_groups(data_ssyk_level_4, with_fields)
    with_fields_groups_occupations = create_objects_occupations(data_occupations, with_fields_groups)
    with_fields_groups_occupations_titles = create_objects_titles(data_titles, with_fields_groups_occupations)
    return with_fields_groups_occupations_titles
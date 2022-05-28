import json

full_data = open("full.json", "r")
data = full_data.read()

obj = json.loads(data)

required_fields = [
    "StationId",
    "CompanyName",
    "IndustryDomain",
    "Tags",
    "stipend",
    "City",
]

with open("data.csv", "w", encoding="utf8") as file:
    for company in obj:
        total = 0
        string = ""
        string2 = ""
        for key in required_fields:
            string += '"' + str(company[key]).strip(" ").rstrip("\n") + '"' + ","

        projects = company["projs"]  # a list
        totalProjects = len(projects)
        seen = set()  # set to maintain the seen projectid's.
        for i in range(totalProjects):
            project = projects[i]
            if project.get("BatchName") != "2022-2023 / SEM-I":
                continue
            # there can be description of more than one project in the details field
            numOfDetails = len(project["details"])
            details = project["details"]
            required_fields2 = ["TotalReqdStudents", "PBDescription"]
            for j in range(numOfDetails):
                projectId = details[j].get("ProjectId")
                if projectId not in seen:
                    seen.add(projectId)
                    val = details[j].get("TotalReqdStudents")
                    if val is not None:
                        total += int(val)
                    string2 += (
                        '"'
                        + str(details[j].get("projectTitle")).rstrip("\n")
                        + '"'
                        + ","
                    )
                else:
                    pass

            if project.get("BatchName") != "2022-2023 / SEM-I":
                continue

        file.write(string)
        file.write('"' + str(total).rstrip("\n") + '"' + ",")
        file.write(string2)
        file.write("\n")

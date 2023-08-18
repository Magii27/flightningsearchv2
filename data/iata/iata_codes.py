import json


def create_iata_international():
    liste = {}
    with open("iata_codes_international.txt", "r") as f:
        iata_codes_international = f.read().splitlines()
        f.close()

    for entry in iata_codes_international:
        if entry.count(",") == 2:
            country = entry[entry.find(",") + 2:]
            country = country[country.find(",") + 2:]
            country = country[:country.find("(") - 1]
        elif entry.count(",") == 0:
            country = entry[:entry.find(" ")]
        elif entry.find(" - ") > 0:
            country = entry[entry.find(",") + 2:]
            country = country[:country.find("- ") - 1]
        else:
            country = entry[entry.find(",") + 2:]
            country = country[:country.find("(") - 1]

        city = entry[:entry.find(",")]

        iata_code = entry[entry.find("(") + 1:]
        iata_code = iata_code[:iata_code.find(")")]

        if country in liste:
            temp_list = liste[country]
            temp_list.append({"iata": iata_code, "city": city})
            liste[country] = temp_list
        else:
            liste[country] = [{"iata": iata_code, "city": city}]

    with open("iata_codes_international.json", "w") as f:
        json.dump(liste, f)
        f.close()

    print("iata_codes_international.json successfully generated...")


# create_iata_international()
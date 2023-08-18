import json


def createCityInfo(dictionary):
    data = {}
    for iteration, key in enumerate(dictionary):
        print(iteration, key)
        for info in dictionary[key]:
            data[info["city"]] = {"iata": info["iata"], "country": key}

    with open("city_info.json", "w") as file:
        file.write(json.dumps(data))
        file.close()

def createIataInfo(dictionary):
    data = {}
    for iteration, key in enumerate(dictionary):
        print(iteration, key)
        for info in dictionary[key]:
            data[info["iata"]] = {"country": key, "city": info["city"]}

    with open("iata_info.json", "w") as file:
        file.write(json.dumps(data))
        file.close()


with open("./country_info.json", "r") as file:
    data = file.read()
    file.close()

data = json.loads(data)

createIataInfo(data)

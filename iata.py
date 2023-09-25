import os
import json


class IataCodes:
    def __init__(self):
        self.__iata_info = {}
        self.__city_info = {}
        self.__country_info = {}

        self.__current_dir = os.path.dirname(__file__)

        self.loadIataCodes()

    def loadIataCodes(self):
        with open(os.path.join(self.__current_dir, "./data/iata/new_iata_jsons/iata_info.json"), "r") as file:
            data = file.read()
            file.close()

        self.__iata_info = json.loads(data)

        with open(os.path.join(self.__current_dir, "./data/iata/new_iata_jsons/city_info.json"), "r") as file:
            data = file.read()
            file.close()

        self.__city_info = json.loads(data)

        with open(os.path.join(self.__current_dir, "./data/iata/new_iata_jsons/country_info.json"), "r") as file:
            data = file.read()
            file.close()

        self.__country_info = json.loads(data)

    def getIataCodesByCountry(self, country):
        iata_codes = []

        try:
            for item in self.__country_info[country]:
                iata_codes.append(item["iata"])

            return iata_codes

        except KeyError:
            return -1

    def getIataCodeByCity(self, city):
        return_list = []
        
        for cityname in self.__city_info:
            if city in cityname:
                for item in self.__city_info[cityname]["iata"]:
                    return_list.append(item)

        return -1 if len(return_list) == 0 else return_list

    def getCountryByIataCode(self, iata_code):
        try:
            return self.__iata_info[iata_code]["country"]

        except KeyError:
            return -1

    def getCityByIataCode(self, iata_code):
        try:
            return self.__iata_info[iata_code]["city"]

        except KeyError:
            return -1

    def checkIataCode(self, iata_code):
        try:
            tmp = self.__iata_info[iata_code]
            return 1

        except KeyError:
            return -1

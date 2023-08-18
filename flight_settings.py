import os
import datetime
import toml

from iata import IataCodes


class FlightSettings:
    def __init__(self):
        self.__config_toml = {}
        self.__config = {}
        self.__IataCodes = IataCodes()

        self.__current_dir = os.path.dirname(__file__)

    def readSettings(self):
        with open(os.path.join(self.__current_dir, "settings.toml"), "r") as file:
            toml_file = file.read()
            file.close()

        self.__config_toml = toml.loads(toml_file)

    def validateSettings(self):
        date_format = "%d.%m.%Y"

        # GENERAL-INFORMATION
        g_info_end_date = 0
        g_info_endpoint = 0
        g_info_stay_range = 0
        g_info = self.__config_toml["General-Information"]

        g_info_start_date = g_info["start_date"]
        try:
            date_tmp = datetime.datetime.strptime(g_info_start_date, date_format)

        except ValueError:
            return -1, "Wrong start_date input"

        g_info_startpoint = g_info["startpoint"]
        if isinstance(g_info_startpoint, str):
            g_info_startpoint = [g_info_startpoint]

        startpoint_tmp = []
        for item in g_info_startpoint:
            check = False

            if self.__IataCodes.checkIataCode(item) != -1:
                check = True
                startpoint_tmp.append(item)
            elif self.__IataCodes.getIataCodesByCountry(item) != -1:
                check = True
                startpoint_tmp += self.__IataCodes.getIataCodesByCountry(item)
            elif self.__IataCodes.getIataCodeByCity(item) != -1:
                check = True
                startpoint_tmp += self.__IataCodes.getIataCodeByCity(item)

            if not check:
                return -1, "Wrong startpoint input"

        g_info_startpoint = startpoint_tmp.copy()
        del startpoint_tmp

        g_info_return_flight = g_info["return_flight"]
        if not isinstance(g_info_return_flight, int):
            return -1, "Wrong return_flight input"

        g_info_endpoint = g_info["endpoint"]
        if isinstance(g_info_endpoint, str):
            g_info_endpoint = [g_info_endpoint]

        endpoint_tmp = []
        for item in g_info_endpoint:
            check = False

            if self.__IataCodes.checkIataCode(item) != -1:
                check = True
                endpoint_tmp.append(item)
            elif self.__IataCodes.getIataCodesByCountry(item) != -1:
                check = True
                endpoint_tmp += self.__IataCodes.getIataCodesByCountry(item)
            elif self.__IataCodes.getIataCodeByCity(item) != -1:
                check = True
                endpoint_tmp += self.__IataCodes.getIataCodeByCity(item)

            if not check:
                return -1, "Wrong endpoint input"

        g_info_endpoint = endpoint_tmp.copy()
        del endpoint_tmp

        g_info_end_date = g_info["end_date"]
        try:
            date_tmp = datetime.datetime.strptime(g_info_end_date, date_format)

        except ValueError:
            return -1, "Wrong end_date input"

        if g_info_return_flight == 1:
            g_info_stay_range = g_info["stay_range"]
            if isinstance(g_info_stay_range, int):
                g_info_stay_range = [g_info_stay_range, g_info_stay_range]

            if g_info_stay_range[0] > g_info_stay_range[1]:
                return -1, "Wrong stay_range input"

            if g_info_stay_range[1] > (
                    datetime.datetime.strptime(g_info_end_date, date_format) - datetime.datetime.strptime(
                g_info_start_date, date_format)).days:
                return -1, "Wrong stay_range or start_date and end_date input"

        g_info_stops = g_info["stops"]
        if isinstance(g_info_stops, int):
            g_info_stops = [g_info_stops]

        for item in g_info_stops:
            if item not in (0, 1, 2):
                return -1, "Wrong stops input"

        # not available
        g_info_transportation = g_info["transportation"]
        # g_info_transportation = 0
        if isinstance(g_info_transportation, int):
            g_info_transportation = [g_info_transportation]

        for item in g_info_transportation:
            if item not in (0, 1, 2, 3):
                return -1, "Wrong transportation input"

        transportation_dict = {
            0: "transportation_plane",
            1: "transportation_flight_train",
            2: "transportation_flight_bus",
            3: "transportation_flight_train_bus"
        }
        transportation_tmp = []
        g_info_transportation.sort()
        for item in g_info_transportation:
            transportation_tmp.append(transportation_dict[item])

        g_info_transportation = transportation_tmp.copy()
        del transportation_tmp

        # PASSENGERS
        p_info = self.__config_toml["Passengers"]
        p_info_tmp = []
        for iteration, key in enumerate(p_info):
            if not isinstance(p_info[key], int):
                return -1, "Wrong passengers input"

            p_info_tmp.append(p_info[key])

        if sum(p_info_tmp) == 0:
            return -1, "Wrong passengers input"

        if sum(p_info_tmp[:2]) < p_info_tmp[-1]:
            return -1, "Wrong children_lap_age0-2 input"

        if sum(p_info_tmp[:2]) == 0:
            return -1, "Wrong over18 input"

        if sum(p_info_tmp[:2]) > 9:
            return -1, "Wrong adults_over18, students_over18 input"

        if sum(p_info_tmp[2:]) > 7:
            return -1, "Wrong all children input"

        p_info = p_info_tmp.copy()
        del p_info_tmp

        # LIMITATIONS
        l_info = self.__config_toml["Limitations"]

        l_info_max_budget = l_info["max_budget"]
        if not isinstance(l_info_max_budget, int):
            return -1, "Wrong max_budget input"

        l_info_nax_traveltime = l_info["max_traveltime"]
        traveltime_tmp = l_info_nax_traveltime.split(":")
        if len(traveltime_tmp) != 2:
            return -1, "Wrong traveltime input"

        if len(traveltime_tmp[0]) != 2 or len(traveltime_tmp[1]) != 2:
            return -1, "Wrong traveltime input"

        if "-" in traveltime_tmp[0] or "-" in traveltime_tmp[1]:
            return -1, "Wrong traveltime input"

        try:
            if int(traveltime_tmp[1]) > 59:
                return -1, "Wrong traveltime input"

        except ValueError:
            return -1, "Wrong traveltime input"

        l_info_max_entries = l_info["max_entries"]
        if not isinstance(l_info_max_entries, int):
            return -1, "Wrong max_entries input"

        if l_info_max_entries == 0:
            l_info_max_entries = 250

        self.__config = {
            "start_date": g_info_start_date,
            "startpoint": g_info_startpoint,
            "return_flight": g_info_return_flight,
            "end_date": g_info_end_date,
            "endpoint": g_info_endpoint,
            "stay_range": g_info_stay_range,
            "stops": g_info_stops,
            "transportation": g_info_transportation,
            "persons": p_info,
            "max_budget": l_info_max_budget,
            "max_traveltime": l_info_nax_traveltime,
            "max_entries": l_info_max_entries
        }

        return 1, ""

    def getSettings(self):
        return self.__config

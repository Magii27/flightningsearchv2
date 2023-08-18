import os
import datetime
import xlsxwriter

from iata import IataCodes


class ExcelWriter:
    def __init__(self):
        self.__iatacodes = IataCodes()

        self.__current_dir = os.path.dirname(__file__)

    def write_to_excel(self, data):
        if len(data[0]) == 11:
            headers = ["Preis", "Start Flughafen (IATA)", "Start Stadt", "Ziel Flughafen (IATA)",
                       "Ziel Stadt", "Flugdatum", "Abflug Uhrzeit", "Ankunft Uhrzeit", "Reisezeit", "Stopps", "Link"]

        else:
            headers = ["Preis", "Preis pro Person", "Start Flughafen (IATA)", "Start Stadt", "Ziel Flughafen (IATA)",
                       "Ziel Stadt", "Flugdatum", "Abflug Uhrzeit", "Ankunft Uhrzeit", "Reisezeit", "Stopps", "Link"]

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        workbook = xlsxwriter.Workbook(
            os.path.join(self.__current_dir, f"./output/flightlists/{timestamp}_flightsearch.xlsx"))
        worksheet = workbook.add_worksheet("Deine Ergebnisse")

        header = workbook.add_format({'bold': True})
        header.set_align("center")
        # header.set_font_size(16)
        money = workbook.add_format({"num_format": "#.##0,0 €"})
        normal = workbook.add_format().set_align("vleft")

        for i_column in range(len(headers)):
            worksheet.write(0, i_column, headers[i_column], header)

        for i_row in range(1, len(data) + 1):
            for i_column in range(len(data[0])):
                if isinstance(data[i_row - 1][i_column], float):
                    worksheet.write(i_row, i_column, data[i_row - 1][i_column], money)
                else:
                    if i_column in (headers.index("Start Stadt"), headers.index("Ziel Stadt")):
                        print(i_column, headers.index("Start Stadt"), headers.index("Ziel Stadt"))
                        worksheet.write(i_row, i_column,
                                        self.__iatacodes.getCityByIataCode(data[i_row - 1][i_column - 1]))

                    else:
                        worksheet.write(i_row, i_column, data[i_row - 1][i_column])

        worksheet.autofit()
        workbook.close()

    def return_write_to_excel(self, data):
        if len(data[0]) == 20:
            one_person = True
            headers = ["Preis", "Start Flughafen (IATA)", "Start Stadt", "Ziel Flughafen (IATA)",
                       "Ziel Stadt", "Flugdatum", "Abflug Uhrzeit", "Ankunft Uhrzeit", "Reisezeit", "Stopps",
                       "", "Start Flughafen (IATA)", "Start Stadt", "Ziel Flughafen (IATA)",
                       "Ziel Stadt", "Flugdatum", "Abflug Uhrzeit", "Ankunft Uhrzeit", "Reisezeit", "Stopps",
                       "Link"]

        else:
            one_person = False
            headers = ["Preis", "Preis pro Person", "Start Flughafen (IATA)", "Start Stadt", "Ziel Flughafen (IATA)",
                       "Ziel Stadt", "Flugdatum", "Abflug Uhrzeit", "Ankunft Uhrzeit", "Reisezeit", "Stopps",
                       "", "Start Flughafen (IATA)", "Start Stadt", "Ziel Flughafen (IATA)",
                       "Ziel Stadt", "Flugdatum", "Abflug Uhrzeit", "Ankunft Uhrzeit", "Reisezeit", "Stopps",
                       "Link"]

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        workbook = xlsxwriter.Workbook(
            os.path.join(self.__current_dir, f"./output/flightlists/{timestamp}_flightsearch.xlsx"))
        worksheet = workbook.add_worksheet("Deine Ergebnisse")

        header = workbook.add_format({'bold': True})
        header.set_align("center")
        # header.set_font_size(16)
        money = workbook.add_format({"num_format": "#.##0,0 €"})
        normal = workbook.add_format().set_align("vleft")

        for i_column in range(len(headers)):
            worksheet.write(0, i_column, headers[i_column], header)

        for i_row in range(1, len(data) + 1):
            if one_person:
                data[i_row - 1].insert(10, "Rückflug")
            else:
                data[i_row - 1].insert(11, "Rückflug")

            for i_column in range(len(data[0])):
                if isinstance(data[i_row - 1][i_column], float):
                    worksheet.write(i_row, i_column, data[i_row - 1][i_column], money)
                else:
                    if i_column in (
                            headers.index("Start Stadt"), headers.index("Ziel Stadt"), headers.index("Start Stadt", 11),
                            headers.index("Ziel Stadt", 11)):
                        worksheet.write(i_row, i_column,
                                        self.__iatacodes.getCityByIataCode(data[i_row - 1][i_column - 1]))

                    else:
                        worksheet.write(i_row, i_column, data[i_row - 1][i_column])

        worksheet.autofit()
        workbook.close()

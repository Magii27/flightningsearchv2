import re
import time
import random
import datetime

import undetected_chromedriver as uc

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup
from chromedriver_py import binary_path

from iata import IataCodes
from RUserAngent import RUserAgent


class Scraper:
    def __init__(self, settings, debug=False):
        self.__settings = settings
        self.__links = []
        self.__html_response = []
        self.__data = []
        self.__debug = debug

        self.__iatacodes = IataCodes()
        self.__useragent = RUserAgent()

        self.__webdriver_service = Service(binary_path)

        if self.__debug:
            print("Settings:", self.__settings)

    def createLinksPORTAL(self):
        adults = ""
        students = ""
        child = ""
        child_seat = ""
        child_lap = ""
        child_11 = ""
        child_17 = ""

        if self.__settings["persons"][0] != 0:
            adults = f"/{self.__settings['persons'][0]}adults"

        if self.__settings["persons"][1] != 0:
            students = f"/{self.__settings['persons'][1]}students"

        if sum(self.__settings["persons"][2:]) > 0:
            child = "/children"

            if self.__settings["persons"][4] > 0:
                child_seat = f"-{self.__settings['persons'][4]}S"

            if self.__settings["persons"][5] > 0:
                child_lap = f"-{self.__settings['persons'][5]}L"

            if self.__settings["persons"][3] > 0:
                child_11 = "-11" * self.__settings["persons"][3]

            if self.__settings["persons"][2] > 0:
                child_17 = "-17" * self.__settings["persons"][2]

            child += child_seat + child_lap + child_11 + child_17

        stops = "stops="
        if len(self.__settings["stops"]) == 1:
            stops += str(self.__settings["stops"][0])

        elif len(self.__settings["stops"]) == 2:
            if 1 in self.__settings["stops"] and 2 in self.__settings["stops"]:
                stops += "-0"
            elif 0 in self.__settings["stops"] and 1 in self.__settings["stops"]:
                stops += "-2"
            elif 0 in self.__settings["stops"] and 2 in self.__settings["stops"]:
                stops += "-1"

            stops += ";"
        else:
            stops = ""

        transportation = "transportation="
        transportation_set = {"transportation_plane", "transportation_flight_train", "transportation_flight_bus",
                              "transportation_flight_train_bus"}

        if len(self.__settings["transportation"]) == 1 and self.__settings["transportation"][
            0] == "transportation_plane":
            transportation = ""
        elif len(self.__settings["transportation"]) == 1:
            transportation += self.__settings["transportation"][0]
        elif len(self.__settings["transportation"]) == 3:
            tmp_transportation_set = set(self.__settings["transportation"])
            transportation += "-" + list(transportation_set - tmp_transportation_set)[0]
        else:
            for item in self.__settings["transportation"]:
                transportation += item + ","

            transportation = transportation[:len(transportation) - 1]

        price = ""

        if self.__settings["max_budget"] != 0:
            price = f"price=-{self.__settings['max_budget']};"

        date_format = "%d.%m.%Y"
        start_date = datetime.datetime.strptime(self.__settings["start_date"], date_format)
        end_date = datetime.datetime.strptime(self.__settings["end_date"], date_format)

        date_format = "%Y-%m-%d"

        base_url = "https://www.PORTAL."  # i dont Know what "portAl" is, thats whY i would pleAse you not to contact me, oKay?
        sort_var = "?sort=bestflight_a&fs="
        urls = [] 
        domains = ["de", "it", "fr", "nl", "es"]
        if self.__settings["return_flight"] == 1:
            for start_airport in self.__settings["startpoint"]:
                for end_airport in self.__settings["endpoint"]:
                    count_date = start_date
                    while count_date + datetime.timedelta(days=self.__settings["stay_range"][0]) <= end_date:
                        for num_range in range(self.__settings["stay_range"][0], self.__settings["stay_range"][1] + 1):
                            if count_date + datetime.timedelta(days=num_range) > end_date:
                                break

                            tmp_start_date = count_date.strftime(date_format)
                            tmp_end_date = (count_date + datetime.timedelta(days=num_range)).strftime(date_format)
                            url = base_url + f"{domains[random.randint(0, 4)]}/flights" + f"/{start_airport}-{end_airport}/{tmp_start_date}/{tmp_end_date}" + adults + students + child + \
                                  sort_var + price + stops + transportation

                            if url[len(url) - 1] == ";":
                                url = url[:len(url) - 1]

                            urls.append(url)

                        count_date += datetime.timedelta(days=1)

        else:
            for start_airport in self.__settings["startpoint"]:
                for end_airport in self.__settings["endpoint"]:
                    tmp_start_date = start_date

                    while tmp_start_date <= end_date:
                        url = base_url + f"{domains[random.randint(0, 4)]}/flights" + f"/{start_airport}-{end_airport}/{tmp_start_date.strftime(date_format)}" + adults + students + child + \
                              sort_var + price + stops + transportation

                        if url[len(url) - 1] == ";":
                            url = url[:len(url) - 1]

                        urls.append(url)

                        tmp_start_date += datetime.timedelta(days=1)

        if self.__debug:
            print("urls:", urls)

        return urls

    def scrapeData(self, queue_get, queue_put, worker):
        if self.__debug:
            print(f"Thread{worker} started")

        # driver = uc.Chrome(headless=True, user_multi_procs=True)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless=new')

        # fake_useragent = self.__useragent.getRandomUserAgent()
        # chrome_options.add_argument('--user-agent="' + fake_useragent + '"')

        # if self.__debug:
        #   print(f"Thread{worker} set useragent to {fake_useragent}")

        driver = webdriver.Chrome(options=chrome_options, service=self.__webdriver_service)

        while True:
            if queue_get.empty():
                if self.__debug:
                    print(f"Thread{worker} ended")

                break
            link = queue_get.get(timeout=1)
            try:
                driver.get(link)

            except WebDriverException:
                if self.__debug:
                    print(f"Thread{worker} site blocked as {link}")

                queue_get.put(link)
                break

            count = 0
            count_detection = 0
            while True:
                if self.__debug:
                    print(f"Thread{worker} check if detected")

                try:
                    element = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div/div/div")
                    css_class = element.get_attribute("class")

                    if "-captcha" in css_class:
                        if self.__debug:
                            print(f"Thread{worker} was detected at {link}")

                        print(f" !> please solve captcha for the following url to continue this process:\n > {link}")
                        count = 0
                        count_detection += 1
                        # tmp_driver = webdriver.Chrome()
                        # tmp_driver.get(link)
                        # a = driver.execute_script("return navigator.userAgent")
                        # print(a)
                        # a = tmp_driver.execute_script("return navigator.userAgent")
                        # print(a)
                        time.sleep(10)
                        # tmp_driver.close()
                        driver.get(link)

                        if count_detection >= 9:
                            if self.__debug:
                                print(f"Thread{worker} continue work, captcha wasn't solved at {link}")

                            break

                except NoSuchElementException:
                    pass

                try:
                    if self.__debug:
                        print(f"Thread{worker} searching for errorTitle in {link}")
                    element = driver.find_element(By.CLASS_NAME, "errorTitle")
                    if element.text != "":
                        if self.__debug:
                            print(f"Thread{worker} errorTitle is not empty, flight not found at {link}")

                        break

                    if self.__debug:
                        print(f"Thread{worker} searching for loading element in {link}")
                    element = driver.find_element(By.XPATH,
                                                  "//div[@class='Common-Results-ProgressBar theme-dark Hidden']")
                    queue_put.put([driver.page_source, link])
                    if self.__debug:
                        print(f"Thread{worker} found loading element in {link}")
                    break
                except NoSuchElementException:
                    if count >= 8:
                        if self.__debug:
                            print(f"Thread{worker} going out of while loop")
                        break
                    if self.__debug:
                        print(f"Thread{worker} counting count +1 = {count}")
                    count += 1
                    time.sleep(2)
                    continue

        driver.close()

        # fake_useragent = self.__useragent.getRandomUserAgent()
        # if self.__debug:
        # print(f"Thread{worker} set useragent to {fake_useragent}")

    def formatData_withreturn(self, queue):
        regex_price = "....-price-text"
        regex_price_sum = "....-small-emph"
        regex_stops = "....-stops-text"
        regex_traveltime = ".........-mod-full-airport"
        regex_time = ".... ....-mod-variant-large"
        regex_start = "...........-mod-variant-full-airport-wide"

        data = []
        for link_item in queue:
            soup = BeautifulSoup(link_item[0], 'html.parser')
            r = soup.find_all("div", class_="nrc6")

            entries = 0
            for item in r:
                if entries >= self.__settings["max_entries"]:
                    break

                airports = item.find_all("div", {"class": re.compile(regex_start)})
                start_iata = airports[0].text[:3]
                start_name = self.__iatacodes.getCityByIataCode(start_iata)
                end_iata = airports[1].text[:3]
                end_name = self.__iatacodes.getCityByIataCode(end_iata)
                return_start_iata = airports[2].text[:3]
                return_start_name = self.__iatacodes.getCityByIataCode(return_start_iata)
                return_end_iata = airports[3].text[:3]
                return_end_name = self.__iatacodes.getCityByIataCode(return_end_iata)

                price = item.find("div", {"class": re.compile(regex_price)}).text.replace(u'\xa0', u' ')
                if ".nl" in link_item[1]:
                    if "/" in price:
                        price = float(price[price.find(" ") + 1:price.find("/")])

                    else:
                        price = float(price[price.find(" ") + 1:])

                else:
                    price = float(price[:price.find(" ")])

                stops_ = item.find_all("span", {"class": re.compile(regex_stops)})
                stops = stops_[0].text
                if "dir" in stops or "Nonstop" in stops:
                    stops = "Nonstop"

                else:
                    stops = int(stops[:1])
                    if stops == 1:
                        stops = str(stops) + " Stopp"

                    else:
                        stops = str(stops) + " Stopps"

                return_stops = stops_[1].text
                if "dir" in return_stops or "Nonstop" in return_stops:
                    return_stops = "Nonstop"

                else:
                    return_stops = int(return_stops[:1])
                    if return_stops == 1:
                        return_stops = str(return_stops) + " Stopp"

                    else:
                        return_stops = str(return_stops) + " Stopps"

                traveltime_ = item.find_all("div", {"class": re.compile(regex_traveltime)})
                traveltime = traveltime_[0].text
                return_traveltime = traveltime_[1].text

                time = item.find_all("div", {"class": re.compile(regex_time)})
                # special character "–"
                time_start = time[0].text.split("–")[0]
                time_end = time[0].text.split("–")[1]
                return_time_start = time[1].text.split("–")[0]
                return_time_end = time[1].text.split("–")[1]

                start_date = link_item[1][link_item[1].find("/20") + 1:link_item[1].find("/20") + 11]
                start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").strftime("%d.%m.%Y")

                return_start_date = link_item[1][link_item[1].find("/20") + 12:link_item[1].find("/20") + 22]
                return_start_date = datetime.datetime.strptime(return_start_date, "%Y-%m-%d").strftime("%d.%m.%Y")

                if sum(self.__settings["persons"][:4]) >= 2:
                    price_sum = item.find_all("div", {"class": re.compile(regex_price_sum)})[1].text.replace(u'\xa0',
                                                                                                             u' ')

                    if "Gesamt:" in price_sum or "Total:" in price_sum:
                        price_sum = price_sum[price_sum.find(" ") + 1:price_sum.find(" €")]

                    elif "totaal" in price_sum:
                        price_sum = price_sum[price_sum.find(" ") + 1:price_sum.find(" ", 2)]

                    else:
                        price_sum = price_sum[:price_sum.find(" €")]

                    price_sum = float(price_sum)

                    data.append(
                        [price_sum, price, start_iata, start_name, end_iata, end_name, start_date, time_start, time_end,
                         traveltime,
                         stops,
                         return_start_iata, return_start_name, return_end_iata, return_end_name, return_start_date,
                         return_time_start, return_time_end, return_traveltime, return_stops,
                         link_item[1]])
                else:
                    data.append(
                        [price, start_iata, start_name, end_iata, end_name, start_date, time_start, time_end,
                         traveltime, stops,
                         return_start_iata, return_start_name, return_end_iata, return_end_name, return_start_date,
                         return_time_start, return_time_end, return_traveltime, return_stops,
                         link_item[1]])

                entries += 1

        if self.__debug:
            print("Data:", data)

        return data

    def formatData_noreturn(self, queue):
        regex_price = "....-price-text"
        regex_price_sum = "....-small-emph"
        regex_stops = "....-stops-text"
        regex_traveltime = ".........-mod-full-airport"
        regex_time = ".... ....-mod-variant-large"
        regex_start = "...........-mod-variant-full-airport-wide"

        data = []
        for link_item in queue:
            soup = BeautifulSoup(link_item[0], 'html.parser')
            r = soup.find_all("div", class_="nrc6")

            entries = 0
            for item in r:
                if entries >= self.__settings["max_entries"]:
                    break

                airports = item.find_all("div", {"class": re.compile(regex_start)})
                start_iata = airports[0].text[:3]
                start_name = self.__iatacodes.getCityByIataCode(start_iata)
                end_iata = airports[1].text[:3]
                end_name = self.__iatacodes.getCityByIataCode(end_iata)

                price = item.find("div", {"class": re.compile(regex_price)}).text.replace(u'\xa0', u' ')
                if ".nl" in link_item[1]:
                    if "/" in price:
                        price = float(price[price.find(" ") + 1:price.find("/")])

                    else:
                        price = float(price[price.find(" ") + 1:])

                else:
                    price = float(price[:price.find(" ")])

                stops = item.find("span", {"class": re.compile(regex_stops)}).text
                if "dir" in stops or "Nonstop" in stops:
                    stops = "Nonstop"

                else:
                    stops = int(stops[:1])
                    if stops == 1:
                        stops = str(stops) + " Stopp"

                    else:
                        stops = str(stops) + " Stopps"

                traveltime = item.find("div", {"class": re.compile(regex_traveltime)}).text

                time = item.find("div", {"class": re.compile(regex_time)}).text
                # special character "–"
                time_start = time.split("–")[0]
                time_end = time.split("–")[1]

                start_date = link_item[1][link_item[1].find("/20") + 1:link_item[1].find("/20") + 11]
                start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").strftime("%d.%m.%Y")

                if sum(self.__settings["persons"][:4]) >= 2:
                    price_sum = item.find_all("div", {"class": re.compile(regex_price_sum)})[1].text.replace(u'\xa0',
                                                                                                             u' ')

                    if "Gesamt:" in price_sum or "Total:" in price_sum:
                        price_sum = price_sum[price_sum.find(" ") + 1:price_sum.find(" €")]

                    elif "totaal" in price_sum:
                        price_sum = price_sum[price_sum.find(" ") + 1:price_sum.find(" ", 2)]

                    else:
                        price_sum = price_sum[:price_sum.find(" €")]

                    price_sum = float(price_sum)

                    data.append(
                        [price_sum, price, start_iata, start_name, end_iata, end_name, start_date, time_start, time_end,
                         traveltime,
                         stops,
                         link_item[1]])

                else:
                    data.append(
                        [price, start_iata, start_name, end_iata, end_name, start_date, time_start, time_end,
                         traveltime, stops,
                         link_item[1]])

                entries += 1

        if self.__debug:
            print("Data:", data)

        return data

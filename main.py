import os
import time

from queue import Queue
from threading import Thread

from flight_settings import FlightSettings
from scraper import Scraper
from excel import ExcelWriter


def main():
    debug = False
    timer_start = time.time()

    print("Welcome to FlightningSearchv2")

    print("\n > reading settings")
    flight_settings = FlightSettings()
    flight_settings.readSettings()
    settings_status, settings_error = flight_settings.validateSettings()

    if settings_status == -1:
        print("Could not start Process. Error occurred:")
        print(settings_error)

    settings_data = flight_settings.getSettings()
    del flight_settings

    web_scraper = Scraper(settings_data, debug=debug)
    print("\n > creating urls")
    links = web_scraper.createLinksPORTAL()
    print(f" > created {len(links)} urls")

    queue_get = Queue()
    queue_put = Queue()
    [queue_get.put(i) for i in links]

    print("\n > starting flightdata scraping")
    print(" > this can take a while, please wait!\n")

    cpu_count = int((os.cpu_count() * 0.5) // 1)

    th = []
    for i in range(cpu_count if queue_get.qsize() > cpu_count else queue_get.qsize()):
        th.append(Thread(target=web_scraper.scrapeData, args=(queue_get, queue_put, i)))
        th[i].start()
        time.sleep(1)

    if not debug:
        q_start_size = queue_get.qsize()
        block = q_start_size / 50

        loading_bar = "█"
        count = 1
        while True:
            percentage = (q_start_size - queue_get.qsize()) / block * 2

            print(f"\r > scraping data {'.' * count} {' ' * (3 - count)}|"
                  f"{loading_bar * int((q_start_size - queue_get.qsize()) // block)}"
                  f"{'═' * (int((q_start_size / q_start_size * 50) - (q_start_size - queue_get.qsize()) // block) - 1)}| "
                  f"{percentage:.1f} %", end="")

            if percentage == 100:
                break

            count += 1
            if count == 4:
                count = 1

            time.sleep(1)

    print("\n\n > closing all threads")
    for i in range(len(th)):
        th[i].join()

    data = list(queue_put.queue)
    del queue_put, queue_get

    print("\n > extracting flightdata")
    if settings_data["return_flight"] == 1:
        data_end = web_scraper.formatData_withreturn(data)

    else:
        data_end = web_scraper.formatData_noreturn(data)

    del web_scraper

    exceljob = ExcelWriter()

    if len(data_end) == 0:
        print(" > Sorry! no flights were found!")

        return
    
    else:
        if len(data_end[0]) == 0:
            print(" > Sorry! no flights were found!")

            return

    print("\n > writing flightdata to excel")

    if len(data_end[0]) >= 20:
        exceljob.return_write_to_excel(data_end)

    else:
        exceljob.write_to_excel(data_end)

    del exceljob

    timer_end = time.time()

    print(
        f"\nFinished after {(timer_end - timer_start) // 60:.0f}:{(timer_end - timer_start) % 60:.0f} min")


if __name__ == "__main__":
    main()

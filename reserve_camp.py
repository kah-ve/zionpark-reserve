from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import requests
import json
import time
import datetime
import pytz
import sys
import random
import calendar

from general_utils import (
    log_in,
    WEBDRIVER_PATH,
    smart_sleep,
    send_discord_notification,
    wait_for_login_screen_or_refresh_till_success,
    navigate_to_date,
    DateObject,
)

SOUTH_CAMP = "https://www.recreation.gov/camping/campgrounds/272266/availability"
WATCH_CAMP = "https://www.recreation.gov/camping/campgrounds/232445/availability"
curr_site = ""
url_of_site = ""
desired_date_global = "05/26/2021"  # Format MM/DD/YYYY


class alert_is_not_present(object):
    """Expect an alert to not to be present."""

    def __call__(self, driver):
        try:
            alert = driver.switch_to.alert
            alert.text
            return False
        except:
            return True


def parse_dates(input_date: str):
    # input date is in format MM/DD/YYYY
    # output date will be in format Mon DD, YYYY (e.g. May 2, 2021)

    date_array = input_date.split("/")
    month, day, year = date_array

    months_dict = dict(zip(range(1, 13), calendar.month_abbr[1:]))

    parsed_month = months_dict[int(month)]
    parsed_date = f"{parsed_month} {int(day)}, {year}"
    return parsed_date


def add_campsite_to_cart(
    driver: WebDriver,
    rows: list[WebElement],
    desired_date: str,
    prefer_sites=set(range(107, 125)),
    reserved_count: int = 0,
):
    global curr_site, url_of_site

    for row in rows:
        campsite: list[WebElement] = row.find_elements_by_class_name("rec-availability-item")

        assert len(campsite) == 1

        campsite_num = campsite[0].text

        matched: list[WebElement] = row.find_elements_by_class_name("rec-availability-date")

        for element in matched:
            aria_label: str = element.get_attribute("aria-label")
            date_from_aria = aria_label.split(" - ")[0]

            availability = element.text
            # print(
            #     f"Campsite {campsite_num} at Date {date_from_aria} is currently: {'available' if availability not in ['R', 'X'] else 'reserved'}"
            # )

            parsed_date = parse_dates(desired_date)

            if date_from_aria != parsed_date:
                continue

            if availability not in ["R", "X"]:
                driver.execute_script("arguments[0].click();", element)
                print(f"Pressed Button on {desired_date} for campsite: {campsite_num}")

                add_to_cart = driver.find_element_by_class_name("availability-page-book-now-button-tracker")
                driver.execute_script("arguments[0].click();", add_to_cart)
                print(f"Pressed add to cart for campsite {campsite_num} at date {desired_date}")

                send_discord_notification(
                    f"Campsite {campsite_num} available at date: {parsed_date}!", curr_site, url_of_site
                )
                # for _ in range(5):
                #     playsound('beep-01a.mp3')

                time.sleep(2)
                check_availability_and_reserve(driver, url_of_site, reserved_count + 1)
                return

    print("No available sites. Nothing has been added to cart.")


def refresh_table(driver: WebDriver):
    # Be wary of the booking notification block after hitting add to cart.
    # need to navigate around it. It's class name is: booking-notification-block
    buttons: list[WebElement] = driver.find_elements_by_class_name("sarsa-button-sm")  # type: ignore

    smart_sleep()

    print("Looking for refresh table button.")
    for button in buttons:
        span_contents: list[WebElement] = driver.find_elements_by_class_name("sarsa-button-content")  # type: ignore
        for content in span_contents:
            if content.text == "Refresh Table":
                print("Refreshing table.")
                driver.execute_script("arguments[0].click();", button)
                return


def check_availability_and_reserve(driver: WebDriver, url: str, reserved_count: int = -1):
    # desired_date = (date.today() + datetime.timedelta(days=14)).strftime("%b %d, %Y")
    # desired_date="May 22, 2021"
    global desired_date_global
    desired_date = desired_date_global

    if reserved_count == 5:
        return

    try:
        while True:
            driver.get(url)

            # Only log in the first attempt
            if reserved_count == -1:
                wait_for_login_screen_or_refresh_till_success(driver, "rec-availability-date", runner, sys.argv[1])
                log_in(driver)
                reserved_count += 1

            print("\nWaiting for page to load...")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "rec-availability-date")))
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "SingleDatePickerInput_calendarIcon"))
            )
            print("Page has loaded!")

            navigate_to_date(driver, desired_date, "single-date-picker-1")

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "rec-availability-date")))

            rows: list[WebElement] = driver.find_elements_by_class_name("undefined")  # type: ignore

            add_campsite_to_cart(driver, rows, desired_date, reserved_count)

            print("Refreshing page to try to find available dates for criteria...\n")
            refresh_table(driver)
            print("Table is refreshed.")

    except Exception as e:
        print(e)
        # win32api.MessageBox(0, "Failure.", "Failure", 0x00001000)
    finally:
        # print('Attempting to restart script')
        # runner(sys.argv[1])
        pass


def open_site(url: str):

    print(f"Opening site {url}.")
    options: Options = webdriver.FirefoxOptions()
    # options.headless = True
    options.headless = False

    driver: WebDriver = webdriver.Firefox(options=options, executable_path=WEBDRIVER_PATH)
    try:
        check_availability_and_reserve(driver, url)
    finally:
        driver.close()
        driver.quit()


def runner(campground):
    global curr_site, SOUTH_CAMP, WATCH_CAMP, url_of_site

    if campground != "W" or campground != "S":
        assert ValueError, "Campground must either be W or S for Watchman and South"

    if campground == "S":
        print("\n######################\nBeginning search for South Campground Sites\n######################\n")
        curr_site = "SOUTH_CAMP"
    else:
        print("\n######################\nBeginning search for Watchman Campground Sites\n######################\n")
        curr_site = "WATCH_CAMP"

    dateObj = DateObject()
    # while (dateObj.get_current_time()[:5] != "09:59"):
    #     print(f"Not yet time. Currently it is {dateObj.get_current_time()}")
    #     time.sleep(5)

    print(f"Time is now {dateObj.get_current_time()}!")
    print("Beginning reserve script.")

    url_of_site = SOUTH_CAMP if campground == "S" else WATCH_CAMP
    open_site(url_of_site)


if __name__ == "__main__":
    runner(sys.argv[1])

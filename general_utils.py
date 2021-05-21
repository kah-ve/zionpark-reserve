from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
import os
from dotenv import load_dotenv
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

load_dotenv()
WEBDRIVER_PATH = os.path.normpath(os.getenv("WEBDRIVER_PATH"))  # type: ignore
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
PASSWORD = os.getenv("ZION_PASSWORD")
USERNAME = os.getenv("ZION_USERNAME")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))


class DateObject:
    def __init__(self, timezone: str = "US/Eastern"):
        self.__tz = pytz.timezone(timezone)

    def __update_current_time(self) -> None:
        self.__current_time = datetime.datetime.now(self.__tz)
        self.__curr_str_time = self.__current_time.strftime("%H:%M:%S")

    def print_curr_time(self) -> str:
        self.__update_current_time()
        return f"Current time US/Eastern is: {self.__curr_str_time}"

    def get_current_time(self) -> str:
        self.__update_current_time()
        return self.__curr_str_time


def send_discord_notification(stats: str, curr_site, url_of_site):

    dateObj = DateObject()
    data = {
        "content": f"{stats}\n\nCampground: \
        {curr_site}!\nAdd to Cart Successful at time \
            {dateObj.get_current_time()}\n \
                Go to URL: {url_of_site}\n"
    }

    result = requests.post(
        # type: ignore
        DISCORD_WEBHOOK_URL,
        data=json.dumps(data),
        headers={"Content-Type": "application/json"},
    )
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Discord Payload delivered successfully, code {}.".format(result.status_code))


def log_in(driver: WebDriver):

    print("Logging in...")
    global PASSWORD, USERNAME

    username = USERNAME
    password = PASSWORD

    sign_in_div: WebElement = driver.find_element_by_class_name("nav-user-sign-in")  # type: ignore
    sign_in_buttons: list[WebElement] = sign_in_div.find_elements_by_class_name("nav-header-button")

    for button in sign_in_buttons:
        if button.text == "Log In":
            driver.execute_script("arguments[0].click();", button)

            email_input = driver.find_element_by_id("rec-acct-sign-in-email-address")
            password_input = driver.find_element_by_id("rec-acct-sign-in-password")

            email_input.send_keys(username)  # type: ignore
            password_input.send_keys(password)  # type: ignore

            # Press Log In Button
            log_in_btn = driver.find_element_by_class_name("rec-acct-sign-in-btn")
            driver.execute_script("arguments[0].click();", log_in_btn)
            print("Logged in.")

    # Wait till login page is gone.
    WebDriverWait(driver, 10).until(EC.invisibility_of_element((By.ID, "signInModalHeading")))


def smart_sleep():
    base_sleep = 1
    total_sleep = base_sleep + random.uniform(0, 6)

    print(f"Sleeping for {total_sleep} seconds before refreshing table.")
    time.sleep(total_sleep)


def wait_for_login_screen_or_refresh_till_success(
    driver: WebDriver, class_to_wait_for: str, script_runner_func, arguments_for_runner_func=None
):

    attempt: int = 1
    while True:
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, class_to_wait_for)))
            return
        except:
            print(f"Login screen not loaded. Refreshing and trying again! On attempt: {attempt}")
            attempt += 1
            if attempt > 5:
                # Try to restart
                print("Too many attempts to try to login. Restarting script")
                script_runner_func(arguments_for_runner_func)


def navigate_to_date(driver: WebDriver, desired_date: str, date_picker_element, id=True):
    print(f"Navigating to intended date. {desired_date}")

    if id:
        select_date: WebElement = driver.find_element_by_id(date_picker_element)  # type: ignore
    else:
        select_date: WebElement = driver.find_element_by_class_name(date_picker_element)  # type: ignore

    select_date.click()

    select_date.send_keys(Keys.CONTROL, "a")
    select_date.send_keys(desired_date)

    print(f"Navigated to date: {desired_date}")

from reserve_camp import wait_for_login_screen_or_refresh_till_success
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from datetime import date
import sys

from general_utils import DateObject, log_in, WEBDRIVER_PATH, navigate_to_date, smart_sleep, send_discord_notification

# Tickets listed as ‘Not Yet Released’ will be available at 5:00 p.m. MT the day before. (7PM ET)

SHUTTLE_SITE = "https://www.recreation.gov/ticket/300016/ticket/3010"
curr_site = ""
desired_date_global = "05/22/2021"  # Format MM/DD/YYYY
desired_times_global = []

headless_global = True

wait_global = False

another_date_obj = DateObject()
current_time_hours_mins = another_date_obj.get_current_time()

# TODO: Need to revert this after quantity testing is complete! Also make headless is TRUE
start_time_global = "18:59"
# start_time_global = current_time_hours_mins[:5]
end_time_global = "19:10"
wait_out_time_global = "20:00"


def refresh_page_and_continue(driver):
    driver.refresh()


def increase_quantity_to_two(driver: WebDriver):
    print("Attempting to increase quantity to two!")
    # Open quantity selection
    quantity_open_button = "guest-counter"
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, quantity_open_button)))

    open_quantity_button = driver.find_element_by_id(quantity_open_button)
    driver.execute_script("arguments[0].click();", open_quantity_button)

    # Find the div that holds the increase quantity button
    div_holder_of_increase_button = "rec-guest-counter-row"
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, div_holder_of_increase_button)))
    open_div_holder_of_increase_button: WebElement = driver.find_element_by_class_name(div_holder_of_increase_button)

    # Get the button we want from within this element
    plus_and_minus_button_class_name = "sarsa-button-subtle"
    buttons = open_div_holder_of_increase_button.find_elements_by_class_name(plus_and_minus_button_class_name)

    select_plus_button = buttons[1]
    driver.execute_script("arguments[0].click();", select_plus_button)

    # # Hit close and continue (probably not needed)
    # close_button_selector = "sarsa-button-link"
    # button = open_div_holder_of_increase_button.find_element_by_class_name(close_button_selector)
    # driver.execute_script("arguments[0].click();", button)
    print("Successful at increasing quantity to two!")


def add_shuttle_to_cart(driver, intended_times, desired_date, reserved_count):
    global SHUTTLE_SITE

    for element in intended_times:
        timing = element.text
        print(f"I see times for {timing}")

        time_in_digits = timing[:5].split(":")
        time_in_digits = time_in_digits[0]

        if len(desired_times_global) == 0 or time_in_digits in desired_times_global:
            driver.execute_script("arguments[0].click();", element)
            print("Clicked on time button!")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "sarsa-button-primary")))

            try:
                is_add_to_cart_disabled: WebElement = driver.find_element_by_class_name("sarsa-button-disabled")  # type: ignore
                continue
            except:
                print("Disabled Button Not Found. Add to Cart Button is Available.")

            add_to_cart = driver.find_element_by_class_name("sarsa-button-primary")
            driver.execute_script("arguments[0].click();", add_to_cart)
            print("Clicked on add to cart button! Reserved the shuttle!")
            reserved_count[0] += 1

            print(f"Pressed add to cart for timing {timing} at date {desired_date}")

            send_discord_notification(
                f"Shuttle at {timing} available at date: {desired_date}!", "Shuttle Website!", SHUTTLE_SITE
            )

            time.sleep(1)
            return check_availability_and_reserve(driver, SHUTTLE_SITE, reserved_count)


def check_if_shuttle_times_are_available(driver, url, reserved_count):
    try:
        WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "ti-radio-pill-time")))
    except:
        print("Times are not available! Refresh and try again!")
        smart_sleep()
        refresh_page_and_continue(driver)
        return check_availability_and_reserve(driver, url, reserved_count)


def check_if_need_to_short_circuit():
    global desired_date_global, end_time_global

    date_obj = DateObject()
    current_time = date_obj.get_current_time()
    if current_time[:5] == end_time_global:
        tomorrows_date = str(int(desired_date_global) + 1)
        desired_date_global = tomorrows_date
        return runner()


def check_if_need_to_stop_from_discord():
    with open("output.log", "r+") as f:
        text = f.read()
        if text == "STOP":
            f.write("EMPTY")
            return True
        else:
            return False


def check_availability_and_reserve(driver: WebDriver, url: str, reserved_count=[-1]):
    desired_date = date.today().strftime("%m-%Y")

    does_discord_want_stop = check_if_need_to_stop_from_discord()
    if does_discord_want_stop:
        print("Stopping from discord command after running")
        driver.close()
        driver.quit()
        return

    check_if_need_to_short_circuit()

    global desired_date_global
    if desired_date_global != "":
        date_split = desired_date.split("-")
        desired_date = f"{date_split[0]}/{desired_date_global}/{date_split[1]}"
    else:
        desired_date = date.today().strftime("%m/%d/%Y")

    print(desired_date)

    if reserved_count[0] == 5:
        global wait_global
        wait_global = True
        return runner()

    try:
        while True:
            driver.get(url)

            # Only log in the first attempt
            if reserved_count[0] == -1:
                wait_for_login_screen_or_refresh_till_success(
                    driver, "SingleDatePickerInput_calendarIcon", runner, None
                )
                log_in(driver)
                reserved_count[0] += 1

            print("\nWaiting for page to load...")

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "SingleDatePickerInput_calendarIcon"))
            )
            print("Page has loaded!")
            increase_quantity_to_two(driver)

            navigate_to_date(driver, desired_date, "DateInput_input_1", False)

            check_if_shuttle_times_are_available(driver, url, reserved_count)

            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "ti-radio-pill-available")))

            intended_times: list[WebElement] = driver.find_elements_by_class_name("ti-radio-pill-time")

            add_shuttle_to_cart(driver, intended_times, desired_date, reserved_count)

            print("Restarting checking process.\n")
            smart_sleep()
            return check_availability_and_reserve(driver, url, reserved_count)
            print("Page is refreshed.")

    except Exception as e:
        print(e)
    finally:
        # print('Attempting to restart script')
        # runner(sys.argv[1])
        pass


def open_site(url: str):
    global headless_global
    print(f"Opening site {url}.")
    options: Options = webdriver.FirefoxOptions()
    options.headless = headless_global

    driver: WebDriver = webdriver.Firefox(options=options, executable_path=WEBDRIVER_PATH)
    try:
        check_availability_and_reserve(driver, url)
    finally:
        driver.close()
        driver.quit()


def runner():
    global SHUTTLE_SITE, wait_global, desired_date_global, desired_times_global, start_time_global, wait_out_time_global

    while True:
        does_discord_want_stop = check_if_need_to_stop_from_discord()
        if does_discord_want_stop:
            print("Stopping from discord command before kicking off run.")
            return

        date_obj = DateObject()
        current_time = date_obj.get_current_time()

        if wait_global:
            while current_time[:5] != wait_out_time_global and not does_discord_want_stop:
                if current_time[:2] == "18":
                    time.sleep(1)
                else:
                    time.sleep(20)

                print(f"Current time is {current_time} and am waiting for 8pm to continue with next iteration")
            wait_global = False
            return runner()

        print(f"The current time is: {current_time} Waiting for 7pm ET for shuttle reservation to open.")

        if current_time[:5] == start_time_global:
            print(
                f"Time is reached. Moving forward with trying to find website for date {desired_date_global} and for times {desired_times_global}"
            )
            open_site(
                SHUTTLE_SITE,
            )

        time.sleep(5)


def run_main(desired_date, desired_times):
    global desired_times_global, desired_date_global
    desired_times_global, desired_date_global = [], ""

    desired_date_global = desired_date

    for times in desired_times.split(","):
        desired_times_global.append(times)

    print(f"Desired Date is: {desired_date_global} and Desired Time(s) is: {desired_times_global}")
    runner()


if __name__ == "__main__":
    run_main(sys.argv[1], sys.argv[2])

    # # day = sys.argv[1]
    # # print(f"Will look at day {day}")

    # if len(sys.argv) > 1:

    #     desired_date_global = sys.argv[1]

    #     collection_of_times = sys.argv[2]
    #     for times in sys.argv[2].split(","):
    #         desired_times_global.append(times)

    # print(f"Desired Date is: {desired_date_global} and Desired Time(s) is: {desired_times_global}")
    # runner()

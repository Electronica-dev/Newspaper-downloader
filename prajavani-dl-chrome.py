
# Web scraping program to download e-paper from the newspaper provider Prajavani, and send it to an email. Chrome
# compatible version.

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
from datetime import date
from os import makedirs
from os import path
from os import environ
import sys
from math import ceil
from time import sleep
# import urllib3
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# if len(sys.argv) < 2:
#     print('Usage: prajavani-dl-chrome.py [recipient-email-address 1] [recipient-email-address 2] ['
#           'recipient-email-address n]')
#     sys.exit()
# else:
#     recipientAddress = sys.argv[1:]

dateToday = date.today().strftime("%d-%m-%Y")

# desired_cap = {
#     'platform': "Windows 10",
#     'browserName': "Chrome",
#     'version': "84",
#     'build': "Onboarding Sample App - Python",
#     'name': "Newspaper-Scraper-Windows-Chrome",
#     'tunnel-identifier': environ['TRAVIS_JOB_NUMBER']
# }

# username = environ["SAUCE_USERNAME"]
# access_key = environ["SAUCE_ACCESS_KEY"]
# driver = webdriver.Remote(desired_capabilities=desired_cap, command_executor='https://{}:{}@ondemand.eu-central-1.saucelabs.com:443/wd/hub'.format(username, access_key))

options = Options()
options.add_argument('--no-sandbox')

driver = webdriver.Chrome()
driver.get('http://epaper.prajavani.net')  # Base url.
driver.maximize_window()  # Maximizing window, else the downloadButton element won't be click-able.


def click_download_button():
    download_button = driver.find_element_by_xpath('//*[@id="btnPrintSave"]')
    download_button.click()


def click_close_button():
    close_button = driver.find_element_by_xpath('//*[@id="printSavePanel"]/div/div/div[1]/div/div/ul/li')
    close_button.click()


def click_next_button():
    next_button = driver.find_element_by_id('btn-next')
    next_button.click()


def click_open_left_page():
    left_page = driver.find_element_by_xpath('//*[@id="leftPageThumb"]/div/div[3]')
    left_page.click()


def click_open_right_page():
    right_page = driver.find_element_by_xpath('//*[@id="rightPageThumb"]/div/div[3]')
    right_page.click()


# First and last page are shown up individually.
def open_first_and_last_page():
    while True:
        thumbnail_container_width = driver.find_element_by_xpath('//*[@id="leftPageThumb"]/div/div[3]').size.get(
            'width')
        if thumbnail_container_width == 141:
            click_open_left_page()
            driver.switch_to.window(driver.window_handles[0])
            click_close_button()
            break


# Checking if the size is shown and page thumbnail is loaded.
def check_size_and_width_middle_pages():
    while True:
        left_thumbnail_container_width = driver.find_element_by_xpath('//*[@id="leftPageThumb"]/div/div[3]').size.get(
            'width')
        right_thumbnail_container_width = driver.find_element_by_xpath('//*[@id="rightPageThumb"]/div/div[3]').size.get(
            'width')
        if left_thumbnail_container_width == 141 and right_thumbnail_container_width == 141:
            click_open_left_page()
            driver.switch_to.window(driver.window_handles[0])
            click_open_right_page()
            driver.switch_to.window(driver.window_handles[0])
            click_close_button()
            break


# Checking if the menu toolbar has loaded.
while True:
    menuWidthCheck = int(driver.find_element_by_xpath('//*[@id="mainmenu"]/div').size.get('width'))
    if menuWidthCheck == 438:
        driver.find_element_by_id('btnPublicationsPanel').click()
        driver.find_element_by_id('pubFilterEdition').click()
        driver.find_element_by_xpath('//*[@id="pubFilterEdition"]/option[3]').click()
        break

while True:
    sleep(2)
    downloadEnableCheck = driver.find_element_by_xpath('//*[@id="mainmenu"]/div/ul/li[7]').get_attribute('class')
    if downloadEnableCheck == 'printSaveFeature':
        click_download_button()
        noOfPages = int(driver.find_element_by_xpath('//*[@id="tpContainer"]/h3/small').get_attribute(
            'data-pginsection'))
        break

# Load first page.
open_first_and_last_page()

# Loop to load all the middle pages.
for i in range(int(ceil(noOfPages - 2) / 2)):
    click_next_button()
    click_download_button()
    check_size_and_width_middle_pages()

# Sequence to load last page.
if not noOfPages % 2:
    click_next_button()
    click_download_button()
    open_first_and_last_page()

folderPath = 'C:/Users/Sammy/Desktop/Prajavani ' + dateToday
makedirs(folderPath)  # Make a folder in desktop with today's date.

# Loop to download pages to the folder.
for i in range(1, (noOfPages + 1)):
    driver.switch_to.window(driver.window_handles[i])
    res = requests.get(driver.current_url)
    res.raise_for_status()
    filePath = open(path.join(folderPath, str(i) + '.pdf'), 'wb')
    print('Downloading page ' + str(i))
    for chunk in res.iter_content(100000):
        filePath.write(chunk)
    filePath.close()

driver.quit()  # Close browser.

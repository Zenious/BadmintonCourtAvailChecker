"""Badminton Availability Checker"""
import os
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

load_dotenv()

USERNAME = os.getenv('ACTIVESG_USERNAME')
PASSWORD = os.getenv('ACTIVESG_PASSWORD')

venues = []
DATE = '2021-10-09'
EPOCH_TIME = 1633622400
driver = webdriver.Chrome('./chromedriver')
driver.get('https://members.myactivesg.com/auth')

driver.find_element(By.ID, "email").send_keys(USERNAME)
driver.find_element(By.ID, "password").send_keys(PASSWORD)
time.sleep(2)
driver.find_element(By.ID, "btn-submit-login").click()

time.sleep(1)
driver.get('https://members.myactivesg.com/facilities/view/activity/18/venue/292')
time.sleep(1)
select = Select(driver.find_element(By.ID, 'facVenueSelection'))
for option in (select.options):
    if not option.get_attribute("value"):
        continue
    venues.append([option.text, option.get_attribute("value")])

cookies = driver.get_cookies()
s = requests.Session()
for cookie in cookies:
    s.cookies.set(cookie['name'], cookie['value'])
driver.close()


for venue_name, venue_no in venues:
    # venue_no= 316
    headers = {
        'authority': 'members.myactivesg.com',
        'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'x-requested-with': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': f'https://members.myactivesg.com/facilities/view/activity/18/venue/\
            {venue_no}',
        'accept-language': 'en-US,en;q=0.9,fr;q=0.8',
    }

    # print(f'Getting result for {venue_name}')
    res = s.get(
        f'https://members.myactivesg.com/facilities/ajax/getTimeslots?\
        activity_id=18&venue_id={venue_no}&DATE={DATE}', headers=headers)
    time.sleep(1)
    content = res.json()
    if isinstance(content) is str:
        if "There are no available slots for your preferred DATE." in content:
            continue
        print(content)
    content = content['activesg']
    tags = content.replace('\\/', '/')
    soup = BeautifulSoup(tags, "html.parser")
    courts = soup.find_all("div", class_="subvenue-slot")
    # print(f'Found {len(courts)} courts')

    for court in courts:
        court_string = court.find("h4").text
        for a, t in (list(zip(court.find_all("input"), court.find_all("label")))):
            if not a.get("disabled") == "":
                print(f'{venue_name}: {court_string} have availability at {t.text}')

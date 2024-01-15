import json
import os
from time import sleep
from requests import Session
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

            
CACHE_FILE = "./selenium_cache.json"
URL = ""

chrome_options = Options()
chrome_options.add_argument("window-size=1200x600")
chrome_options.add_argument("user-data-dir=./profile")
driver = webdriver.Chrome(options=chrome_options)

wait = WebDriverWait(driver, 10)

session = Session()

cache = {}
if os.path.exists(CACHE_FILE):
    with open(file=CACHE_FILE, mode="r") as cache_file:
        cache = json.load(cache_file)

driver.get(f"https://{URL}/faces/game")

sleep(1)

try:
    play_button = driver.find_element(By.CLASS_NAME, "rotation-loader")
except NoSuchElementException:
    print("You are not authentified")
        
    while True:
        print("Press to Y where you are authentificated")
        result = input()
        if result.upper() == "Y":
            break
        
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "rotation-loader")))
    play_button = driver.find_element(By.CLASS_NAME, "rotation-loader")
        
auth_token_cookie = driver.get_cookie("authToken")
session.cookies.set("authToken", value=auth_token_cookie["value"])

play_button.click()

while True:
    try:
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ng-trigger-questionAnimation")))
    except Exception:
        break
    
    buttons = driver.find_elements(By.CLASS_NAME, "ng-trigger-questionAnimation")
    
    valid_buttons: list[WebElement] = []
    for button in buttons:  
        if button.accessible_name in cache.keys():
            valid_buttons.append(button)
            
    if len(valid_buttons) == 1:
        valid_buttons[0].click()
    else:
        image_element = driver.find_element(By.CLASS_NAME, "image")

        image_url = image_element.value_of_css_property("background-image")
        image_url = image_url.replace('url("', "").replace('")', "")

        image = session.get(url=image_url)
        image_wreight = image.headers["content-length"]
        
        for button in valid_buttons:
            if cache[button.accessible_name] == image_wreight:
                button.click()
                break
            
    sleep(2.1)
            
driver.quit()
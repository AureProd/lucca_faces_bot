import json
import os
from time import sleep
from requests import Session
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
 
CACHE_FILE = "./selenium_cache_bis.json"
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

play_button = driver.find_element(By.CLASS_NAME, "rotation-loader")
if not play_button:
    print("You are not authentified")
    
    while True:
        print("Press to Y where you are authentificated")
        result = input()
        if result.upper() == "Y":
            break
        
auth_token_cookie = driver.get_cookie("authToken")
session.cookies.set("authToken", value=auth_token_cookie["value"])

play_button.click()

while True:
    try:
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ng-trigger-questionAnimation")))
    except Exception:
        break
    
    buttons = driver.find_elements(By.CLASS_NAME, "ng-trigger-questionAnimation")
    
    image_element = driver.find_element(By.CLASS_NAME, "image")
    
    image_url = image_element.value_of_css_property("background-image")
    image_url = image_url.replace('url("', "").replace('")', "")

    image = session.get(url=image_url)
    image_wreight = image.headers["content-length"]
    
    clicked = False
    for button in buttons:    
        if button.accessible_name not in cache.keys():
            continue
        
        if cache[button.accessible_name] == image_wreight:
            clicked = True
            button.click()
            break
        
    if not clicked:
        print("Give me the number of good button please")
        result = input()
        if result in ["1", "2", "3", "4"]:
            button = buttons[int(result) - 1]
            button.click()
            cache[button.accessible_name] = image_wreight
            
    sleep(2.1)
            
driver.quit()

with open(CACHE_FILE, 'w') as cache_file:
    json.dump(cache, cache_file)
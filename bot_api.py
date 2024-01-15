import json
import math
import os
from requests import session
from tqdm import tqdm
from PIL import Image
from io import BytesIO

def parse_picture(response):
    img = Image.open(BytesIO(response.content))
    width, height = img.size
    center_x = width // 2
    center_y = height // 2
    return img.getpixel((center_x, center_y))

def check_pictures(picture, picture_response):
    question_picture = parse_picture(response=picture_response)
    
    if picture == question_picture:
        return True
    try:
        proba = math.dist(picture, question_picture)
    except ValueError:
        return False
    return proba < 30

# CONSTANTS

URL = ""
TOKEN = ""
CACHE_FILE = "./cache.json"
CHECK_CACHE_FILE = "./check_cache.json"

# AUTH

print("Start iluca game bot")

session = session()

session.cookies.set("authToken", value=TOKEN)

# GET TEAMMATES PICTURES

print("Recuperation of teammates pictures")

teammates = {}
if os.path.exists(CACHE_FILE):
    with open(file=CACHE_FILE, mode="r") as cache_file:
        teammates = json.load(cache_file)
else:
    teammates_data = session.get(url=f"https://{URL}/api/v3/users/scope?appInstanceId=5&operations=1&fields=id,name,firstName,lastName,mail,directLine,professionalMobile,jobTitle,birthDate,picture%5Bid,name,url,href,mimetype%5D,collection.count&orderBy=lastName,asc&paging=0,100").json()

    for teammate in tqdm(teammates_data["data"]["items"]):
        if teammate["picture"] is None:
            continue
        
        teammate_picture = session.get(url=teammate["picture"]["href"])
        
        teammates[teammate["name"]] = parse_picture(response=teammate_picture)
        
    with open(CACHE_FILE, 'w') as cache_file:
        json.dump(teammates, cache_file)

# READ SAVED CHECKS

already_check = {}
if os.path.exists(CHECK_CACHE_FILE):
    with open(file=CHECK_CACHE_FILE, mode="r") as cache_file:
        already_check = json.load(cache_file)
    
# START GAME

print("Start game")

game_data = session.post(url=f"https://{URL}/faces/api/games").json()
game_id = game_data["id"]

highscore = 0
highscore_data = session.get(url=f"https://{URL}/faces/api/highscores?ownerId=26").json()
if len(highscore_data["items"]) == 1:
    highscore = highscore_data["items"][0]["score"]
    print(f"Your current highscore is {highscore}")

final_score = 0
for index in range(game_data["nbQuestions"]):
    question_data = session.post(url=f"https://{URL}/faces/api/games/{game_id}/questions/next").json()
    question_id = question_data["id"]
    question_picture = session.get(url=f"https://{URL}{question_data['imageUrl']}")
    
    question_picture_wreight = question_picture.headers["content-length"]
    
    good_response = None
    not_saved = False
    for response in question_data["suggestions"]:  
        if response["value"] not in already_check.keys():
            if response["value"] not in teammates.keys():
                continue
            
            if check_pictures(picture=teammates[response["value"]], picture_response=question_picture):
                good_response = response["id"]
                print("not saved")
                not_saved = True
                break 
              
        if already_check[response["value"]] == question_picture_wreight:
            good_response = response["id"]
            break       
    
    result_data = session.post(url=f"https://{URL}/faces/api/games/{game_id}/questions/{question_id}/guess", json={"questionId": question_id, "suggestionId": good_response}).json()
    
    final_score += result_data['score']
    print(f"Current score : {final_score} (Response {'OK' if good_response == result_data['correctSuggestionId'] else 'NOK'}) + {result_data['score']}")
    
    if not_saved and good_response == result_data['correctSuggestionId']:
        already_check[response["value"]] = question_picture_wreight
        
print(f"Game finish (final score : {final_score}) {'This is the new highscore' if final_score > highscore else ''}")

# RETURN NEW HIGHSCORD

highscore_data = session.get(url=f"https://{URL}/faces/api/highscores?ownerId=26").json()
if len(highscore_data["items"]) == 1:
    highscore = highscore_data["items"][0]["score"]
    print(f"Your current highscore is {highscore}")
    
# SAVE NEW CHECKS   
    
with open(CHECK_CACHE_FILE, 'w') as cache_file:
    json.dump(already_check, cache_file)
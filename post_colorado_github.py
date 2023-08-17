import requests
import json
import random
from atproto import Client
import os

USERNAME = os.environ["USERNAME_VAR"]
PASS = os.environ["PASS_VAR"]
print("here's the environ again", os.environ)

print(USERNAME)
print(PASS)

def convert_coordinates(coordinates, NW):
    degrees, minutes, seconds = map(int, coordinates.split())
    return f"{degrees}° {minutes}' {seconds:.2f}\" {NW}"

def get_info_string(record):
    message = ""
    labels = {"project_roll_frame" : "ID",
              "date" : "Date",
              "publisher" : "Publisher",
              "county" : "County",
              "state" : "State",
              "landmark" : "Landmark"}
    for key, val in labels.items():
        if key in record.keys():
            message += f"{val} : {record[key]}\n"
    try:
        if "center_point_latitude" in record.keys() and "center_point_longitude" in record.keys():
            message += f"Coordinates : {convert_coordinates(record['center_point_latitude'],'N')}, {convert_coordinates(record['center_point_longitude'],'W')}\n"
    except:
        print("coorindate issue")
    if "identifier_ark" in record.keys():
        message += f"Source : {record['identifier_ark']}"
    return message

#read in extracted data, filter for slur
with open("extracted_metadata.json", 'r') as file:
    data = json.load(file)

approved_records = [x for x in data if "squaw".lower() not in " ".join([str(y) for y in x.values()]).lower()]

posted_ids = []
selected_record = random.choice(approved_records)
page_id = str(selected_record['wiki_id'])

if page_id not in posted_ids:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    #get image
    img_search = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&pageids={page_id}&iiprop=url"
    img_response = requests.get(img_search, headers=headers).json()
    image_info = img_response["query"]["pages"][str(page_id)]["imageinfo"]
    if image_info:
        img_url = image_info[0]["url"]
        img_data = requests.get(img_url, headers=headers).content
        with open(f"images/selection.jpg", 'wb') as file:
            file.write(img_data)
        with open("images/selection.jpg", 'rb') as file:
            img = file.read()
        client = Client()
        client.login(USERNAME, PASS)
        client.send_image(pagetext=get_info_string(selected_record), image=img, image_alt=f'Aerial shot looking down on {selected_record["county"]} county, {selected_record["state"]}')

        print(get_info_string(selected_record))
    else:
        print(f"No image found for pageid: {page_id}")
posted_ids.append(page_id)








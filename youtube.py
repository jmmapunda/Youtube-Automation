import requests
import random
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os
import pickle
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from cloudinary import CloudinaryVideo
from urllib.request import urlretrieve
import cloudinary
import cloudinary.api
import time
from dotenv import load_dotenv

# load_dotenv()
PEXELKEY = os.getenv('PEXELKEY')
cloudname = os.getenv('cloudname')
APIKEY = os.getenv('APIKEY')
APISECRET = os.getenv('APISECRET')
api_KEY_youtube = os.getenv('api_KEY_youtube')
client_id_youtube = os.getenv('client_id_youtube')
client_secret_youtube = os.getenv('client_secret_youtube')
YOUTUBE_REFRESH_TOKEN = os.getenv('YOUTUBE_REFRESH_TOKEN')

# print("refresh_token:", YOUTUBE_REFRESH_TOKEN[:5] + "..." if YOUTUBE_REFRESH_TOKEN else "MISSING")
# print("client_id:", client_id_youtube[:5] + "..." if client_id_youtube else "MISSING")
# print("client_secret:", client_secret_youtube[:5] + "..." if client_secret_youtube else "MISSING")

def horoscope(time, data):
    response = requests.get(time).json()
    data.append({
        "sign": sign,
        "horoscope": response['data']['horoscope_data']
        })

horoscope_signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius",
                   "Capricorn", "Aquarius", "Pisces"]

data_daily = []
data_weekly = []
data_monthly = []

today_date = datetime.now().strftime('%B %d, %Y')

for sign in horoscope_signs:
    horoscope_daily = f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily?sign={sign}&day=TODAY"
    horoscope_weekly = f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/weekly?sign={sign}"
    horoscope_monthly = f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/monthly?sign={sign}"
    if datetime.now().day == 1:
        horoscope(horoscope_monthly, data_monthly)
        youtube_title = f'Month of {datetime.now().strftime('%B')} Horoscope - {today_date}'

    elif datetime.now().weekday() == 0:
        horoscope(horoscope_weekly, data_weekly)
        youtube_title = f"This Week's Horoscope - {today_date}"

    else:
        horoscope(horoscope_daily, data_daily)
        youtube_title = f"Today's {today_date} Horoscope"


print(f'daily data: {data_daily}')
print(f'weekly data: {data_weekly}')
print(f'monthly data: {data_monthly}')

key_video = ['astrology', 'zodiac']
search_video = random.choice(key_video)
print(search_video)
# Endpoint for searching photos
url = "https://api.pexels.com/videos/search"

# Define parameters
params = {
    "query": search_video,  # The search term (can be anything)
    "orientation": 'portrait',  # Number of results per page (maximum is 80)
    "page": 1,  # The page number (for pagination)
    "size": 'large',
    "per_page": 20
    }
# Headers with the API key for authentication
headers = {
    "Authorization": PEXELKEY
    }

# Send GET request to Pexels API
response = requests.get(url, headers=headers, params=params)
video_list = []
# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    # print(data)
    for video in data["videos"]:
        video_list.append(video["video_files"][0]["link"])
else:
    print(f"Error: {response.status_code}")
#from image_list choice one image to work with
video_to_edit = random.choice(video_list)
print(video_to_edit)

cloudinary.config(
    cloud_name=cloudname,
    api_key=APIKEY,
    api_secret=APISECRET,
    secure=True
    )

# Upload a video
upload_result = cloudinary.uploader.upload(video_to_edit, public_id="horoscope", resource_type="video")
print("Uploaded Video URL:", upload_result["secure_url"])
video_time = int(cloudinary.api.resource(public_id="horoscope", resource_type="video", media_metadata=True)['duration'])
print(video_time)

if video_time < 100:
    loop_time = 100//video_time + 1
    video_original = CloudinaryVideo("horoscope")
    video_url_original = video_original.build_url(
        resource_type="video",
        transformation=[

            {'effect': f'loop:{loop_time}'},
            {'start_offset': '0', 'duration': '100'},
            {'width': 1080, 'height': 1920, 'crop': "scale"},
            ])
else:
    video_original = CloudinaryVideo("horoscope")
    video_url_original = video_original.build_url(
        resource_type="video",
        transformation=[

            {'start_offset': '0', 'duration': '100'},
            {'width': 1080, 'height': 1920, 'crop': "scale"},
            ])


download_path = "transformed_video.mp4"
urlretrieve(video_url_original, download_path)
upload_result_original = cloudinary.uploader.upload(download_path, public_id="horoscope_trimmed", resource_type="video")
print(f'Trimmed video url:{upload_result_original["secure_url"]}')


def cloudinary_text_overlay(line, colour, size, position, offset_time, offset_time_end):
    video = CloudinaryVideo("horoscope_trimmed")  # 👈 public_id without extension
    video_url = video.build_url(
        resource_type="video",
        transformation=[
            {
                'overlay': {
                    'font_family': "Palatino",  # Change to your preferred font
                    'font_size': size,
                    'font_weight': "bold",
                    'text': line,
                    'background': '#ffffff'
                    },
                'width': 980,
                'crop': "fit",
                'color': colour,  # Hex color or named color
                'gravity': position,
                'start_offset': offset_time,
                'end_offset': offset_time_end,
                'duration': "8",
                'y': 70,
                'flags': "layer_apply"
                }
            ]
        )
    return video_url



def horoscope_time_group(time_to_use):  #data_daily or data_weekly or data_monthly
    offset = 0
    offset_finish = 8
    final_video_url = ''
    for i in range(len(horoscope_signs)):
        print(f'for i.. {i + 1}')
        first_line = "%0A".join([time_to_use[i]['sign'],])
        rest_of_horoscope = "%0A".join([time_to_use[i]['horoscope'],])

        video_url = cloudinary_text_overlay(first_line, '#F28705', 150, 'north', offset, offset_finish)
        urlretrieve(video_url, download_path)
        upload_result = cloudinary.uploader.upload(download_path, public_id="horoscope_trimmed", resource_type="video")

        video_url_second = cloudinary_text_overlay(rest_of_horoscope, '#002333', 60, 'center', offset, offset_finish)
        urlretrieve(video_url_second, download_path)
        upload_result_second = cloudinary.uploader.upload(download_path, public_id="horoscope_trimmed", resource_type="video")
        time.sleep(3)
        offset += 8
        offset_finish += 8
        print(f'Batch url:{int(i) + 1}', upload_result_second["secure_url"])
        if time_to_use[i]['sign'] == horoscope_signs[len(horoscope_signs)-1]:
            final_video_url = upload_result_second["secure_url"]

    print("Generated Final Video URL with Overlay:", final_video_url)

    # ✅ Upload final video to YouTube
    local_path = "final_video.mp4"
    print("Uploading started...")

    try:
        urlretrieve(final_video_url, local_path)
        upload_video(local_path, youtube_title, youtube_description)
        print("Uploaded video successfully.")
    except Exception as e:
        print(f"Failed to upload video: {e}")
    finally:
        if os.path.exists(local_path):
            try:
                os.remove(local_path)
                os.remove(download_path)
                print("Cleaned up local video file.")
            except Exception as cleanup_error:
                print(f"Failed to delete local video file: {cleanup_error}")


url_youtube = 'https://www.googleapis.com/youtube/v3'
response = requests.get(url_youtube, api_KEY_youtube)
print(response)



# Set YouTube upload scope
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Authenticate and get credentials
# def authenticate_youtube():
#     creds = None
#     if os.path.exists("token.pickle"):
#         with open("token.pickle", "rb") as token:
#             creds = pickle.load(token)
#     if not creds:
#         flow = InstalledAppFlow.from_client_secrets_file("client_secret_youtube.json", SCOPES)
#         creds = flow.run_local_server(port=0)
#         with open("token.pickle", "wb") as token:
#             pickle.dump(creds, token)
#     youtube = build('youtube', 'v3', credentials=creds)
#     return youtube

def authenticate_youtube():
    creds = Credentials(
        token=None,
        refresh_token=YOUTUBE_REFRESH_TOKEN,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=client_id_youtube,
        client_secret=client_secret_youtube,
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    creds.refresh(Request())  # This fetches a new access token using the refresh token
    youtube = build('youtube', 'v3', credentials=creds)
    return youtube

# Download video from URL
def download_video_from_url(url, save_path):
    response = requests.get(url, stream=True)
    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

# Upload to YouTube
def upload_video(file_path, title, description):
    youtube = authenticate_youtube()
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": youtube_hashtags,
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }
    media = MediaFileUpload(file_path, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )
    response = request.execute()
    print(f"✅ Video uploaded: https://www.youtube.com/watch?v={response['id']}")

    # Cleanup local file
    os.remove(file_path)
    print("🧹 Local file deleted.")

horoscope_hashtags = [
    "Horoscope", "Astrology", "ZodiacSigns", "DailyHoroscope", "WeeklyHoroscope",
    "MonthlyHoroscope", "ZodiacReading", "AstrologyUpdate", "AstrologyForecast", "TarotAndAstrology",
    "AriesHoroscope", "TaurusHoroscope", "GeminiHoroscope", "CancerHoroscope",
    "LeoHoroscope", "VirgoHoroscope", "LibraHoroscope", "ScorpioHoroscope",
    "SagittariusHoroscope", "CapricornHoroscope", "AquariusHoroscope", "PiscesHoroscope",
    "ZodiacVibes", "DailyZodiac", "SpiritualGuidance", "Manifestation", "EnergyReading",
    "TodayInAstrology", "WhatTheStarsSay", "CelestialVibes", "AstroShorts", "ZodiacTalk",
    "UniverseMessages", "CosmicEnergy", "StarSigns", "ZodiacDaily", "AstroInsights",
    "SpiritualVibes", "MoonSigns", "PlanetaryInfluence", "MysticMessages", "AstroLife"
]

youtube_hashtags = random.sample(horoscope_hashtags, 10)

youtube_description_data = []
time_occurrences = [data_monthly, data_weekly, data_daily]

for dataset in time_occurrences:
    for item in dataset:
        youtube_description_data.append(f"{item['sign']}: {item['horoscope']}\n")

youtube_description = ''.join(youtube_description_data)[:4000]


for time_occurrence in time_occurrences:
    try:
        horoscope_time_group(time_occurrence)

        print(time_occurrence)
    except Exception as e:
        print(f"{time_occurrence} An error occurred: {e}")

# from google_auth_oauthlib.flow import InstalledAppFlow
#
# SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
#
# flow = InstalledAppFlow.from_client_secrets_file("client_secret_youtube.json", SCOPES)
# creds = flow.run_local_server(port=0)
#
# print("Access Token:", creds.token)
# print("Refresh Token:", creds.refresh_token)

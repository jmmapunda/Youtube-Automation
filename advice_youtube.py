import requests
import time
from datetime import datetime
from moviepy import *
import random
import os
import google.generativeai as genai
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from dotenv import load_dotenv

# load_dotenv()
NINJA_API_KEY = os.getenv('NINJA_API_KEY')
api_KEY_youtube = os.getenv('api_KEY_youtube')
client_id_youtube = os.getenv('client_id_youtube')
client_secret_youtube = os.getenv('client_secret_youtube')
YOUTUBE_REFRESH_TOKEN = os.getenv('YOUTUBE_REFRESH_TOKEN')
AI_KEY = os.getenv('AI_KEY')

today = datetime.now()
day_of_year = today.timetuple().tm_yday

hashtags = [
    "MangaAI", "AnimeArt", "AestheticAnime", "AIAnime", "AnimeVibes", "OtakuLife", "AnimeLovers", "MangaArt",
    "AnimeEdits", "AnimeOverlay", "AIArtworks", "DailyAdvice", "LifeTips", "AnimeQuotes", "InspoOverlay",
    "MotivationAnime", "AIGenerated", "Shorts", "YouTubeShorts", "AnimeShorts", "ArtInspo", "DigitalDreams",
    "StayInspired", "OtakuQuotes", "VisualWisdom", "AIVisuals", "MangaMood", "ASMR", "YOUTUBE", "Labubu"
    ]
advice_hashtags = random.sample(hashtags, 10)


advice = 'https://api.api-ninjas.com/v1/advice'
response = requests.get(advice, headers={'X-Api-Key': NINJA_API_KEY})
if response.status_code == requests.codes.ok:
    print(response.json()['advice'])
today_advice = response.json()['advice']
print(today_advice)

from moviepy import *

one_line = 28
lines = len(response.json()['advice']) // one_line + 2
text_height = 70 * lines

# Create black background clip (1080x1920)
background = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=10)

advice_image = random.choice(range(1, 18))
print(f"Image used is anime_{advice_image}.jpg")


# Load and resize the image to fit bottom 1720 height
image = (ImageClip(f"static/assets/pictures/anime_{advice_image}.jpg").resized(height=1920 - text_height)
         .with_position(("center", "bottom"))
         .with_duration(10))
# image = image.cropped(height=1720)  # Force height to 1720 if needed

# Create a text clip
text = TextClip(text=f"{response.json()['advice']}", font_size=70, text_align="center",
                font="static/assets/font/Newsreader-VariableFont_opsz,wght.ttf", color="white", size=(940, text_height),
                method="caption").with_duration(10).with_position(("center", 20))

# Optional: add background audio
facts_audio = random.choice(range(1, 4))
print(f"Audio used is audio_{facts_audio}.mp3")


audio = AudioFileClip(f"static/assets/audio/audio_{facts_audio}.mp3").with_duration(10)

# Composite final video
final = CompositeVideoClip([background, image, text])
final = final.with_audio(audio)
# Export the video
final.write_videofile("youtube_advice.mp4", fps=24)

# YouTube uploads start
# url_youtube = 'https://www.googleapis.com/youtube/v3'
# response = requests.get(url_youtube, api_KEY_youtube)
# print(response)



genai.configure(api_key=f"{AI_KEY}")

model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content(
    f"Create a YouTube title just one line based on this advice include emoji if possible '{today_advice}'")
print(f'AI summary is: {response.text}')
advice_title = response.text

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

# Upload to YouTube
def upload_video(file_path, title, description, youtube_hashtags):
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

# ✅ Upload final video to YouTube
local_path = "youtube_advice.mp4"
print("Uploading started...")

try:
    upload_video(file_path=local_path, title=f'{advice_title} #shorts', description="",
                 youtube_hashtags=advice_hashtags)
    print("Uploaded video successfully.")
# except Exception as e:
#     print(f"Failed to upload video: {e}")
finally:
    if os.path.exists(local_path):
        try:
            os.remove(local_path)
            print("Cleaned up local video file.")
        except Exception as cleanup_error:
            print(f"Failed to delete local video file: {cleanup_error}")


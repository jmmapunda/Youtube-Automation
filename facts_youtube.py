import requests
import time
from datetime import datetime
from moviepy import *
import random
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from dotenv import load_dotenv

# load_dotenv()
api_KEY_youtube = os.getenv('api_KEY_youtube')
client_id_youtube = os.getenv('client_id_youtube')
client_secret_youtube = os.getenv('client_secret_youtube')
YOUTUBE_REFRESH_TOKEN = os.getenv('YOUTUBE_REFRESH_TOKEN')

URL = 'https://uselessfacts.jsph.pl/random.json?language=en' # .json()['text']
URL_2 = 'http://numbersapi.com/random/trivia' # .text

today = datetime.now()
day_of_year = today.timetuple().tm_yday


results = requests.get(URL).json()['text']
results_2 = requests.get(URL_2).text
facts_description = random.choice([results, results_2])


closing_texts = [
    "Subscribe for more daily facts!",
    "Liked the video? More coming tomorrow \ndon’t forget to subscribe!",
    "Come back tomorrow for your next fact!\nSubscribe",
    "One fact a day keeps boredom away\nSubscribe!",
    "Hit like if you learned something new!",
    "Share this with a friend who loves facts!",
    "Comment your favorite fact below!",
    "New facts every day \ndon’t miss out!\nSubscribe",
    "That’s it for today \nsee you tomorrow with another surprise!\nSubscribe",
    "This was just the beginning \nsubscribe for more!",
    "Fuel your brain daily \nhit that subscribe button!",
    "A fact a day makes you wiser \nsubscribe now!",
    "Join our fact family \nhit subscribe!",
    "Want more mind-blowing facts? You know what to do!\nSubscribe",
    "Don’t miss a day \nturn on notifications!",
    "More facts, more fun \nsee you next time!",
    "The learning never stops \nsubscribe and stay curious!",
    "Thanks for watching! Subscribe for tomorrow’s fact!",
    "Let’s make learning a habit \nsubscribe today!",
    "Knowledge is power \nsubscribe and get yours daily!",
]
closing_text = random.choice(closing_texts)

hashtags = [
    "DailyFacts",
    "FunFact",
    "DidYouKnow",
    "FactOfTheDay",
    "LearnSomethingNew",
    "RandomFacts",
    "InterestingFacts",
    "MindBlown",
    "Shorts",
    "YouTubeShorts",
    "KnowledgeIsPower",
    "StayCurious",
    "FactShorts",
    "QuickFacts",
    "TriviaTime",
    "FactLovers",
    "EducationInSeconds",
    "BrainBoost",
    "FactAddict",
    "SmartFacts"
]
facts_hashtags = random.sample(hashtags, 10)

video = VideoFileClip("static/assets/video/video_1.mp4")
video_width, video_height = video.size

text_width = video_width - 140  # 70px left and right padding

# Text 1 at 0s to 3s
txt1 = (TextClip(font="static/assets/font/Newsreader_60pt-Bold.ttf", text=f"Welcome\nDay {day_of_year} Daily Facts!",
                 text_align='center', font_size=250, color='#193C40', size=(text_width, None), method='caption', )
        .with_position("center", 0.1)
        .with_duration(3)
        .with_start(0))

# Text 2 at 3s to 6s
txt2 = (TextClip(font="static/assets/font/Newsreader-VariableFont_opsz,wght.ttf", text=f"{results}", font_size=130,
                 text_align='center', color='#F2E7DC', size=(text_width, None), method='caption', )
        .with_position("center")
        .with_duration(3)
        .with_start(3))

txt3 = (TextClip(font="static/assets/font/Newsreader-VariableFont_opsz,wght.ttf", text=f"{results_2}", font_size=130,
                 text_align='center', color='#F2E7DC', size=(text_width, None), method='caption', )
        .with_position("center")
        .with_duration(3)
        .with_start(6))

txt4 = (TextClip(font="static/assets/font/Newsreader-VariableFont_opsz,wght.ttf", text=f"{closing_text}", font_size=130,
                 text_align='center', color='#F2E7DC', size=(text_width, None), method='caption', )
        .with_position("center")
        .with_duration(3)
        .with_start(9))
# Optional: add background audio
audio = AudioFileClip("static/assets/audio/audio_1.mp3").with_duration(video.duration)

final = CompositeVideoClip([video, txt1, txt2, txt3, txt4])
final = final.with_audio(audio)

final.write_videofile("youtube_facts.mp4", fps=24)


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
local_path = "youtube_facts.mp4"
print("Uploading started...")

try:
    upload_video(file_path=local_path, title=f'Day {day_of_year} Daily Facts!', description=facts_description,
                 youtube_hashtags=facts_hashtags)
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

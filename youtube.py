import requests
import random
from moviepy import *
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
import google.generativeai as genai


# load_dotenv()
PEXELKEY = os.getenv('PEXELKEY')
cloudname = os.getenv('cloudname')
APIKEY = os.getenv('APIKEY')
APISECRET = os.getenv('APISECRET')
api_KEY_youtube = os.getenv('api_KEY_youtube')
client_id_youtube = os.getenv('client_id_youtube')
client_secret_youtube = os.getenv('client_secret_youtube')
YOUTUBE_REFRESH_TOKEN = os.getenv('YOUTUBE_REFRESH_TOKEN')
AI_KEY = os.getenv('AI_KEY')

# print("refresh_token:", YOUTUBE_REFRESH_TOKEN[:5] + "..." if YOUTUBE_REFRESH_TOKEN else "MISSING")
# print("client_id:", client_id_youtube[:5] + "..." if client_id_youtube else "MISSING")
# print("client_secret:", client_secret_youtube[:5] + "..." if client_secret_youtube else "MISSING")

def horoscope(time, data, sn=1):
    response = requests.get(time).json()
    data.append({
        "sign": sign,
        "horoscope": response['data']['horoscope_data'],
        'sn': sn
        })

today = datetime.now()
today_date = datetime.now().strftime('%B %d, %Y')
current_year = datetime.now().year
day_of_year = today.timetuple().tm_yday
current_month = today.strftime('%B')


horoscope_signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius",
                   "Capricorn", "Aquarius", "Pisces"]
closing_texts = [
    "Thanks for watching! Come back tomorrow for your next horoscope 🌟",
    "Enjoyed your reading? Subscribe for daily cosmic insights ✨",
    "One horoscope a day keeps uncertainty away 🔮 Subscribe now!",
    "The stars never sleep, and neither do we 🌙 Subscribe for more!",
    "Tomorrow’s destiny awaits... don’t miss it 🔭 Subscribe!",
    "Hit like if the stars spoke to you today ⭐",
    "Know someone who loves astrology? Share this with them 🌌",
    "Join our cosmic community — subscribe for daily horoscopes 💫",
    "The universe has more in store for you… come back tomorrow 🌠",
    "Feeling aligned? Make it a daily ritual 🔁 Subscribe now!",
    "Let the stars guide you daily ✨ Hit that subscribe button!",
    "Your next forecast is just a sunrise away ☀️ Don’t miss it!",
    "More astrology, more insight 🔮 Subscribe and stay tuned!",
    "Unlock the mysteries of the universe daily — subscribe now 🌌",
    "Stay in sync with the cosmos 🪐 New horoscope every day!",
    "Let your zodiac lead the way — subscribe for tomorrow’s reading!",
    "Thanks for your energy today 💖 See you tomorrow under new stars!",
    "Don’t miss a sign from the stars — turn on notifications 🔔",
    "Your future self will thank you — subscribe for daily guidance 💫",
    ]

closing_text = random.choice(closing_texts)

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
youtube_horoscope_hashtags = random.sample(horoscope_hashtags, 10)

disclaimer_copyright = (
    "\n\n📌Disclaimer & Copyright Notice\nAll horoscope and information presented in this video are intended "
    "for educational and informational purposes only. While every effort has been made to ensure "
    "accuracy, we do not guarantee the completeness or reliability of any horoscope. Viewers are "
    f"encouraged to verify content independently.\n\n📌Copyright © {current_year} John "
    "Mapunda\nAll rights reserved. This video and its contents, including audio, visuals, "
    "and branding, are the intellectual property of John Mapunda and may not be reproduced, "
    "redistributed, or reused without express permission.\n\n\nVisit:🌐 https://johnmapunda.com for "
    "more content and resources.")

horoscope_description = ("🌟 Welcome to Your Daily Dose of Cosmic Insight! 🌟\n\nUnlock the mysteries of the stars "
                         "with today’s horoscope readings for all zodiac signs. Whether you're looking for clarity, "
                         "motivation, or a sign from the universe — we've got your back!\n\n✨ What to Expect in This "
                         "Video:\n✔️ Accurate daily, weekly, or monthly horoscopes\n✔️ Guidance for love, career, "
                         "health, and more\n✔️ Personalized astrology insights for every zodiac sign\n\n📅 Horoscope "
                         f"Date: {today_date}\n\n🔔 Subscribe & Turn on Notifications to never miss your "
                         "daily insight!") + disclaimer_copyright

data_daily = []
data_weekly = []
data_monthly = []



#RANDOMIZATION COMPONENTS
tones = ["mystical", "urgent", "romantic", "career-focused", "uplifting", "mysterious"]
emojis = ["🔮", "✨", "🌟", "🌌", "♈♉♊", "🔥", "🌠", "🪐", "📅"]
selected_tone = random.choice(tones)
selected_emojis = random.sample(emojis, 2)

#DATE INFO
today_date = datetime.now().strftime('%B %d, %Y')
# current_month = datetime.now().strftime('%B')
current_week = datetime.now().isocalendar().week

#VIDEO TYPE: 'daily', 'weekly', or 'monthly'
if datetime.now().day == 1:
    video_type = "monthly"  # ← set this dynamically based on logic
elif datetime.now().weekday() == 0:
    video_type = "weekly"  # ← set this dynamically based on logic
else:
    video_type = "daily"

#Generate context based on video type
if video_type == "daily":
    base_title = f"Daily horoscope for {today_date}"
    style_note = "short-term cosmic insights, fresh energy"
elif video_type == "weekly":
    base_title = f"Weekly horoscope for Week {current_week}, {today_date}"
    style_note = "weekly zodiac forecast, opportunities & challenges"
elif video_type == "monthly":
    base_title = f"Monthly horoscope for {current_month} {datetime.now().year}"
    style_note = "monthly guidance, deep astrology insights"

prompt = f"""
You're a YouTube SEO expert and creative title writer.
Generate ONE highly engaging, click-worthy YouTube title (one line only) for a {video_type} horoscope video based on this:

🪐 Content: "{base_title}"
🎯 Style: {style_note}
🎭 Tone: {selected_tone}
🎉 Emojis: {' '.join(selected_emojis)}

✅ Must be under 100 characters
✅ Include SEO keywords like: 'horoscope', 'astrology', 'zodiac', '{video_type} prediction', etc.
✅ Avoid repeating phrases from previous days/weeks/months
✅ Add curiosity or urgency when appropriate

Examples:
- "This Week’s Astrology Forecast 🔮 What Awaits Your Sign? (Week {current_week})"
- "August 2025 Horoscope 🌟 Monthly Insights for All Zodiac Signs"
- "Today’s Horoscope Revealed ✨ What the Stars Say for {today_date}"

Now generate the title:
"""

#Gemini API
genai.configure(api_key=AI_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content(prompt)
youtube_title = response.text.strip()

print(f"Generated {video_type.capitalize()} Title: {youtube_title}")

for sign in horoscope_signs:
    horoscope_daily = f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily?sign={sign}&day=TODAY"
    horoscope_weekly = f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/weekly?sign={sign}"
    horoscope_monthly = f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/monthly?sign={sign}"
    sn = 1
    if datetime.now().day == 1:
        horoscope(horoscope_monthly, data_monthly)
        # youtube_title = f'Month of {current_month} Horoscope - {today_date}'
        sn += 1

    elif datetime.now().weekday() == 0:
        horoscope(horoscope_weekly, data_weekly)
        # youtube_title = f"This Week's Horoscope - {today_date}"
        sn += 1

    else:
        horoscope(horoscope_daily, data_daily)
        # youtube_title = f"Today's {today_date} Horoscope"
        sn += 1


horoscope_data = [data_daily, data_weekly, data_monthly]

horoscope_video = random.choice(range(1, 10))
print(f"Video used is horoscope_{horoscope_video}.mp4")
video_time = 123

video_to_use = VideoFileClip(f"static/assets/video/horoscope_{horoscope_video}.mp4")
video_duration = video_to_use.duration
multiple_by = 1
if video_duration < video_time:
    multiple_by = int(video_time // video_duration + 1)
    print(multiple_by)
video = (video_to_use * multiple_by).subclipped(0, video_time)
video_width, video_height = video.size
if datetime.now().day == 1:
    video_resized = video.resized(height=1080)
    video_final = video_resized.cropped(width=1920, x_center=video_resized.w / 2)
    text_width = 1780  # 70px left and right padding
    font_size = 43
elif datetime.now().weekday() == 0:
    video_resized = video.resized(height=1080)
    video_final = video_resized.cropped(width=1920, x_center=video_resized.w / 2)
    text_width = 1780  # 70px left and right padding
    font_size = 50

else:
    video_resized = video.resized(height=1920)
    video_final = video_resized.cropped(width=1080, x_center=video_resized.w / 2)
    text_width = 940  # 70px left and right padding
    font_size = 100


# Text 1 at 0s to 3s
txt_start = (
    TextClip(font="static/assets/font/Newsreader_60pt-Bold.ttf", text=f"Welcome\nDay {day_of_year} Daily horoscope!",
             text_align='center', font_size=190, color='#D5F2ED', stroke_color="#BF0000", stroke_width=3,
             size=(text_width, None), method='caption', )
    .with_position("center", 0.1)
    .with_duration(3)
    .with_start(0))
start_time = 3
clips = []
for horo_time_range in horoscope_data:
    if horo_time_range:
        for horoscope_details in horo_time_range:
            horoscope_details['sign'] = (
                TextClip(font="static/assets/font/Newsreader-VariableFont_opsz,wght.ttf",
                         text=f"{horoscope_details['sign']}", font_size=120, text_align='center', color='yellow',
                         stroke_color="#BF0000", stroke_width=2, size=(text_width, None), method='caption', )
                .with_position(('center', 60))
                .with_duration(10)
                .with_start(start_time))
            horoscope_details['sn'] = (
                TextClip(font="static/assets/font/Newsreader-VariableFont_opsz,wght.ttf",
                         text=f"{horoscope_details['horoscope']}", font_size=font_size, text_align='center',
                         color='#C4EEF2',
                         stroke_color="#BF0000", stroke_width=2, size=(text_width, None), method='caption', )
                .with_position("center")
                .with_duration(10)
                .with_start(start_time))
            start_time += 10
            clips.append(horoscope_details['sign'])
            clips.append(horoscope_details['sn'])

txt_last = (
    TextClip(font="static/assets/font/Newsreader-VariableFont_opsz,wght.ttf", text=f"{closing_text}", font_size=130,
             text_align='center', color='#FFFFFF', stroke_color="#E50000", stroke_width=2, size=(text_width, None),
             method='caption', )
    .with_position("center")
    .with_duration(3)
    .with_start(123))
# Optional: add background audio
horoscope_audio = random.choice(range(1, 4))
print(f"Audio used is audio_{horoscope_audio}.mp3")

audio = AudioFileClip(f"static/assets/audio/audio_{horoscope_audio}.mp3").subclipped(0, 20)
repeats = int(video.duration // 20) + 1
audio_looped = concatenate_audioclips([audio] * repeats).subclipped(0, video.duration)
audio = CompositeAudioClip([audio_looped])

final = CompositeVideoClip([video_final, txt_start, *clips, txt_last])
final = final.with_audio(audio)

final.write_videofile("youtube_horoscope.mp4", fps=24, threads=8)

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
def upload_video(file_path, title, thumbnail, description, youtube_hashtags):
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
    video_id = response['id']
    print(f"✅ Video uploaded: https://www.youtube.com/watch?v={video_id}")
    thumbnail_request = youtube.thumbnails().set(
        videoId=video_id,
        media_body=thumbnail
        )
    thumbnail_response = thumbnail_request.execute()

    # Cleanup local file
    os.remove(file_path)
    print("🧹 Local file deleted.")

# ✅ Upload final video to YouTube
local_path = "youtube_horoscope.mp4"
thumbnail_path = "thumbnail.jpg"
print("Uploading started...")

video = VideoFileClip("youtube_horoscope.mp4")
thumbnail_time = 2  # second mark to grab the frame
frame = video.get_frame(thumbnail_time)  # Numpy array
video.close()

from PIL import Image
import numpy as np

thumbnail_img = Image.fromarray(np.uint8(frame))
thumbnail_img.save(thumbnail_path)


try:
    upload_video(file_path=local_path, thumbnail=thumbnail_path, title=youtube_title, description=horoscope_description,
                 youtube_hashtags=youtube_horoscope_hashtags)
    print("Uploaded video successfully.")
# except Exception as e:
#     print(f"Failed to upload video: {e}")
finally:
    if os.path.exists(local_path):
        try:
            os.remove(thumbnail_path)
            os.remove(local_path)
            print("Cleaned up local video file.")
        except Exception as cleanup_error:
            print(f"Failed to delete local video file: {cleanup_error}")
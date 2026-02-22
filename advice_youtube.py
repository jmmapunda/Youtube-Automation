import requests
import time
from datetime import datetime
from moviepy import *
import random
import os
import google.generativeai as genai
from twilio.rest import Client
from dotenv import load_dotenv
from gtts import gTTS
from automation import YouTube, TextToSpeech

start_time = time.time()
# load_dotenv()
NINJA_API_KEY = os.getenv('NINJA_API_KEY')
api_KEY_youtube = os.getenv('api_KEY_youtube')
AI_KEY = os.getenv('AI_KEY')
twilio_account_sid = os.getenv('twilio_account_sid')
twilio_auth_token = os.getenv('twilio_auth_token')
my_number = os.getenv('my_number')
client_id_youtube = os.getenv('client_id_youtube')
client_secret_youtube = os.getenv('client_secret_youtube')
YOUTUBE_REFRESH_TOKEN = os.getenv('YOUTUBE_REFRESH_TOKEN')

today = datetime.now()
day_of_year = today.timetuple().tm_yday

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

print(today.month)
if today.month == 12:
    advice_image = random.choice(range(1, 25))
    print(f"Image used is anime_{advice_image}.jpg")
    image = (ImageClip(f"https://johnmapunda.com/static/assets/image/chrismass/chrismass_{advice_image}.jpg").resized(height=1920 - text_height)
             .with_position(("center", "bottom"))
             .with_duration(10))
else:
    advice_image = random.choice(range(1, 18))
    image = (ImageClip(f"static/assets/pictures/anime_{advice_image}.jpg").resized(height=1920 - text_height)
             .with_position(("center", "bottom"))
             .with_duration(10))

# Create a text clip
text = TextClip(text=f"{response.json()['advice']}", font_size=70, text_align="center",
                font="static/assets/font/Newsreader-VariableFont_opsz,wght.ttf", color="white", size=(940, text_height),
                method="caption").with_duration(10).with_position(("center", 20))

# Optional: add background audio
tts = gTTS(f'{today_advice}', lang="en", slow=False)
tts.save("advice_audio.mp3")

facts_audio = random.choice(range(1, 4))

try:
    google_tts = TextToSpeech(text=today_advice)
    google_tts.google_tts()
    audio = AudioFileClip(f'advice_audio.mp3')
except Exception as e:
    print('Google TTS Failed', e)
    try:
        gtts_audio = TextToSpeech(text=today_advice)
        gtts_audio.gtts()
        audio = AudioFileClip(f'advice_audio.mp3')
    except Exception as e:
        print('gTTS Failed', e)
        audio = AudioFileClip(f"static/assets/audio/audio_{facts_audio}.mp3").with_duration(10)
        print(f"Audio used is audio_{facts_audio}.mp3")


# Composite final video
final = CompositeVideoClip([background, image, text])
final = final.with_audio(audio)
# Export the video
final.write_videofile("youtube_advice.mp4", fps=24)

genai.configure(api_key=f"{AI_KEY}")

model = genai.GenerativeModel("gemini-2.5-flash")

for i in range(10):
    print(f"Adive Title Attempt: {i + 1}")
    response = model.generate_content(
        f'Generate exactly ONE YouTube title based on the advice: {today_advice}. Rules:'
        f'- The title MUST be 80 characters or fewer'
        f'- Natural, engaging, SEO-friendly, click-worthy'
        f'- Include 1–2 relevant hashtags at the end'
        f'- NO emojis, NO symbols'
        f'- Return ONLY the title text'
        f'- Do NOT add explanations, quotes, options, or extra words'
        )

    if len(response.text) < 80:
        print(f'AI summary is: {response.text}')
        break
    else:
        print(f"Failed: {len(response.text)} - {response.text}")

advice_title = response.text
print(advice_title)
# Set YouTube upload scope
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Upload final video to YouTube
local_path = "youtube_advice.mp4"
print("Uploading started...")

authenticate_youtube = YouTube.authenticate_youtube(
    client_id_youtube=client_id_youtube,
    client_secret_youtube=client_secret_youtube,
    YOUTUBE_REFRESH_TOKEN=YOUTUBE_REFRESH_TOKEN)

try:
    YouTube.upload_video(
        file_path=local_path,
        title=f'{advice_title} #shorts',
        description='',
        youtube_hashtags='',
        thumbnail='',
        authenticate_youtube=authenticate_youtube
        )
except Exception as e:
    print(f"Failed to upload video: {e}")
finally:
    if os.path.exists(local_path):
        try:
            os.remove(local_path)
            print("Cleaned up local video file.")
        except Exception as cleanup_error:
            print(f"Failed to delete local video file: {cleanup_error}")


# Send message to my whatsapp
client = Client(twilio_account_sid, twilio_auth_token)

try:
    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body=f'Advice: {today_advice}\nAI Summary/Title: {advice_title}!',
        to=f'whatsapp:{my_number}'
        )
    print(message.sid)
except Exception as whatsapp:
    print(f'Failed to send to Whatsapp error: {whatsapp}')

finish_time = time.time()
print(f"Finished in {round(finish_time - start_time, 2)} seconds.")

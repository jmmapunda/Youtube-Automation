import requests
import time
from datetime import datetime
from moviepy import *
import random
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import google.generativeai as genai
import pandas as pd
from automation import TextToSpeech, YouTube


start_time = time.time()
# load_dotenv()
api_KEY_youtube = os.getenv('api_KEY_youtube')
client_id_youtube = os.getenv('client_id_youtube')
client_secret_youtube = os.getenv('client_secret_youtube')
YOUTUBE_REFRESH_TOKEN = os.getenv('YOUTUBE_REFRESH_TOKEN')
NINJA_API_KEY = os.getenv('NINJA_API_KEY')

AI_KEY = os.getenv('AI_KEY')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
print("✅ Supabase connection established.")

URL = 'https://uselessfacts.jsph.pl/random.json?language=en'  # .json()['text']
URL_2 = 'http://numbersapi.com/random/trivia'  # .text
URL_3 = 'https://api.api-ninjas.com/v1/facts'  # .[0]['fact'] from API NINJA

today = datetime.now()
day_of_year = today.timetuple().tm_yday
current_year = today.year

MAX_RETRIES = 1
retry_delay = 10  # seconds
facts = []

for attempt in range(MAX_RETRIES):
    try:
        results = requests.get(URL).json()['text']
        facts.append((results, 'Useless Facts'))

    except Exception as e:
        results = None
        print(f"Attempt {attempt + 1} failed: {e}")
        if attempt < MAX_RETRIES - 1:
            time.sleep(retry_delay)
    try:
        results_2 = requests.get(URL_2).text
        facts.append((results_2, 'Numbers API'))

    except Exception as e:
        results_2 = None
        print(f"Attempt {attempt + 1} failed: {e}")
        if attempt < MAX_RETRIES - 1:
            time.sleep(retry_delay)
    try:
        results_3 = requests.get(URL_3, headers={'X-Api-Key': NINJA_API_KEY}).json()[0]['fact']
        facts.append((results_3, 'Ninja API'))
    except Exception as e:
        results_3 = None
        print(f"Attempt {attempt + 1} failed: {e}")
        if attempt < MAX_RETRIES - 1:
            time.sleep(retry_delay)

def save_facts(facts):
    rows = [{"Fact": fact, "Source": source} for fact, source in facts]
    supabase.table("facts").insert(rows).execute()
    print(f"🆕 Inserted {len(rows)} facts into Supabase.")

allfacts = supabase.table('facts').select('Fact').execute()
factsresults = allfacts.data
randomfact = random.choice(factsresults)

if results is None:
    results = randomfact['Fact']
if results_2 is None:
    results_2 = randomfact['Fact']
if results_3 is None:
    results_3 = randomfact['Fact']

save_facts(facts)

print(f'Results 1: {results}')
print(f'Results 2: {results_2}')
print(f'Results 3:{results_3}')
facts_description = random.choice([results, results_2, results_3])
today_facts = f"'{results}', '{results_2}', '{results_3}'"

genai.configure(api_key=f"{AI_KEY}")

model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content(
    f'Create one catchy, SEO-optimized YouTube title (max 80 characters) for a facts video based on these facts: {today_facts}.'
    f'The title should: '
    f'Be exciting, curiosity-driven, and natural (not clickbait).'
    f'Include relevant keywords like “Amazing Facts”, “Did You Know”, “Unbelievable”, “Mind-Blowing”, etc.'
    f'Combine or summarize the three facts into one engaging idea.'
    f'Be written in title case (each major word capitalized).'
    f'Two relevant hashtags'
    f'Output only the final title.')

print(f'AI summary is: {response.text}')
facts_title = response.text

closing_texts = [
    "Subscribe for more daily facts!", "Liked the video? More coming tomorrow \ndon’t forget to subscribe!",
    "Come back tomorrow for your next fact!\nSubscribe", "One fact a day keeps boredom away\nSubscribe!",
    "Hit like if you learned something new!", "Share this with a friend who loves facts!",
    "Comment your favorite fact below!", "New facts every day \ndon’t miss out!\nSubscribe",
    "That’s it for today \nsee you tomorrow with another surprise!\nSubscribe",
    "This was just the beginning \nsubscribe for more!", "Fuel your brain daily \nhit that subscribe button!",
    "A fact a day makes you wiser \nsubscribe now!", "Join our fact family \nhit subscribe!",
    "Want more mind-blowing facts? You know what to do!\nSubscribe", "Don’t miss a day \nturn on notifications!",
    "More facts, more fun \nsee you next time!", "The learning never stops \nsubscribe and stay curious!",
    "Thanks for watching! Subscribe for tomorrow’s fact!", "Let’s make learning a habit \nsubscribe today!",
    "Knowledge is power \nsubscribe and get yours daily!",
    ]
closing_text = random.choice(closing_texts)

# Video overlay start
facts_video = random.choice(range(1, 8))
print(f"Video used is facts_{facts_video}.mp4")
video_time = 18

video_to_use = VideoFileClip(f"static/assets/video/facts_{facts_video}.mp4")
video_duration = video_to_use.duration
multiple_by = 1
if video_duration < video_time:
    multiple_by = video_time // video_duration + 1
video = (video_to_use * multiple_by).subclipped(0, video_time)
video_width, video_height = video.size
video_resized = video.resized(height=1920)
video_final = video_resized.cropped(width=1080, x_center=video_resized.w / 2)

text_width = 940  # 70px left and right padding

txt2 = (TextClip(font="static/assets/font/Newsreader-VariableFont_opsz,wght.ttf", text=f"{results}", font_size=100,
                 text_align='center', color='#C4EEF2', stroke_color="#BF0000", stroke_width=2, size=(text_width, None),
                 method='caption', )
        .with_position("center")
        .with_duration(5)
        .with_start(0))

txt3 = (TextClip(font="static/assets/font/Newsreader-VariableFont_opsz,wght.ttf", text=f"{results_2}", font_size=100,
                 text_align='center', color='#C4EEF2', stroke_color="#BF0000", stroke_width=2, size=(text_width, None),
                 method='caption', )
        .with_position("center")
        .with_duration(5)
        .with_start(5))

txt4 = (TextClip(font="static/assets/font/Newsreader-VariableFont_opsz,wght.ttf", text=f"{results_3}", font_size=100,
                 text_align='center', color='#C4EEF2', stroke_color="#BF0000", stroke_width=2, size=(text_width, None),
                 method='caption', )
        .with_position("center")
        .with_duration(5)
        .with_start(10))

txt5 = (TextClip(font="static/assets/font/Newsreader-VariableFont_opsz,wght.ttf", text=f"{closing_text}", font_size=130,
                 text_align='center', color='#FFFFFF', stroke_color="#E50000", stroke_width=1, size=(text_width, None),
                 method='caption', )
        .with_position("center")
        .with_duration(3)
        .with_start(15))

# Optional: add background audio
facts_audio = random.choice(range(1, 4))
print(f"Audio used is audio_{facts_audio}.mp3")


audio = AudioFileClip(f"static/assets/audio/audio_{facts_audio}.mp3").with_duration(video.duration)

final = CompositeVideoClip([video_final, txt2, txt3, txt4, txt5])
final = final.with_audio(audio)

final.write_videofile("youtube_facts.mp4", fps=24)

# YouTube uploads start
url_youtube = 'https://www.googleapis.com/youtube/v3'
response = requests.get(url_youtube, api_KEY_youtube)
print(response)



# Set YouTube upload scope
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Upload final video to YouTube
local_path = "youtube_facts.mp4"
print("Uploading started...")

authenticate_youtube = YouTube.authenticate_youtube(
    client_id_youtube=client_id_youtube,
    client_secret_youtube=client_secret_youtube,
    YOUTUBE_REFRESH_TOKEN=YOUTUBE_REFRESH_TOKEN)

try:
    YouTube.upload_video(
        file_path=local_path,
        title=facts_title,
        description=facts_description,
        youtube_hashtags=None,
        thumbnail='',
        authenticate_youtube=authenticate_youtube
        )
    print("Uploaded video successfully.")
except Exception as e:
    print(f"Failed to upload video: {e}")
finally:
    if os.path.exists(local_path):
        try:
            os.remove(local_path)
            print("Cleaned up local video file.")
        except Exception as cleanup_error:
            print(f"Failed to delete local video file: {cleanup_error}")


all_facts = supabase.table('facts').select('*').execute()

df = pd.DataFrame(all_facts.data)
duplicates = df[df.duplicated(subset=['Fact'], keep="first")]
duplicates_list = duplicates['id'].to_list()
print(duplicates_list)

day_to_delete_duplicates = datetime.now().day
if day_to_delete_duplicates == 1:

    try:
        if duplicates_list:
            supabase.table('facts').delete().in_(column='id', values=duplicates_list).execute()
            print(f'Deleted {len(duplicates_list)} duplicates.')
        else:
            print('No Data to Delete.')
    except Exception as e:
        print('Error Deleting Duplicates', e)
else:
    print('Not day Uno, so we are not deleting duplicates.')

finish_time = time.time()
print(f"Finished in {round(finish_time - start_time, 2)} seconds.")
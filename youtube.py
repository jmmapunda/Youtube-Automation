import requests
import random
from dotenv import load_dotenv
from moviepy import *
from datetime import datetime
import os
import time
from automation import YouTube, AI
from supabase import create_client, Client
from PIL import ImageFont, ImageDraw, Image
import numpy as np


start_time = time.time()
# load_dotenv()
PEXELKEY = os.getenv('PEXELKEY')
cloudname = os.getenv('cloudname')
APIKEY = os.getenv('APIKEY')
APISECRET = os.getenv('APISECRET')
api_KEY_youtube = os.getenv('api_KEY_youtube')
AI_KEY = os.getenv('AI_KEY')
client_id_youtube = os.getenv('client_id_youtube')
client_secret_youtube = os.getenv('client_secret_youtube')
YOUTUBE_REFRESH_TOKEN = os.getenv('YOUTUBE_REFRESH_TOKEN')

supabase_url = os.getenv("SUPABASE_URL")
supabase_srkey = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(supabase_url, supabase_srkey)

def horoscope(time, data, sn=1):
    try:
        response = requests.get(time).json()
        data.append({
            "sign": sign,
            "horoscope": response['data']['horoscope'],
            'sn': sn
            })
    except Exception as e:
        print('API Failed to captured horoscope', e)
        exit()

today = datetime.now()
today_date = datetime.now().strftime('%B %d, %Y')
current_year = datetime.now().year
day_of_year = today.timetuple().tm_yday
current_month = today.strftime('%B')

horoscope_signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius",
                   "Capricorn", "Aquarius", "Pisces"]
closing_texts = [
    "Thanks for watching! Come back tomorrow for your next horoscope",
    "Enjoyed your reading? Subscribe for daily cosmic insights",
    "One horoscope a day keeps uncertainty away Subscribe now!",
    "The stars never sleep, and neither do we Subscribe for more!",
    "Tomorrow’s destiny awaits... don’t miss it Subscribe!",
    "Hit like if the stars spoke to you today",
    "Know someone who loves astrology? Share this with them",
    "Join our cosmic community — subscribe for daily horoscopes",
    "The universe has more in store for you… come back tomorrow",
    "Feeling aligned? Make it a daily ritual Subscribe now!",
    "Let the stars guide you daily Hit that subscribe button!",
    "Your next forecast is just a sunrise away Don’t miss it!",
    "More astrology, more insight Subscribe and stay tuned!",
    "Unlock the mysteries of the universe daily — subscribe now",
    "Stay in sync with the cosmos New horoscope every day!",
    "Let your zodiac lead the way — subscribe for tomorrow’s reading!",
    "Thanks for your energy today See you tomorrow under new stars!",
    "Don’t miss a sign from the stars — turn on notifications",
    "Your future self will thank you — subscribe for daily guidance",
    ]

closing_text = random.choice(closing_texts)

data_daily = []
data_weekly = []
data_monthly = []


#RANDOMIZATION COMPONENTS
tones = ["mystical", "urgent", "romantic", "career-focused", "uplifting", "mysterious"]
selected_tone = random.choice(tones)

#DATE INFO
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

Content: "{base_title}"
Style: {style_note}
Tone: {selected_tone}

- Must be under 100 characters
- Include SEO keywords like: 'horoscope', 'astrology', 'zodiac', '{video_type} prediction', etc.
- Avoid repeating phrases from previous days/weeks/months
- Add curiosity or urgency when appropriate

Examples:
- "This Week’s Astrology Forecast What Awaits Your Sign? (Week {current_week})"
- "August 2025 Horoscope Monthly Insights for All Zodiac Signs"
- "Today’s Horoscope Revealed What the Stars Say for {today_date}"

Now generate the title:
"""
ai_title = AI(prompt)
response = ai_title.ai_summary()
youtube_title = response.strip()

print(f"Generated {video_type.capitalize()} Title: {youtube_title}")
day_today = datetime.now().strftime('%B %d')
week_today = datetime.now().isocalendar().week
month_today = datetime.now().month


def save_horoscope_data(time_supabase, time, date, data_horoscope):
    try:
        supabase.table(time).insert(
            {time_supabase: date, 'sign': sign, 'horoscope': data_horoscope}).execute()
    except Exception as e:
        print('Failed to insert and save horoscope data', e)


for sign in horoscope_signs:
    horoscope_daily = f"https://freehoroscopeapi.com/api/v1/get-horoscope/daily?sign={sign}"
    horoscope_weekly = f"https://freehoroscopeapi.com/api/v1/get-horoscope/weekly?sign={sign}"
    horoscope_monthly = f"https://freehoroscopeapi.com/api/v1/get-horoscope/monthly?sign={sign}"
    sn = 1

    daily_horoscope_data = requests.get(horoscope_daily).json()['data']['horoscope']
    weekly_horoscope_data = requests.get(horoscope_weekly).json()['data']['horoscope']
    monthly_horoscope_data = requests.get(horoscope_monthly).json()['data']['horoscope']
    save_horoscope_data(time_supabase='date', time='horoscope_day', date=day_today, data_horoscope=daily_horoscope_data)
    save_horoscope_data(time_supabase='week', time='horoscope_week', date=week_today, data_horoscope=weekly_horoscope_data)
    save_horoscope_data(time_supabase='month', time='horoscope_month', date=month_today, data_horoscope=monthly_horoscope_data)

    if datetime.now().day == 1:
        horoscope(horoscope_monthly, data_monthly)
        sn += 1

    elif datetime.now().weekday() == 0:
        horoscope(horoscope_weekly, data_weekly)
        sn += 1

    else:
        horoscope(horoscope_daily, data_daily)
        sn += 1


horoscope_data = [data_daily, data_weekly, data_monthly]


prompt_youtube_description = f"""
Write a YouTube video description for a horoscope video. 

Requirements:
1. Include a short summary of all horoscope signs using the provided {horoscope_data}.
2. Make it short, clear, and easy to read (max 5000 characters).
3. Include strong keywords and clickbait phrases like "must watch," "today's horoscope," "life-changing predictions," "your future revealed."
4. Add relevant hashtags like #horoscope, #astrology, #dailyhoroscope, #zodiac, #horoscopesigns.
5. Do NOT use emojis or symbols.
6. Write in a friendly, engaging style that encourages viewers to watch the video.

Here is the horoscope data: {horoscope_data}

Generate the description only.
"""
ai_description = AI(prompt_youtube_description)
response = ai_description.ai_summary()
horoscope_description = response.strip()
print(f'Generated description: {horoscope_description}')

horoscope_video = random.choice(range(1, 10))
print(f"Video used is horoscope_{horoscope_video}.mp4")
video_time = 123


def fitted_text(
        text,
        font,
        max_width,
        max_height,
        start,
        duration,
        color="#FFFFFF",
        stroke_color="#000000",
        stroke_width=2,
        text_align="center",
        position="center",
        method="caption",
        min_font=20,
        max_font=300,
        ):
    """
    Create the largest possible TextClip that fits inside
    max_width × max_height using binary search.
    """

    low = min_font
    high = max_font
    best_clip = None

    while low <= high:

        font_size = (low + high) // 2

        clip = TextClip(
            text=text,
            font=font,
            font_size=font_size,
            color=color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            size=(max_width, None),
            method=method,
            text_align=text_align,
            )

        if clip.w <= max_width and clip.h <= max_height:
            best_clip = clip
            low = font_size + 1
        else:
            high = font_size - 1

    if best_clip is None:
        best_clip = TextClip(
            text=text,
            font=font,
            font_size=min_font,
            color=color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            size=(max_width, None),
            method=method,
            text_align=text_align,
            )

    return (
        best_clip
        .with_start(start)
        .with_duration(duration)
        .with_position(position)
    )



video_to_use = VideoFileClip(
    f"static/assets/video/horoscope_{horoscope_video}.mp4"
    )


video_duration = video_to_use.duration

multiple_by = 1
if video_duration < video_time:
    multiple_by = int(video_time // video_duration + 1)

video = (video_to_use * multiple_by).subclipped(0, video_time)

if datetime.now().day == 1 or datetime.now().weekday() == 0:

    # Landscape 1920x1080
    video_resized = video.resized(height=1080)
    video_final = video_resized.cropped(
        width=1920,
        x_center=video_resized.w / 2,
        )

else:

    # Portrait 1080x1920
    video_resized = video.resized(height=1920)
    video_final = video_resized.cropped(
        width=1080,
        x_center=video_resized.w / 2,
        )

VIDEO_W = video_final.w
VIDEO_H = video_final.h

TEXT_WIDTH = int(VIDEO_W * 0.90)
TEXT_HEIGHT = int(VIDEO_H * 0.90)

TITLE_HEIGHT = int(VIDEO_H * 0.12)
BODY_HEIGHT = int(VIDEO_H * 0.75)

txt_start = fitted_text(
    text=f"Welcome\nDay {day_of_year} Daily Horoscope!",
    font="static/assets/font/Newsreader_60pt-Bold.ttf",
    max_width=TEXT_WIDTH,
    max_height=int(VIDEO_W * 0.88),
    start=0,
    duration=3,
    color="#D5F2ED",
    stroke_color="#BF0000",
    stroke_width=3,
    position=("center", VIDEO_H * 0.08),
    )

start_time = 3
clips = []


for horo_time_range in horoscope_data:

    if not horo_time_range:
        continue

    for horoscope_details in horo_time_range:
        sign = fitted_text(
            text=horoscope_details["sign"],
            font="static/assets/font/Newsreader-VariableFont_opsz,wght.ttf",
            max_width=TEXT_WIDTH,
            max_height=TITLE_HEIGHT,
            start=start_time,
            duration=10,
            color="yellow",
            stroke_color="#BF0000",
            stroke_width=2,
            position=("center", VIDEO_H * 0.05),
            )

        body = fitted_text(
            text=horoscope_details["horoscope"],
            font="static/assets/font/Newsreader-VariableFont_opsz,wght.ttf",
            max_width=TEXT_WIDTH,
            max_height=BODY_HEIGHT,
            start=start_time,
            duration=10,
            color="#C4EEF2",
            stroke_color="#BF0000",
            stroke_width=2,
            position=("center", VIDEO_H * 0.18),
            )

        clips.append(sign)
        clips.append(body)

        start_time += 10
        count += 1


txt_last = fitted_text(
    text=closing_text,
    font="static/assets/font/Newsreader-VariableFont_opsz,wght.ttf",
    max_width=TEXT_WIDTH,
    max_height=TEXT_HEIGHT,
    start=123,
    duration=3,
    color="#FFFFFF",
    stroke_color="#E50000",
    stroke_width=2,
    )

horoscope_audio = random.choice(range(2, 4))
print(f"Audio used is audio_{horoscope_audio}.mp3")

audio = AudioFileClip(f"static/assets/audio/audio_{horoscope_audio}.mp3").subclipped(0, 20)
repeats = int(video.duration // 20) + 1
audio_looped = concatenate_audioclips([audio] * repeats).subclipped(0, video.duration)
audio = CompositeAudioClip([audio_looped])

final = CompositeVideoClip([video_final, txt_start, *clips, txt_last])
final = final.with_audio(audio)

# final.write_videofile("youtube_horoscope.mp4", fps=24, threads=8)
final.write_videofile(
    "youtube_horoscope.mp4",
    fps=30,
    codec="libx264",
    preset="fast",
    threads=8,
    audio_codec="aac"
    )

url_youtube = 'https://www.googleapis.com/youtube/v3'
response = requests.get(url_youtube, api_KEY_youtube)
print(response)

# Set YouTube upload scope
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Upload final video to YouTube
local_path = "youtube_horoscope.mp4"
thumbnail_path = "thumbnail.jpg"
print("Uploading started...")

video = VideoFileClip("youtube_horoscope.mp4")
thumbnail_time = 2  # second mark to grab the frame
frame = video.get_frame(thumbnail_time)  # Numpy array
video.close()

thumbnail_img = Image.fromarray(np.uint8(frame))
thumbnail_img.save(thumbnail_path)

authenticate_youtube = YouTube.authenticate_youtube(
    client_id_youtube=client_id_youtube,
    client_secret_youtube=client_secret_youtube,
    YOUTUBE_REFRESH_TOKEN=YOUTUBE_REFRESH_TOKEN)

try:
    YouTube.upload_video(
        file_path=local_path,
        thumbnail=thumbnail_path,
        title=youtube_title,
        description=horoscope_description,
        youtube_hashtags='',
        authenticate_youtube=authenticate_youtube,
        )

    print("Uploaded video successfully.")
except Exception as e:
    print(f"Failed to upload video: {e}")
finally:
    if os.path.exists(local_path):
        try:
            os.remove(thumbnail_path)
            os.remove(local_path)
            print("Cleaned up local video file.")
        except Exception as cleanup_error:
            print(f"Failed to delete local video file: {cleanup_error}")

finish_time = time.time()
print(f"Finished in {round(finish_time - start_time, 2)} seconds.")
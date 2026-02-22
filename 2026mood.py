import datetime
import time
from automation import YouTube
from dotenv import load_dotenv
import os
import urllib.request



load_dotenv()
client_id_youtube = os.getenv("YTA_CLIENT_ID")
client_secret_youtube = os.getenv("YTA_CLIENT_SECRET")
YOUTUBE_REFRESH_TOKEN = os.getenv("YT_MOOD_RT")
# print(client_id_youtube, YOUTUBE_REFRESH_TOKEN, client_secret_youtube)

file_url = "https://johnmapunda.com/static/assets/image/2026/mood_2026.MP4"
local_filename = "mood_2026.MP4"

# Check if file already exists
if os.path.exists(local_filename):
    print(f"File already exists: {local_filename}")
else:
    print(f"Downloading {file_url} ...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
    request = urllib.request.Request(file_url, headers=headers)
    with urllib.request.urlopen(request) as response, open(local_filename, "wb") as out_file:
        out_file.write(response.read())
    print(f"Downloaded: {local_filename}")

file_path = os.path.abspath(local_filename)
print("File path:", file_path)
day_of_year = datetime.datetime.now().timetuple().tm_yday
title = f' Day {day_of_year} of 2026'
description = "#mood2026 i don't own the content for deletion just check me out and i'll remove the content. Follow @iampriesst on is account for this music in Apple Music check https://music.apple.com/tz/album/akonuche/1865986757?i=1865986759"
hashtags = '#2026'
thumbnail = None

authenticate_youtube = YouTube.authenticate_youtube(
    client_id_youtube=client_id_youtube,
    client_secret_youtube=client_secret_youtube,
    YOUTUBE_REFRESH_TOKEN=YOUTUBE_REFRESH_TOKEN)
YouTube.upload_video(file_path=file_path, title=title, description=description, youtube_hashtags=hashtags,
                     thumbnail=thumbnail, authenticate_youtube=authenticate_youtube)

time.sleep(60)
os.remove(file_path)
print("🧹 Local file deleted.")

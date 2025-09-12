import os
import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from supabase import create_client, Client
from dotenv import load_dotenv

# load_dotenv()
# === CONSTANTS === #
YTA_YOUTUBE_REFRESH_TOKEN = os.getenv("YTA_YOUTUBE_REFRESH_TOKEN")
GSHEETS_REFRESH_TOKEN = os.getenv("GSHEETS_REFRESH_TOKEN")
YTA_CLIENT_ID = os.getenv("YTA_CLIENT_ID")
YTA_CLIENT_SECRET = os.getenv("YTA_CLIENT_SECRET")
channel_id = os.getenv("channel_id")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

client_id_youtube = os.getenv('client_id_youtube')
client_secret_youtube = os.getenv('client_secret_youtube')
YOUTUBE_REFRESH_TOKEN = os.getenv('YOUTUBE_REFRESH_TOKEN')
YT_FORCE_RT = os.getenv('YT_FORCE_RT')

# === SUPABASE SETUP === #
print("🔌 Connecting to Supabase...")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
print("✅ Supabase connection established.")

# === YOUTUBE DATA FETCHING === #
def authenticate_youtube():
    print("🔐 Authenticating YouTube API...")
    creds = Credentials(
        token=None,
        refresh_token=YTA_YOUTUBE_REFRESH_TOKEN,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=YTA_CLIENT_ID,
        client_secret=YTA_CLIENT_SECRET,
        scopes=["https://www.googleapis.com/auth/youtube.readonly"],
    )
    creds.refresh(Request())
    print("✅ YouTube authentication successful.")
    return build("youtube", "v3", credentials=creds)

youtube = authenticate_youtube()

def get_uploads_playlist_id(channel_id):
    print("📥 Fetching uploads playlist ID...")
    response = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    ).execute()
    playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    print(f"✅ Uploads playlist ID: {playlist_id}")
    return playlist_id

def get_all_video_ids(playlist_id):
    print("📼 Fetching all video IDs from playlist...")
    video_ids = []
    next_page_token = None
    while True:
        response = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        for item in response["items"]:
            video_ids.append(item["contentDetails"]["videoId"])

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    print(f"✅ Total videos found: {len(video_ids)}")
    return video_ids

def get_video_details(video_id, index, total):
    print(f"🔍 Fetching video {index + 1} out of {total}...")
    video_response = youtube.videos().list(
        part="snippet,statistics",
        id=video_id
    ).execute()

    snippet = video_response['items'][0]['snippet']
    stats = video_response['items'][0]['statistics']

    upload_date = datetime.datetime.strptime(snippet['publishedAt'][:10], "%Y-%m-%d").date()
    title = snippet['title']
    description = snippet.get('description', '')
    view_count = int(stats.get('viewCount', 0))
    like_count = int(stats.get('likeCount', 0))
    comment_count = int(stats.get('commentCount', 0))

    subs_response = youtube.channels().list(
        part="statistics",
        id=channel_id
    ).execute()
    subscriber_count = int(subs_response['items'][0]['statistics'].get('subscriberCount', 0))

    return {
        "video_id": video_id,
        "title": title,
        "description": description,
        "upload_date": str(upload_date),
        "view_count": view_count,
        "like_count": like_count,
        "comment_count": comment_count,
        "subscriber_count": subscriber_count
    }

def save_or_update_video(data):
    print(f"💾 Saving or updating video data...")
    existing = supabase.table("youtube_automation").select("video_id").eq("video_id", data['video_id']).execute()
    if existing.data:
        supabase.table("youtube_automation").update(data).eq("video_id", data['video_id']).execute()
        print("🔄 Video updated.")
    else:
        supabase.table("youtube_automation").insert(data).execute()
        print("🆕 Video inserted.")

# === MAIN FETCH AND STORE === #
uploads_playlist_id = get_uploads_playlist_id(channel_id)
video_ids = get_all_video_ids(uploads_playlist_id)

for index, vid in enumerate(video_ids):
    details = get_video_details(vid, index, len(video_ids))
    save_or_update_video(details)

print("✅ All video data saved or updated in Supabase.")

# === GOOGLE SHEETS AUTH === #
def authenticate_sheets():
    print("🔐 Authenticating Google Sheets API...")
    creds = Credentials(
        token=None,
        refresh_token=GSHEETS_REFRESH_TOKEN,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=YTA_CLIENT_ID,
        client_secret=YTA_CLIENT_SECRET,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    creds.refresh(Request())
    print("✅ Google Sheets authentication successful.")
    return build('sheets', 'v4', credentials=creds)

# === EXPORT TO SHEET === #
def export_to_sheet():
    print("📤 Exporting data to Google Sheets...")
    service = authenticate_sheets()
    sheet = service.spreadsheets()

    rows = [
        ["Upload Date", "Subscribers", "Views", "Likes", "Comments", "Video Title"]
    ]

    data = supabase.table("youtube_automation").select("*").order("upload_date").execute().data

    for row in data:
        rows.append([
            row['upload_date'],
            row['subscriber_count'],
            row['view_count'],
            row['like_count'],
            row['comment_count'],
            row['title']
        ])

    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range="Sheet1!A1",
        valueInputOption="RAW",
        body={"values": rows}
    ).execute()

    print("📊 Data exported to Google Sheets")

export_to_sheet()


response_data = (
    supabase.table("youtube_automation")
    .select("*")
    .execute()
)
# print(response_data)

from datetime import datetime, timedelta

# Define today and the 90-day cutoff
today = datetime.today()
ninety_days_ago = today - timedelta(days=90)

filtered = []
for to_delete in response_data.data:
    if datetime.strptime(to_delete['upload_date'], "%Y-%m-%d") <= ninety_days_ago and to_delete['view_count'] == 0 and to_delete['like_count'] == 0 and to_delete['comment_count'] == 0:
        filtered.append(to_delete)

delete_this = []
delete = sorted(filtered, key=lambda x: x['id'])[:1]
for item in delete:
    delete_this.append(item['video_id'])
    print(item['id'])

video_to_delete = delete_this[0]
print(video_to_delete)

def authenticate_youtube():
    creds = Credentials(
        token=None,
        refresh_token=YT_FORCE_RT,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=YTA_CLIENT_ID,
        client_secret=YTA_CLIENT_SECRET,
        scopes=["https://www.googleapis.com/auth/youtube.force-ssl"],
        )
    creds.refresh(Request())  # This fetches a new access token using the refresh token
    youtube = build('youtube', 'v3', credentials=creds)
    return youtube

def delete_video(video_id):
    youtube = authenticate_youtube()
    try:
        youtube.videos().delete(id=video_id).execute()
        print(f"Deleted video: {video_id}")
    except Exception as e:
        print(f"Failed to delete video {video_id}: {e}")

if today.day % 2 == 0:
    try:
        delete_video(f'{video_to_delete}')
    except Exception as e:
        print(e)
else:
    print("We are not Deleting video Today")
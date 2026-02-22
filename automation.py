from dotenv import load_dotenv
from google.cloud import texttospeech
import os
from gtts import gTTS
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# load_dotenv()
# client_id_youtube = os.getenv('client_id_youtube')
# client_secret_youtube = os.getenv('client_secret_youtube')
# YOUTUBE_REFRESH_TOKEN = os.getenv('YOUTUBE_REFRESH_TOKEN')

class TextToSpeech:
    def __init__(self, text):
        self.text = text

    def google_tts(self):
        # 1. JSON key
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_service_account_key.json"

        # 2. client
        client = texttospeech.TextToSpeechClient()

        # 3. request
        synthesis_input = texttospeech.SynthesisInput(text=self.text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
            name='en-US-Chirp-HD-F'
            )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
            )

        # 4. Save
        with open("advice_audio.mp3", "wb") as f:
            f.write(response.audio_content)
        print("Audio saved!")

    def gtts(self):
        tts = gTTS(f'{self.text}', lang="en", slow=False)
        tts.save("advice_audio.mp3")

class YouTube:
    @classmethod
    def authenticate_youtube(cls, YOUTUBE_REFRESH_TOKEN, client_id_youtube, client_secret_youtube):
        print(YOUTUBE_REFRESH_TOKEN, client_id_youtube, client_secret_youtube)
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

    @classmethod
    def upload_video(cls, file_path, title, description, youtube_hashtags, thumbnail, authenticate_youtube):
        youtube = authenticate_youtube
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
        try:
            thumbnail_request.execute()
        except Exception as e:
            print('No Thumbnail or it Failed to add', e)

        # Cleanup local file
        try:
            os.remove(file_path)
            print("Local file deleted.")
        except Exception as e:
            print('Failed to remove', e)

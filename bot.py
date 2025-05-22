import tweepy
import os
from dotenv import load_dotenv
from openai import OpenAI
import gspread
from google.oauth2.service_account import Credentials

# .env読み込み
load_dotenv()

# OpenAIクライアント
client_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# OAuth1.0a認証（tweepy.API用）
auth = tweepy.OAuth1UserHandler(
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_KEY_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET")
)
api = tweepy.API(auth)

# gspread認証設定
def save_to_sheet(tweet_text, reply_text):
    google_creds_dict = {
        "type": os.getenv("GOOGLE_TYPE"),
        "project_id": os.getenv("GOOGLE_PROJECT_ID"),
        "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
        "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_CERT_URL"),
        "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_CERT_URL")
    }

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(google_creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("ReHumanログ").sheet1
    sheet.append_row([tweet_text, reply_text])

# リプライ生成
def generate_reply(tweet_text):
    prompt = f"このツイートに誠実で鋭い日本語のリプライを作成してください:\n\n{tweet_text}"
    response = client_ai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "あなたはX（旧Twitter）上で魅力的な返事をする知的なBotです。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# メイン処理
TARGET_USERNAME = "ReHuman_parkour"

try:
    user = api.get_user(screen_name=TARGET_USERNAME)
    tweets = api.user_timeline(user_id=user.id, count=5, tweet_mode="extended")

    if tweets:
        latest_tweet = tweets[0]
        reply = generate_reply(latest_tweet.full_text)
        api.update_status(
            status=f"@{user.screen_name} {reply}",
            in_reply_to_status_id=latest_tweet.id
        )
        print("送信済みリプライ：", reply)
        save_to_sheet(latest_tweet.full_text, reply)
    else:
        print("ツイートが見つかりませんでした。")

except tweepy.TweepyException as e:
    print("Tweepyエラー:", str(e))
except Exception as e:
    print("予期しないエラー：", str(e))
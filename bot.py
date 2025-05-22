import tweepy
import os
import time
import gspread
from openai import OpenAI
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

# 環境変数の読み込み
load_dotenv()

# OpenAIクライアント初期化
client_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Twitter API認証
client_tw = tweepy.Client(
    bearer_token=os.getenv("BEARER_TOKEN"),
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_KEY_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET")
)

# Google Sheetsに保存する関数
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

# リプライ文を生成する関数
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
    user = client_tw.get_user(username=TARGET_USERNAME)
    tweets = client_tw.get_users_tweets(id=user.data.id, max_results=5)

    if tweets.data:
        latest_tweet = tweets.data[0]
        reply = generate_reply(latest_tweet.text)
        client_tw.create_tweet(in_reply_to_tweet_id=latest_tweet.id, text=reply)
        print("送信済みリプライ：", reply)
        save_to_sheet(latest_tweet.text, reply)
    else:
        print("ツイートが見つかりませんでした。")

except tweepy.TooManyRequests:
    print("リクエストが多すぎます。15分待機します。")
    time.sleep(900)

except Exception as e:
    print("予期しないエラー：", str(e))
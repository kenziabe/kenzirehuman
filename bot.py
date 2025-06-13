import os
import json
import tweepy
import gspread
from dotenv import load_dotenv
from openai import OpenAI
from google.oauth2.service_account import Credentials

# 環境変数の読み込み
load_dotenv()

# OpenAIクライアント
client_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# GPTでツイート生成
def generate_tweet():
    response = client_ai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは人を前向きに励ます言葉を投稿するツイートBotです。"},
            {"role": "user", "content": "140文字以内で今日の元気が出る言葉をツイートしてください。"}
        ]
    )
    return response.choices[0].message.content.strip()

# Twitter API v2クライアント設定
twitter_client = tweepy.Client(
    bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
    consumer_key=os.getenv("TWITTER_API_KEY"),
    consumer_secret=os.getenv("TWITTER_API_SECRET"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_SECRET")
)

# Google Sheets APIクライアント設定
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
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(google_creds_dict, scopes=scope)
sheet = gspread.authorize(creds).open("ReHumanログ").sheet1

# ツイート内容をスプレッドシートに保存
def save_to_sheet(tweet_text):
    sheet.append_row([tweet_text])

# 投稿処理
def post_tweet(tweet_text):
    twitter_client.create_tweet(text=tweet_text)

# 実行ブロック
if __name__ == "__main__":
    tweet = generate_tweet()
    print("生成されたツイート：", tweet)
    post_tweet(tweet)
    save_to_sheet(tweet)
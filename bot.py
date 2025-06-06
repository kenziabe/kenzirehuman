import os
import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from openai import OpenAI
import json
import tweepy  # ← 追加

# 環境変数読み込み（Railwayでもローカルでも対応）
load_dotenv()

# OpenAIクライアント（v1形式）
client_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Google認証情報の辞書を構築
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

# Google Sheets APIの認証
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_info(google_creds_dict, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open("ReHumanログ").sheet1

# Twitter API 認証（OAuth1.0a）
auth = tweepy.OAuth1UserHandler(
    os.getenv("TWITTER_API_KEY"),
    os.getenv("TWITTER_API_SECRET"),
    os.getenv("TWITTER_ACCESS_TOKEN"),
    os.getenv("TWITTER_ACCESS_SECRET")
)
twitter_client = tweepy.API(auth)

# ChatGPTでリプライを生成
def generate_reply(tweet_text):
    response = client_ai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは人間味と共感力をもった優しいリプライを作成するBotです。"},
            {"role": "user", "content": f"このツイートに共感ある返信を書いてください：{tweet_text}"}
        ]
    )
    return response.choices[0].message.content.strip()

# Google Sheets に書き込む関数
def save_to_sheet(tweet_text, reply_text):
    sheet.append_row([tweet_text, reply_text])

# Twitterにリプライ投稿
def post_reply(reply_text, tweet_id):
    twitter_client.update_status(
        status=reply_text,
        in_reply_to_status_id=tweet_id,
        auto_populate_reply_metadata=True
    )

# テスト実行
if __name__ == "__main__":
    tweet = "今日もがんばったあなたへ。"
    tweet_id = 1234567890123456789  # ← ここを実際のツイートIDに変更してテスト！

    reply = generate_reply(tweet)
    print("生成されたリプライ：", reply)

    save_to_sheet(tweet, reply)
    post_reply(reply, tweet_id)
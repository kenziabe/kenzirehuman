import tweepy
import os
import time
from dotenv import load_dotenv
from openai import OpenAI

# .envから環境変数を読み込む
load_dotenv()

# OpenAIクライアント初期化（gpt-3.5使用中）
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Twitter APIクライアント
client = tweepy.Client(
    bearer_token=os.getenv("BEARER_TOKEN"),
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_KEY_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET")
)

# リプライ対象のアカウント
TARGET_USERNAME = "ReHuman_parkour"

# ChatGPTでリプライを生成
def generate_reply(tweet_text):
    prompt = f"このツイートに誠実で鋭い日本語のリプライを作成してください:\n\n{tweet_text}"
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",  # GPT-4解放後に "gpt-4" に変更OK
        messages=[
            {"role": "system", "content": "あなたはX（旧Twitter）上で魅力的な返事をする知的なBotです。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# メイン処理
try:
    user = client.get_user(username=TARGET_USERNAME)
    tweets = client.get_users_tweets(id=user.data.id, max_results=5)

    if tweets.data:
        latest_tweet = tweets.data[0]
        reply = generate_reply(latest_tweet.text)
        client.create_tweet(in_reply_to_tweet_id=latest_tweet.id, text=reply)
        print("送信済みリプライ：", reply)
        save_to_sheet(latest_tweet.text, reply)
        import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials

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
    creds = ServiceAccountCredentials.from_json_keyfile_dict(google_creds_dict, scope)
    client = gspread.authorize(creds)

    # ここでスプレッドシート名を指定（Google Drive 上に作成済みのもの）
    sheet = client.open("ReHumanログ").sheet1
    sheet.append_row([tweet_text, reply_text])
    else:
        print("ツイートが見つかりませんでした。")

except tweepy.TooManyRequests:
    print("リクエスト過多。15分休憩します。")
    time.sleep(900)

except Exception as e:
    print("予期しないエラー：", str(e))
    import gspread
from google.oauth2.service_account import Credentials

def save_to_sheet(tweet_text, reply_text):
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(
        "credentials.json",  # Railwayではこの内容を環境変数にして後述する別方法が必要
        scopes=scopes
    )
    client = gspread.authorize(creds)
    sheet = client.open("ReHumanログ").sheet1
    sheet.append_row([tweet_text, reply_text])
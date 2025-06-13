import os
import tweepy
import gspread
import json
import datetime
from dotenv import load_dotenv
from openai import OpenAI
from google.oauth2.service_account import Credentials

# 環境変数読み込み
load_dotenv()

# GPTクライアント
client_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# プロンプト一覧（案①〜③）
prompts = [
    "限界を超えて進化する人間＝Re:Humanとして、日々の行動や思考を変えるような一言を140文字以内でツイートしてください。",
    "Re:Humanという自己再構築をテーマに、力・意志・習慣・哲学を持って生きる人に向けたメッセージを140文字で表現してください。",
    "Re:Humanの精神である『本能を制し、理性で進化する』というテーマに沿った、知的で力強いツイートを140文字以内で生成してください。"
]

# Google Sheets連携
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

# 投稿数からプロンプトを選ぶ（ループ式）
def select_prompt():
    total_posts = len(sheet.get_all_values())  # ヘッダー無しで全行数
    index = total_posts % len(prompts)
    return prompts[index]

# GPTでツイート生成
def generate_tweet():
    prompt = select_prompt()
    response = client_ai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたはRe:Humanという哲学的ストイックなツイートを投稿するAIです。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# Twitter v2投稿（無料OK）
twitter_client = tweepy.Client(
    bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
    consumer_key=os.getenv("TWITTER_API_KEY"),
    consumer_secret=os.getenv("TWITTER_API_SECRET"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_SECRET")
)

# 投稿実行
def post_tweet(tweet_text):
    twitter_client.create_tweet(text=tweet_text)

# Sheetsへ保存（日時＋内容）
def save_to_sheet(tweet_text):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    sheet.append_row([now, tweet_text])

# 実行
if __name__ == "__main__":
    tweet = generate_tweet()
    print("生成されたツイート：", tweet)
    post_tweet(tweet)
    save_to_sheet(tweet)
from openai import OpenAI
import os
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

# OpenAI初期化
client_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Sheets保存関数（credentials.jsonを直接読み込む方式）
def save_to_sheet(tweet_text, reply_text):
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("ReHumanログ").sheet1
    sheet.append_row([tweet_text, reply_text])

# GPTでリプライ生成
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

# 実行テスト
if __name__ == "__main__":
    tweet = "人生は短い。だからこそ、本当にやりたいことに時間を使いたい。"
    reply = generate_reply(tweet)
    print("生成されたリプライ：", reply)
    save_to_sheet(tweet, reply)
import os
import gspread
from google.oauth2.service_account import Credentials
from openai import OpenAI

# OpenAIクライアント（v1形式）
client_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Google認証情報の読み込み
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
scope = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_info(google_creds_dict, scopes=scope)
client_gs = gspread.authorize(creds)
sheet = client_gs.open("ReHumanログ").sheet1

# ChatGPTでリプ生成
def generate_reply(tweet_text):
    prompt = f"このツイートに誠実で共感のある日本語のリプライを作成してください:\n\n{tweet_text}"
    response = client_ai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたはX上で知性と共感のあるリプライを返すAIです。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# シートに保存
def save_to_sheet(tweet_text, reply_text):
    sheet.append_row([tweet_text, reply_text])

# 実行テスト
if __name__ == "__main__":
    tweet = "人生は短い。だからこそ、本当にやりたいことに時間を使いたい。"
    reply = generate_reply(tweet)
    print("生成されたリプライ：", reply)
    save_to_sheet(tweet, reply)
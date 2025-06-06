import os
import gspread
from openai import OpenAI
from google.oauth2.service_account import Credentials

# OpenAIクライアント（v1形式）
client_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Google認証情報（環境変数から）
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
gs_client = gspread.authorize(creds)
sheet = gs_client.open("ReHumanログ").sheet1

def generate_reply(tweet_text):
    prompt = f"このツイートに誠実で共感のある日本語のリプライを作成してください:\n\n{tweet_text}"
    response = client_ai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは思慮深く共感力のあるXアカウント運用者です。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def save_to_sheet(tweet_text, reply_text):
    sheet.append_row([tweet_text, reply_text])

if __name__ == "__main__":
    tweet = "人生は短い。だからこそ、本当にやりたいことに時間を使いたい。"
    reply = generate_reply(tweet)
    print("生成されたリプライ：", reply)
    save_to_sheet(tweet, reply)
import os
import gspread
from google.oauth2.service_account import Credentials

# Google認証用の辞書を環境変数から構築
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

# 認証スコープ設定（Google Sheets向け）
scope = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_info(google_creds_dict, scopes=scope)

# 認証してシートにアクセス
client = gspread.authorize(creds)
sheet = client.open("ReHumanログ").sheet1  # あなたのスプレッドシート名に合わせて変更可能

# テスト保存関数（必要に応じて使う）
def save_to_sheet(tweet_text, reply_text):
    sheet.append_row([tweet_text, reply_text])
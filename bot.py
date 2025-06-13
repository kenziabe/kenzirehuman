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

# 投稿テーマ（案①〜⑤）
prompts = [
    "Re:Humanという進化思想において、日々の行動・意志・習慣が自分を再構築する鍵である。限界を超えて成長しようとする人間に向けて、知性と力強さを持ち合わせた140文字のメッセージを生成してください。",
    "Re:Humanの精神である『本能を制し、理性で進化する』というテーマに沿った、知的で力強いツイートを140文字以内で生成してください。",
    "Re:Humanという進化思想において、肉体は理性と知識に基づき進化すべき対象でありながら、同時に本能的で野生的な力とも接続されるべきである。運動生理学・神経系・栄養・可動性の観点から、都市を生き抜く野生としての身体をどう最適化するか、140文字で投稿してください。",
    "Re:Humanという自己進化思想において、言語・対人関係・影響力のコントロールもまた鍛えるべき対象である。自身の言葉が他者に与える影響、対話の質、共感と自己主張のバランスを知性と意志で高めていく姿勢を示す投稿を、140文字で生成してください。",
    "Re:Humanという進化思想において、パルクールは思考・身体・空間との関係を再構築するための極めて実践的な手段である。運動生理学・神経科学・空間認知・教育学的視点に基づき、パルクールの意義・理想・トレーニング・業界構造への問いなどを含んだ哲学的・実践的ツイートを140文字で生成してください。"
]

# Google Sheets 認証
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

# 投稿順を算出（ループ）
def select_prompt():
    total_posts = len(sheet.get_all_values())
    index = total_posts % len(prompts)
    return prompts[index]

# GPTで生成
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

# ✅ Twitter API v1.1（無料で投稿可能）
auth = tweepy.OAuth1UserHandler(
    os.getenv("TWITTER_API_KEY"),
    os.getenv("TWITTER_API_SECRET"),
    os.getenv("TWITTER_ACCESS_TOKEN"),
    os.getenv("TWITTER_ACCESS_SECRET")
)
twitter_client = tweepy.API(auth)

# ツイート投稿（140文字制限あり）
def post_tweet(tweet_text):
    twitter_client.update_status(status=tweet_text)

# Sheetsへ保存（日時＋本文）
def save_to_sheet(tweet_text):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    sheet.append_row([now, tweet_text])

# 実行
if __name__ == "__main__":
    tweet = generate_tweet()
    print("生成されたツイート：", tweet)
    post_tweet(tweet)
    save_to_sheet(tweet)
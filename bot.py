import os
from dotenv import load_dotenv
from openai import OpenAI
import tweepy

# 環境変数読み込み
load_dotenv()

# OpenAIクライアント
client_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# GPTでツイート生成
def generate_tweet():
    response = client_ai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは人を前向きにする優しいツイートを投稿するBotです。"},
            {"role": "user", "content": "今日の元気が出る一言を140文字以内でください。"}
        ]
    )
    return response.choices[0].message.content.strip()

# Twitter API v2 認証
twitter_client = tweepy.Client(
    bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
    consumer_key=os.getenv("TWITTER_API_KEY"),
    consumer_secret=os.getenv("TWITTER_API_SECRET"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_SECRET")
)

# 投稿処理
def post_tweet(tweet_text):
    twitter_client.create_tweet(text=tweet_text)

# 実行
if __name__ == "__main__":
    tweet = generate_tweet()
    print("生成されたツイート：", tweet)
    post_tweet(tweet)
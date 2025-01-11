import logging
from bs4 import BeautifulSoup
import os
import json
import requests

logging.basicConfig(level=logging.DEBUG)

API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
SENT_LIST_FILE = 'google.json'

KEYWORDS = "открытие фонтанов"
IGNORE_SITES = ["instagram", "livejournal", "fontanka"]
IGNORE_WORDS = ["нефть", "недр", "месторождение"]

def clean_url(url):
    url = url[len('/url?q='):]
    url = url.split('&sa=U&ved')[0]
    return url

def is_valid_link(link):
    cleaned_link = clean_url(link)
    if requests.head(cleaned_link).status_code == 200:
        return True
    return False

def get_google_search_results(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
    response = requests.get(query, headers=headers)
    return BeautifulSoup(response.text, 'html.parser')

def check_if_url_already_sent(link):
    with open(SENT_LIST_FILE, 'r') as file:
        sent_list = json.load(file)
    return link in sent_list

def save_sent_list(sent_list):
    with open(SENT_LIST_FILE, 'w') as file:
        json.dump(sent_list, file)

def get_news_articles():
    query = f'https://www.google.ru/search?q={KEYWORDS}&hl=ru&tbs=qdr:d'
    soup = get_google_search_results(query)
    articles = soup.find_all('h3')
    return articles

def send_message(title, link):
    message_text = f"{title}\n{link}\n⛲@MonitoringFontan📰#MonitoringFontan"
    return requests.post(f"https://api.telegram.org/bot{API_TOKEN}/sendMessage", data={
        'chat_id': CHANNEL_ID,
        'text': message_text
    })

def main():
    articles = get_news_articles()
    sent_list = []
    repeat_count = 0

    with open(SENT_LIST_FILE, 'r') as file:
        sent_list = json.load(file)

    for article in articles:
        link = article.find('a')['href']
        title = article.text
        cleaned_link = clean_url(link)

        if check_if_url_already_sent(cleaned_link):
            continue

        if any(word in title for word in IGNORE_WORDS):
            continue

        if any(site in cleaned_link for site in IGNORE_SITES):
            continue

        if is_valid_link(link):
            send_message(title, link)
            sent_list.append(cleaned_link)

        repeat_count += 1

        if repeat_count % 90 == 0:
            sent_list = sent_list[-9:]
            save_sent_list(sent_list)

if __name__ == '__main__':
    main()

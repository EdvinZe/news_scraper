import datetime
from bs4 import BeautifulSoup
import lxml
import requests
import csv
import pandas as pd
import re
import time


url_lrytas = "https://www.lrytas.lt"
url_delfi = "https://www.delfi.lt/paieska"

headers = {
    "Accept" : "*/*",
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

data = []

def get_news_lrytas(url):
    try:
        req = requests.get(url, headers=headers)
        req.raise_for_status()
        src = req.text
    except requests.exceptions.RequestException as ex:
        print(f"Error fetching Lrytas: {ex}")
        return

    # with open("data/lrytas_new.html", "w") as file:
    #     file.write(src)

    # with open("data/lrytas_new.html", "r") as file:
    #     src = file.read()

    soup = BeautifulSoup(src, "lxml")

    divs_to_remove = soup.find_all("div", class_="mb-9")
    if len(divs_to_remove) >= 3:
        divs_to_remove[-3].decompose()

    div_blocks = soup.find_all("div", class_="rounded-[4px] h-full flex relative shadow-base bg-white flex-col")

    for item in div_blocks:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        href = item.find("a").get("href")
        full_href = "https://www.lrytas.lt"+href
        text = item.find("h2").text
        theme = item.find("span", class_="text-xs ml-1.5").text
        record = {
            "time" : current_time,
            "site" : "Lrytas",
            "link" : full_href,
            "description" : text,
            "theme" : theme
        }
        data.append(record)

def get_news_delfi(url):
    try:
        req = requests.get(url, headers=headers)
        req.raise_for_status()
        src = req.text
    except requests.exceptions.RequestException as ex:
        print(f"Error fetching Delfi: {ex}")
        return

    # with open("data/delfi_new.html", "w") as file:
    #     file.write(src)
    # with open("data/delfi_new.html", "r") as file:
    #     src = file.read()

    soup = BeautifulSoup(src, "lxml")

    div_block = soup.find("div", attrs={"data-container" : "articles-container"}).find_all("div", class_="col-12")

    for item in div_block:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        href = item.find("a").get("href")
        if href.startswith("/"):
            href = "https://www.delfi.lt/" + href
        text = item.find("h5", class_="headline-title headline-title--size-h4 headline-title--size-sm-h6").text
        theme = item.find("div", class_="headline-labels__label").text.strip()

        record = {
            "time" : current_time,
            "site" : "Delfi",
            "link" : href,
            "description" : text,
            "theme" : theme
        }
        data.append(record)

def get_data():
    get_news_lrytas(url_lrytas)
    get_news_delfi(url_delfi)

    new_dp = pd.DataFrame(data)
    existing_data = pd.read_excel("data/thenews.xlsx")
    old_dp = pd.DataFrame(existing_data)

    if not existing_data.empty:
        new_news = new_dp[~new_dp["link"].isin(existing_data["link"])]
    else:
        new_news = new_dp

    combined_data = pd.concat([old_dp, new_dp]).drop_duplicates(subset=["link"], keep="first")
    combined_data.to_excel("data/thenews.xlsx", index=False)
    combined_data.to_csv("data/thenews.csv", index=False)

    print("New news")
    print(new_news)

while True:
    get_data()
    time.sleep(600)
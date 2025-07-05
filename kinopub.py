import json
import re
import sys
import time
import logging
import argparse
from typing import Dict
import requests
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from history import (
    saveSeasonsOfTranslator,
    searchPhrase,
    searchSeason,
    searchShow,
    saveShow,
    write,
    read,
)
from browser import Browser
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


headers = {"User-Agent": "Mozilla/5.0"}


def setLocalStoragePlayerSettings(driver: WebDriver):
    script = """
    localStorage.setItem('pljsquality', '1080p');
    """
    driver.execute_script(script)

    script = """
    localStorage.setItem('pljssubtitle', 'English');
    """
    driver.execute_script(script)


def get_source_or_seasons(translator_id: str, url: str):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    seasons = {}

    # Find season items
    li_seasons = soup.find_all(class_="b-simple_season__item")

    if not li_seasons:
        try:
            driver = startBrowser()
        except Exception as e:
            return {"error": e}

        driver.get(url)
        return captureNetwork(driver)

    for li in li_seasons:
        tab_id = li.get("data-tab_id")
        if tab_id:
            seasons[tab_id] = 0

    # Count episodes for each season
    for tab_id in seasons.keys():
        li_episodes = soup.select(f'a[data-season_id="{tab_id}"]')
        seasons[tab_id] = len(li_episodes)

    return {"seasons": seasons}


def get_episode_url(translator: Dict[str, str]):
    try:
        driver = startBrowser()
    except Exception as e:
        return {"error": e}

    translator["url"] = translator["url"].replace(".html", "/")
    url = f"{translator['url']}{translator['s']}-season/{translator['e']}-episode.html"

    driver.get(url)

    # Reload page until dialog window with error is not visible
    # TODO: Refine
    while True:
        try:
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.ID, "ps-infomessage-title"))
            )
            time.sleep(1)
            driver.execute_script("window.location.reload(true);")
        except TimeoutException:
            break

    try:
        # Wait until button with needed translator_id is active
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, f"a[data-translator_id='{translator['t']}'].active")
            )
        )
        # Wait until preloader is gone
        WebDriverWait(driver, 30).until(
            EC.invisibility_of_element_located((By.ID, "cdnplayer-preloader"))
        )
    except TimeoutException:
        return {"error": "Timed out waiting for translator element or preloader"}

    time.sleep(2)

    return captureNetwork(driver)


def get(show_url: str):

    response = requests.get(show_url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Find translator list items
    li_translators = soup.select("ul#translators-list a")

    if not li_translators:
        try:
            driver = startBrowser()
        except Exception as e:
            return {"error": e}

        driver.get(show_url)

        # WebDriverWait(driver, 10).until(
        #    EC.invisibility_of_element_located((By.ID, "cdnplayer-preloader"))
        # )

        # If only video, without audio tracks and seasons
        return captureNetwork(driver)

    translators = []
    for li in li_translators:
        translator = {
            "href": li.get("href"),
            "id": li.get("data-translator_id"),
            "title": li.text.strip(),
        }
        translators.append(translator)

    return {"translators": translators}


def scrapAllShows(url: str):
    pages = [url]
    results = []
    is_navigation = False

    for page in pages:
        response = requests.get(page, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        if not is_navigation:
            links_without_span = [
                a
                for a in soup.select("div.b-navigation a")
                if not a.find("span", recursive=False)
            ]
            is_navigation = True
            pages.extend(link["href"] for link in links_without_span)

            items = soup.find_all(class_="b-content__inline_item-link")
            for item in items:
                a = item.find("a")
                if a:
                    results.append({"href": a.get("href"), "title": item.text.strip()})

    return results


def findShow(show: str):
    url = f"https://kinopub.me/engine/ajax/search.php?q={show.replace(' ', '%20')}"
    response = requests.get(url)

    if response.status_code != 200:
        return {"error": "Can't find any show"}

    soup = BeautifulSoup(response.text, "html.parser")

    all = soup.find(class_="b-search__live_all")

    # If to many common items
    if all:
        return scrapAllShows(all.get("href").replace(" ", "%20"))

    items = soup.find_all("li")

    if not items:
        return {"error": "Can't find any show"}

    results = []

    for item in items:
        rating = item.find(class_="rating")
        a = item.find("a")

        if a and rating:
            href = a.get("href")
            title = a.text.replace(rating.text, "").strip()
            results.append(
                {
                    "href": href,
                    "title": title,
                }
            )

    return results


def captureNetwork(driver: WebDriver):
    logs = driver.get_log("performance")

    result = {"url": "", "sub": ""}

    for log in reversed(logs):
        message = log["message"]
        if "Network.responseReceived" in message:
            params = json.loads(message)["message"].get("params")
            if params:
                response = params.get("response")
                if response:
                    if not result["url"] and response["url"].endswith(".m3u8"):
                        match = re.search(r"(.+?\.mp4)", response["url"])
                        if match:
                            result["url"] = match.group(1)
                    if not result["sub"] and response["url"].endswith(".vtt"):
                        result["sub"] = response["url"]

    driver.quit()
    return result


def startBrowser() -> WebDriver:
    try:
        driver = Browser().run()
        driver.get("https://kinopub.me/")
        setLocalStoragePlayerSettings(driver)
        time.sleep(1)
        return driver
    except Exception as e:
        raise Exception(e)


def handle_show_search(search_key: str):
    try:
        return searchPhrase(search_key)
    except Exception:
        result = findShow(search_key)

        saved_history = read()
        saved_history["search"][search_key] = result
        write(saved_history)

        return result


def handle_translator_url(translator_id: str, url: str):
    try:
        return searchSeason(url, translator_id)
    except Exception:
        result = get_source_or_seasons(translator_id, url)
        try:
            saveSeasonsOfTranslator(result, url, translator_id)
        except Exception:
            pass

        return result


def handle_url(url: str):
    try:
        return searchShow(url)
    except Exception:
        result = get(url)
        saveShow(result, url)
        return result


def handle_translator(translator: Dict[str, str]):
    return get_episode_url(translator)


def main():
    base_parser = argparse.ArgumentParser()

    subparsers = base_parser.add_subparsers()

    show_parser = subparsers.add_parser(
        name="show",
        prog="show",
        usage="%(prog)s [options]",
        parents=[base_parser],
        add_help=False,
    )
    show_parser.add_argument("-t", "--title", help='Example: "Better Call Saul"')

    t_parser = subparsers.add_parser(
        name="translator",
        prog="translator",
        usage="%(prog)s [options]",
        parents=[base_parser],
        add_help=False,
    )
    t_parser.add_argument("-u", "--url")
    t_parser.add_argument("-ti", "--translatorId")
    t_parser.add_argument("-s", "--season")
    t_parser.add_argument("-e", "--episode")

    t = t_parser.parse_args()
    show = show_parser.parse_args()

    if show.title:
        search_key = show.title.strip().lower()
        return handle_show_search(search_key)

    if t.url and t.translatorId and t.season and t.episode:
        return handle_translator(
            {
                "url": t.url,
                "t": t.translatorId,
                "s": t.season,
                "e": t.episode,
            }
        )
    elif t.translatorId and t.url:
        return handle_translator_url(t.translatorId, t.url)
    elif t.url:
        return handle_url(t.url)
    else:
        return {"error": "Specified Arguments not found"}


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    result = main()
    result = json.dumps(result)

    sys.stdout.write(str(result))
    sys.exit(0)

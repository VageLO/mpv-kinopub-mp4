import json
import os
from typing import Any

def read() -> Any:
    path = os.path.join(os.path.expanduser('~'), '.config', 'kinopub-history.json')
    if not os.path.exists(path):
        write({"search": {}, "shows": []})

    with open(path, 'r') as infile:
        try:
            return json.load(infile)
        except json.JSONDecodeError as e:
            raise Exception(e)

def write(data):
    path = os.path.join(os.path.expanduser('~'), '.config', 'kinopub-history.json')
    with open(path, 'w') as file:
        json.dump(data, file, indent=4)

def getExistedShowIndex(href):
    try:
        existing_data = read()
    except Exception as e:
        raise Exception(e)

    for index, show in enumerate(existing_data["shows"]):
        if show["href"] == href:
            return existing_data, index
    return existing_data, None 

def searchPhrase(phrase):
    try:
        data = read()
    except Exception as e:
        raise Exception(e)

    if phrase in data["search"]:
        return data["search"][phrase]
    else:
        raise Exception("No item found")

def searchShow(href):
    try:
        existing_data, index = getExistedShowIndex(href) 
    except Exception as e:
        raise Exception(e)

    if index is None:
        raise Exception("No item found")

    show = existing_data["shows"][index]

    if show["href"] == href:
        if "translators" in show:
            return {"translators": show["translators"]}
        elif "url" in show:
            return {"url": show["url"], "sub": show["sub"]} 

    raise Exception("No item found")

def searchSeason(href, translator_id):
    try:
        existing_data, index = getExistedShowIndex(href) 
    except Exception as e:
        raise Exception(e)

    if index is None:
        raise Exception("No item found")

    show = existing_data["shows"][index]

    if 'translators' not in show:
        raise Exception("No translators found")

    for translator in show["translators"]:
        if translator["id"] == translator_id:
            if 'seasons' in translator:
                return {"seasons": translator["seasons"]}
            else:
                return {"url": translator["url"], "sub": translator["sub"]}

    raise Exception("No item found")

def saveShow(data, href):
    try:
        existing_data, index = getExistedShowIndex(href) 
    except Exception as e:
        raise Exception(e)

    show = {
        "href": href,
    }

    if "translators" in data:
        show["translators"] = data["translators"]
    elif "url" in data:
        show["url"] = data["url"]
        if "sub" in data:
            show["sub"] = data["sub"]

    if index is not None:
        existing_data["shows"][index].update(show)
    else:
        existing_data["shows"].append(show)

    write(existing_data)

def saveSeasonsOfTranslator(data, href, translator_id):
    try:
        existing_data, show_index = getExistedShowIndex(href) 
    except Exception as e:
        print(e)
        raise Exception(e)

    if show_index is None:
        raise Exception("No item found")

    show = existing_data["shows"][show_index]

    if 'translators' not in show:
        raise Exception("No translators found")

    translator_index = None
    for idx, translator in enumerate(show["translators"]):
        if translator["id"] == translator_id:
            translator_index = idx
            break

    if translator_index is not None:
        show["translators"][translator_index].update(data)
        existing_data["shows"][show_index].update(show)
        write(existing_data)

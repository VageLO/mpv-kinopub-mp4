import requests
import json
import sys


def getNumberOfSeasons(tvShow):
    tvShowUrl = f"https://api.tvmaze.com/singlesearch/shows?q={tvShow}"

    # Get TVShow json data
    res = requests.get(tvShowUrl)
    show = res.json()

    # TVShow id
    showID = show["id"]

    res = requests.get(show["_links"]["previousepisode"]["href"])
    lastEpisode = res.json()

    return {
        "showID": showID,
        "seasons": lastEpisode["season"]
    }


def getNumberOfEpisodes(tvShowID, selectedSeason, part):

    url = f"https://api.tvmaze.com/shows/{tvShowID}/seasons"

    res = requests.get(url)
    seasons = res.json()

    numberEpisodesFromApi = 0
    for season in seasons:
        if season["number"] != selectedSeason:
            continue

        if season["episodeOrder"] is not None:
            numberEpisodesFromApi = season["episodeOrder"]
            break

        season_url = season["_links"]["self"]["href"]
        res = requests.get(f"{season_url}/episodes")
        episodes = res.json()

        numberEpisodesFromApi = len(episodes)
        break

    numberEpisodes = 0
    for num in range(1, numberEpisodesFromApi + 1):
        if num < 10:
            num = f'0{num}'
        url = f"https://s3.streamani.top/video1/BhcfuSh5dWKu9KmZ1jh_jg/1734188744/{part}/{selectedSeason}/original/{selectedSeason}{num}.mp4"
        res = requests.head(url)
        if res.status_code != 200:
            continue
        numberEpisodes += 1

    return {
        "episodes": numberEpisodes,
        "url": f"https://s3.streamani.top/video1/BhcfuSh5dWKu9KmZ1jh_jg/1734188744/{part}/{selectedSeason}/original/{selectedSeason}",
        "sub": f"https://{part}.mult-fan.tv/captions/eng/{selectedSeason}/"
    }


def main():
    try:
        args = sys.argv[1]
        args = json.loads(args)
    except Exception as e:
        return f'Error {e} {args} {sys.argv}'
    except json.JSONDecodeError:
        return f'Error: json decode {args}'

    result = {}

    if 'showID' in args:
        if 'selectedSeason' in args:
            result = getNumberOfEpisodes(
                args["showID"], args["selectedSeason"], args["part"])

    if 'show' in args:
        result = getNumberOfSeasons(args["show"])

    return result


if __name__ == '__main__':
    result = main()

    sys.stdout.write(str(result))
    sys.exit(0)

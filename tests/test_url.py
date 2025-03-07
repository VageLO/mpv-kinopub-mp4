import time
import pytest
from unittest.mock import patch
from kinopub import main

@pytest.mark.parametrize("show_url", [
    "https://kinopub.me/series/drama/55680-ukrytie-2023.html",
    "https://kinopub.me/series/thriller/646-vo-vse-tyazhkie-2008.html",
    "https://kinopub.me/series/drama/14806-vo-vse-tyazhkie-mini-epizody-2009.html",
    "https://kinopub.me/series/drama/7769-luchshe-zvonite-solu-2015.html",
    "https://kinopub.me/cartoons/comedy/49237-luchshe-zvonite-solu-predstavlyaet-paduchiy-dzhimmi-2022.html",
    "https://kinopub.me/series/action/32360-mandalorec-2019.html",
    "https://kinopub.me/series/documentary/34541-galereya-disney-mandalorec-2020.html",
    "https://kinopub.me/series/thriller/17109-ochen-strannye-dela-2016.html",
    "https://kinopub.me/series/action/32556-vedmak-2019.html",
    "https://kinopub.me/animation/adventures/40712-vedmak-koshmar-volka-2021.html",
    "https://kinopub.me/films/drama/882-rozhdestvenskiy-kottedzh-2008.html",
    "https://kinopub.me/films/drama/32863-rozhdestvenskiy-nastavnik-2019.html",
])

def test_url_success(show_url):
    # Test with sys.argv simulation
    with patch('sys.argv', ['kinopub.py', 'translator', '-u', show_url]):
        result = main()

        print(result)
        assert isinstance(result, dict), "Result should be a dict"
        assert (
            ('translators' in result) or 
            ('url' in result and result['url'] != "" and 'sub' in result)
        ), "Each item must have 'translators' or non-empty 'url' and 'sub'"
        time.sleep(2)

if __name__ == '__main__':
    pytest.main(['-v'])

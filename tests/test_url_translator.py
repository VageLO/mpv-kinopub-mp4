import time
import pytest
from unittest.mock import patch
from kinopub import main

@pytest.mark.parametrize("show_url_translator", [
    "https://kinopub.me/series/drama/55680-ukrytie-2023.html",
    "https://kinopub.me/series/thriller/646-vo-vse-tyazhkie-2008.html",
    "https://kinopub.me/series/drama/7769-luchshe-zvonite-solu-2015.html",
    "https://kinopub.me/films/drama/882-rozhdestvenskiy-kottedzh-2008.html",
    "https://kinopub.me/films/detective/1194-sem-1995.html",
])

def test_url_translator_success(show_url_translator):
    # Test with sys.argv simulation
    with patch('sys.argv', ['kinopub.py', 'translator', '-u', show_url_translator, '-ti', "238"]):
        result = main()

        print(result)

        assert isinstance(result, dict), "Result should be a dict"
        assert (
            ('seasons' in result) or 
            ('url' in result and result['url'] != "" and 'sub' in result)
        ), "Each item must have 'seasons' or both non-empty 'url' and 'sub'"
        time.sleep(2)

if __name__ == '__main__':
    pytest.main(['-v'])

import time
import pytest
from unittest.mock import patch
from kinopub import main

@pytest.mark.parametrize("show_url", [
    "https://kinopub.me/series/drama/55680-ukrytie-2023.html",
    "https://kinopub.me/series/thriller/646-vo-vse-tyazhkie-2008.html",
    "https://kinopub.me/series/drama/7769-luchshe-zvonite-solu-2015.html",
])

def test_url_source(show_url):
    # Test with sys.argv simulation
    with patch('sys.argv', [
        'kinopub.py',
        'translator',
        '-u', show_url,
        '-ti', '238',
        '-s', '1',
        '-e', '1'
    ]):
        result = main()

        assert isinstance(result, dict), "Result should be a dict"
        assert ('url' in result and result['url'] != "" and 'sub' in result)
        time.sleep(1)

if __name__ == '__main__':
    pytest.main(['-v'])

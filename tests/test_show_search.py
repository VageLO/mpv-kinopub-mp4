import pytest
from unittest.mock import patch
from kinopub import main

@pytest.mark.parametrize("show_title", [
    "Silo",
    "Breaking Bad",
    "Better Call Saul",
    "The Mandalorian",
    "Stranger Things",
    "The Witcher",
    "Christmas",
])

def test_show_search_success(show_title):
    # Test with sys.argv simulation
    with patch('sys.argv', ['kinopub.py', 'show', '-t', show_title]):
        result = main()
        print(result)

        assert isinstance(result, list)
        assert len(result) > 0
        assert all(item['title'] != "" for item in result)
        assert all('href' in item and item['href'].startswith('https://') for item in result)

def test_show_search_not_found():
    # Test with a deliberately obscure title that shouldn't exist
    with patch('sys.argv', ['kinopub.py', 'show', '-t', 'NonExistentShowXYZ123']):
        result = main()
        
        assert isinstance(result, dict)
        assert "error" in result
        assert result["error"] == "Can't find any show"

if __name__ == '__main__':
    pytest.main(['-v'])

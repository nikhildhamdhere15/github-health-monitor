import pytest
from src.ingestion.github_fetcher import GitHubFetcher

@pytest.fixture
def fetcher():
    return GitHubFetcher()

def test_fetcher_initialization(fetcher):
    """Test that fetcher initializes correctly"""
    assert fetcher.token is not None
    assert fetcher.base_url == 'https://api.github.com'

def test_get_repo_data(fetcher):
    """Test fetching repository data"""
    data = fetcher.get_repo_data('kubernetes', 'kubernetes')
    
    assert data is not None
    assert data['name'] == 'kubernetes'
    assert data['owner'] == 'kubernetes'
    assert 'stars' in data
    assert 'url' in data

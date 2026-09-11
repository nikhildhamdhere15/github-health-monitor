import requests
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, List, Optional

load_dotenv()

logger = logging.getLogger(__name__)

class GitHubFetcher:
    """Fetch data from GitHub API"""
    
    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GITHUB_TOKEN not found in .env")
        
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'
        self.rate_limit_remaining = None
    
    def _check_rate_limit(self):
        """Check GitHub API rate limit"""
        url = f'{self.base_url}/rate_limit'
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            remaining = data['rate']['remaining']
            limit = data['rate']['limit']
            logger.info(f"Rate limit: {remaining}/{limit}")
            return remaining > 0
        return False
    
    def get_repo_data(self, owner: str, repo: str) -> Optional[Dict]:
        """Get repository metadata"""
        url = f'{self.base_url}/repos/{owner}/{repo}'
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'name': data['name'],
                    'owner': data['owner']['login'],
                    'url': data['html_url'],
                    'stars': data['stargazers_count'],
                    'forks': data['forks_count'],
                    'watchers': data['watchers_count'],
                    'open_issues': data['open_issues_count'],
                    'last_push': data['pushed_at'],
                    'created_at': data['created_at'],
                    'description': data['description'],
                    'language': data['language'],
                    'license': data['license']['name'] if data['license'] else None,
                    'fetched_at': datetime.now().isoformat()
                }
            else:
                logger.error(f"Error {response.status_code}: {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"Error fetching repo data: {str(e)}")
            return None
    
    def get_commits(self, owner: str, repo: str, days: int = 30) -> List[Dict]:
        """Get commits from last N days"""
        url = f'{self.base_url}/repos/{owner}/{repo}/commits'
        
        try:
            since_date = datetime.now().isoformat()
            params = {
                'since': since_date,
                'per_page': 100
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return []
        
        except Exception as e:
            logger.error(f"Error fetching commits: {str(e)}")
            return []
    
    def get_issues(self, owner: str, repo: str) -> List[Dict]:
        """Get open issues"""
        url = f'{self.base_url}/repos/{owner}/{repo}/issues'
        
        try:
            params = {'state': 'open', 'per_page': 100}
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return []
        
        except Exception as e:
            logger.error(f"Error fetching issues: {str(e)}")
            return []
    
    def get_pull_requests(self, owner: str, repo: str) -> List[Dict]:
        """Get open pull requests"""
        url = f'{self.base_url}/repos/{owner}/{repo}/pulls'
        
        try:
            params = {'state': 'open', 'per_page': 100}
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return []
        
        except Exception as e:
            logger.error(f"Error fetching PRs: {str(e)}")
            return []
    
    def get_contributors(self, owner: str, repo: str) -> List[Dict]:
        """Get top contributors"""
        url = f'{self.base_url}/repos/{owner}/{repo}/contributors'
        
        try:
            params = {'per_page': 100}
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return []
        
        except Exception as e:
            logger.error(f"Error fetching contributors: {str(e)}")
            return []
    
    def get_releases(self, owner: str, repo: str) -> List[Dict]:
        """Get releases"""
        url = f'{self.base_url}/repos/{owner}/{repo}/releases'
        
        try:
            params = {'per_page': 100}
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return []
        
        except Exception as e:
            logger.error(f"Error fetching releases: {str(e)}")
            return []


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    fetcher = GitHubFetcher()
    
    # Test fetch
    data = fetcher.get_repo_data('kubernetes', 'kubernetes')
    print(f"Repo: {data['name']}")
    print(f"Stars: {data['stars']}")

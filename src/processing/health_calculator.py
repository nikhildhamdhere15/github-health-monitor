from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class HealthCalculator:
    """Calculate repository health metrics"""
    
    def __init__(self):
        pass
    
    def calculate_activity_score(self, last_push_date: str) -> float:
        """Score based on recency of activity (0-100)"""
        try:
            last_push = datetime.fromisoformat(last_push_date.replace('Z', '+00:00'))
            days_since_push = (datetime.now(last_push.tzinfo) - last_push).days
            
            if days_since_push < 7:
                return 100  # Very active
            elif days_since_push < 30:
                return 80   # Active
            elif days_since_push < 90:
                return 50   # Moderate
            elif days_since_push < 180:
                return 25   # Stale
            else:
                return 0    # Abandoned
        except Exception as e:
            logger.error(f"Error calculating activity score: {str(e)}")
            return 0
    
    def calculate_contributor_score(self, num_contributors: int) -> float:
        """Score based on contributor diversity (0-100)"""
        if num_contributors >= 100:
            return 100
        elif num_contributors >= 50:
            return 90
        elif num_contributors >= 20:
            return 80
        elif num_contributors >= 5:
            return 60
        elif num_contributors >= 2:
            return 40
        else:
            return 20  # Single contributor = risk
    
    def calculate_issue_score(self, open_issues: int, commits_30d: int) -> float:
        """Score based on issue management (0-100)"""
        if commits_30d == 0:
            return 0
        
        # Lower is better
        issue_to_commit_ratio = open_issues / max(commits_30d, 1)
        
        if issue_to_commit_ratio < 1:
            return 100
        elif issue_to_commit_ratio < 5:
            return 80
        elif issue_to_commit_ratio < 10:
            return 50
        else:
            return 20
    
    def calculate_release_score(self, num_releases_90d: int) -> float:
        """Score based on release frequency (0-100)"""
        if num_releases_90d >= 4:  # 1+ per month
            return 100
        elif num_releases_90d >= 2:
            return 80
        elif num_releases_90d >= 1:
            return 60
        else:
            return 30
    
    def calculate_popularity_score(self, stars: int) -> float:
        """Score based on stars (0-100)"""
        if stars >= 50000:
            return 100
        elif stars >= 10000:
            return 90
        elif stars >= 1000:
            return 80
        elif stars >= 100:
            return 60
        elif stars >= 10:
            return 40
        else:
            return 20
    
    def calculate_overall_health(self, metrics: dict) -> float:
        """Calculate overall health score (weighted average)"""
        weights = {
            'activity': 0.35,
            'contributors': 0.25,
            'issues': 0.20,
            'releases': 0.10,
            'popularity': 0.10
        }
        
        score = (
            metrics['activity_score'] * weights['activity'] +
            metrics['contributor_score'] * weights['contributors'] +
            metrics['issue_score'] * weights['issues'] +
            metrics['release_score'] * weights['releases'] +
            metrics['popularity_score'] * weights['popularity']
        )
        
        return round(score, 1)
    
    def get_health_status(self, score: float) -> str:
        """Get status label"""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        elif score >= 20:
            return "Poor"
        else:
            return "Critical"
    
    def calculate_all_metrics(self, repo_data: dict, commits: list, issues: list, 
                             prs: list, contributors: list, releases: list) -> dict:
        """Calculate all metrics at once"""
        
        num_commits_30d = len(commits)
        num_open_issues = len(issues)
        num_open_prs = len(prs)
        num_contributors = len(contributors)
        num_releases_90d = len([r for r in releases if 
                               (datetime.now() - datetime.fromisoformat(r['created_at'].replace('Z', '+00:00'))).days < 90])
        
        metrics = {
            'repo_name': f"{repo_data['owner']}/{repo_data['name']}",
            'url': repo_data['url'],
            'last_push': repo_data['last_push'],
            'commits_30d': num_commits_30d,
            'open_issues': num_open_issues,
            'open_prs': num_open_prs,
            'contributors': num_contributors,
            'stars': repo_data['stars'],
            'forks': repo_data['forks'],
            'activity_score': self.calculate_activity_score(repo_data['last_push']),
            'contributor_score': self.calculate_contributor_score(num_contributors),
            'issue_score': self.calculate_issue_score(num_open_issues, num_commits_30d),
            'release_score': self.calculate_release_score(num_releases_90d),
            'popularity_score': self.calculate_popularity_score(repo_data['stars']),
        }
        
        metrics['overall_health'] = self.calculate_overall_health(metrics)
        metrics['status'] = self.get_health_status(metrics['overall_health'])
        metrics['fetched_at'] = datetime.now().isoformat()
        
        return metrics

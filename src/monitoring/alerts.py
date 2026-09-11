import logging
from src.storage.database import HealthDatabase

logger = logging.getLogger(__name__)

class AlertSystem:
    """Generate alerts based on metrics"""
    
    def __init__(self):
        self.db = HealthDatabase()
    
    def check_abandoned(self, metrics: dict) -> tuple:
        """Check if repo is abandoned"""
        if metrics['activity_score'] < 20:
            return True, "Repository appears abandoned (no activity 6+ months)"
        return False, None
    
    def check_single_maintainer(self, metrics: dict) -> tuple:
        """Check if only 1 maintainer"""
        if metrics['contributors'] == 1:
            return True, "Single maintainer risk - no backup or succession plan"
        return False, None
    
    def check_pr_queue(self, metrics: dict) -> tuple:
        """Check if PR queue is growing"""
        if metrics['open_prs'] > 20:
            return True, f"Large PR queue ({metrics['open_prs']} open PRs) - review bottleneck"
        return False, None
    
    def check_issue_backlog(self, metrics: dict) -> tuple:
        """Check if issues are accumulating"""
        if metrics['commits_30d'] > 0:
            ratio = metrics['open_issues'] / metrics['commits_30d']
            if ratio > 10:
                return True, f"Large issue backlog - {metrics['open_issues']} issues, {ratio:.1f}x commits"
        return False, None
    
    def check_health_drop(self, repo_id: int, current_health: float, 
                         previous_health: float = None) -> tuple:
        """Check if health score dropped significantly"""
        if previous_health and (previous_health - current_health) > 20:
            drop = previous_health - current_health
            return True, f"Health score dropped {drop} points ({previous_health} → {current_health})"
        return False, None
    
    def generate_alerts(self, repo_id: int, metrics: dict) -> list:
        """Generate all applicable alerts"""
        alerts = []
        
        # Check abandonment
        is_abandoned, msg = self.check_abandoned(metrics)
        if is_abandoned:
            alerts.append((repo_id, 'abandonment', msg, 'critical'))
        
        # Check single maintainer
        is_single, msg = self.check_single_maintainer(metrics)
        if is_single:
            alerts.append((repo_id, 'single_maintainer', msg, 'warning'))
        
        # Check PR queue
        has_queue, msg = self.check_pr_queue(metrics)
        if has_queue:
            alerts.append((repo_id, 'pr_queue', msg, 'warning'))
        
        # Check issue backlog
        has_backlog, msg = self.check_issue_backlog(metrics)
        if has_backlog:
            alerts.append((repo_id, 'issue_backlog', msg, 'warning'))
        
        return alerts

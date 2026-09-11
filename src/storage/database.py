import sqlite3
import logging
from datetime import datetime
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

class HealthDatabase:
    """Store health metrics in SQLite"""
    
    def __init__(self, db_path: str = 'data/health_metrics.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Repositories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS repositories (
                id INTEGER PRIMARY KEY,
                owner TEXT NOT NULL,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                description TEXT,
                language TEXT,
                created_at DATETIME,
                UNIQUE(owner, name)
            )
        ''')
        
        # Health metrics table (time-series)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_metrics (
                id INTEGER PRIMARY KEY,
                repo_id INTEGER NOT NULL,
                overall_health REAL,
                activity_score REAL,
                contributor_score REAL,
                issue_score REAL,
                release_score REAL,
                popularity_score REAL,
                status TEXT,
                commits_30d INTEGER,
                open_issues INTEGER,
                open_prs INTEGER,
                contributors INTEGER,
                stars INTEGER,
                last_push DATETIME,
                fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(repo_id) REFERENCES repositories(id)
            )
        ''')
        
        # Alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY,
                repo_id INTEGER NOT NULL,
                alert_type TEXT,
                message TEXT,
                severity TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(repo_id) REFERENCES repositories(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized: {self.db_path}")
    
    def add_repository(self, owner: str, name: str, url: str, 
                      description: Optional[str], language: Optional[str]) -> int:
        """Add or update repository"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO repositories 
            (owner, name, url, description, language, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (owner, name, url, description, language, datetime.now()))
        
        conn.commit()
        repo_id = cursor.lastrowid
        conn.close()
        
        return repo_id
    
    def add_metrics(self, repo_id: int, metrics: dict) -> bool:
        """Add health metrics for a repository"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO health_metrics 
                (repo_id, overall_health, activity_score, contributor_score, 
                 issue_score, release_score, popularity_score, status,
                 commits_30d, open_issues, open_prs, contributors, stars, last_push)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                repo_id,
                metrics['overall_health'],
                metrics['activity_score'],
                metrics['contributor_score'],
                metrics['issue_score'],
                metrics['release_score'],
                metrics['popularity_score'],
                metrics['status'],
                metrics['commits_30d'],
                metrics['open_issues'],
                metrics['open_prs'],
                metrics['contributors'],
                metrics['stars'],
                metrics['last_push']
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding metrics: {str(e)}")
            return False
    
    def get_latest_metrics(self, owner: str, name: str) -> Optional[tuple]:
        """Get latest metrics for a repo"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT hm.* FROM health_metrics hm
            JOIN repositories r ON hm.repo_id = r.id
            WHERE r.owner = ? AND r.name = ?
            ORDER BY hm.fetched_at DESC
            LIMIT 1
        ''', (owner, name))
        
        result = cursor.fetchone()
        conn.close()
        
        return result
    
    def get_all_latest_metrics(self) -> List[tuple]:
        """Get latest metrics for all repos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.owner, r.name, r.url, hm.* 
            FROM health_metrics hm
            JOIN repositories r ON hm.repo_id = r.id
            WHERE hm.fetched_at = (
                SELECT MAX(fetched_at) FROM health_metrics WHERE repo_id = r.id
            )
            ORDER BY hm.overall_health DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def add_alert(self, repo_id: int, alert_type: str, message: str, 
                 severity: str = 'warning') -> bool:
        """Add alert for a repository"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alerts (repo_id, alert_type, message, severity)
                VALUES (?, ?, ?, ?)
            ''', (repo_id, alert_type, message, severity))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding alert: {str(e)}")
            return False

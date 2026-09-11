import pytest
from src.processing.health_calculator import HealthCalculator
from datetime import datetime, timedelta

@pytest.fixture
def calculator():
    return HealthCalculator()

def test_activity_score_recent(calculator):
    """Test activity score for recent activity"""
    recent_date = datetime.now().isoformat() + 'Z'
    score = calculator.calculate_activity_score(recent_date)
    assert score >= 80

def test_activity_score_abandoned(calculator):
    """Test activity score for abandoned repos"""
    old_date = (datetime.now() - timedelta(days=200)).isoformat() + 'Z'
    score = calculator.calculate_activity_score(old_date)
    assert score <= 25

def test_contributor_score(calculator):
    """Test contributor scoring"""
    assert calculator.calculate_contributor_score(100) == 100
    assert calculator.calculate_contributor_score(50) == 90
    assert calculator.calculate_contributor_score(1) == 20

def test_health_status(calculator):
    """Test health status determination"""
    assert calculator.get_health_status(90) == "Excellent"
    assert calculator.get_health_status(70) == "Good"
    assert calculator.get_health_status(50) == "Fair"
    assert calculator.get_health_status(25) == "Poor"
    assert calculator.get_health_status(10) == "Critical"

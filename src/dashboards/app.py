import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import logging

from src.ingestion.github_fetcher import GitHubFetcher
from src.processing.health_calculator import HealthCalculator
from src.storage.database import HealthDatabase
from src.monitoring.alerts import AlertSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Streamlit config
st.set_page_config(
    page_title="GitHub Health Monitor",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🔍 GitHub Repository Health Monitor")
st.markdown("Production-grade system to monitor repository health and detect risks")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    owner = st.text_input("Repository Owner", "kubernetes", key="owner")
    repo = st.text_input("Repository Name", "kubernetes", key="repo")
    
    col1, col2 = st.columns(2)
    with col1:
        fetch_btn = st.button("🔄 Fetch Data", use_container_width=True)
    with col2:
        view_all = st.button("📊 View All", use_container_width=True)

# Initialize components
fetcher = GitHubFetcher()
calculator = HealthCalculator()
db = HealthDatabase()
alert_system = AlertSystem()

# Main content
if fetch_btn:
    try:
        with st.spinner(f"Fetching data for {owner}/{repo}..."):
            # Fetch all data
            repo_data = fetcher.get_repo_data(owner, repo)
            if not repo_data:
                st.error(f"Repository not found: {owner}/{repo}")
            else:
                commits = fetcher.get_commits(owner, repo)
                issues = fetcher.get_issues(owner, repo)
                prs = fetcher.get_pull_requests(owner, repo)
                contributors = fetcher.get_contributors(owner, repo)
                releases = fetcher.get_releases(owner, repo)
                
                # Calculate metrics
                metrics = calculator.calculate_all_metrics(
                    repo_data, commits, issues, prs, contributors, releases
                )
                
                # Store in database
                repo_id = db.add_repository(
                    owner, repo, repo_data['url'],
                    repo_data['description'], repo_data['language']
                )
                db.add_metrics(repo_id, metrics)
                
                # Generate alerts
                alerts = alert_system.generate_alerts(repo_id, metrics)
                for alert in alerts:
                    db.add_alert(alert[0], alert[1], alert[2], alert[3])
                
                st.success(f"✅ Data fetched successfully for {owner}/{repo}")
                
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "📊 Health Score",
                        f"{metrics['overall_health']}",
                        f"Status: {metrics['status']}"
                    )
                
                with col2:
                    st.metric("👥 Contributors", metrics['contributors'])
                
                with col3:
                    st.metric("⭐ Stars", f"{metrics['stars']:,}")
                
                with col4:
                    st.metric("🍴 Forks", f"{metrics['forks']:,}")
                
                # Detailed metrics
                st.subheader("📈 Detailed Metrics")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Activity & Engagement**")
                    st.write(f"- Commits (30d): {metrics['commits_30d']}")
                    st.write(f"- Last Push: {metrics['last_push'][:10]}")
                    st.write(f"- Activity Score: {metrics['activity_score']}/100")
                
                with col2:
                    st.write("**Issues & PRs**")
                    st.write(f"- Open Issues: {metrics['open_issues']}")
                    st.write(f"- Open PRs: {metrics['open_prs']}")
                    st.write(f"- Issue Score: {metrics['issue_score']}/100")
                
                # Scores visualization
                st.subheader("📊 Score Breakdown")
                
                scores = {
                    'Activity': metrics['activity_score'],
                    'Contributors': metrics['contributor_score'],
                    'Issues': metrics['issue_score'],
                    'Releases': metrics['release_score'],
                    'Popularity': metrics['popularity_score']
                }
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=list(scores.keys()),
                        y=list(scores.values()),
                        marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
                    )
                ])
                fig.update_layout(
                    title="Repository Score Breakdown",
                    yaxis_title="Score (0-100)",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Alerts
                if alerts:
                    st.subheader("⚠️ Alerts")
                    for alert in alerts:
                        severity = alert[3]
                        message = alert[2]
                        
                        if severity == 'critical':
                            st.error(f"🔴 {message}")
                        else:
                            st.warning(f"🟡 {message}")
                
                # Repository info
                st.subheader("ℹ️ Repository Information")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Language**: {repo_data['language'] or 'N/A'}")
                
                with col2:
                    st.write(f"**License**: {repo_data['license'] or 'None'}")
                
                with col3:
                    st.write(f"**Created**: {repo_data['created_at'][:10]}")
                
                st.write(f"**Description**: {repo_data['description'] or 'No description'}")
                st.write(f"**URL**: {repo_data['url']}")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        logger.error(f"Error fetching data: {str(e)}")

elif view_all:
    st.subheader("📋 All Monitored Repositories")
    
    try:
        all_metrics = db.get_all_latest_metrics()
        
        if all_metrics:
            # Convert to DataFrame
            df_data = []
            for metric in all_metrics:
                df_data.append({
                    'Owner': metric[0],
                    'Repo': metric[1],
                    'Health Score': metric[14],
                    'Status': metric[19],
                    'Contributors': metric[22],
                    'Stars': metric[23],
                    'Activity': metric[15],
                    'Issues': metric[17]
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No repositories monitored yet. Fetch data to get started!")
    
    except Exception as e:
        st.error(f"Error loading repositories: {str(e)}")

else:
    st.info("👈 Enter a repository name in the sidebar and click 'Fetch Data' to get started!")
    
    st.markdown("""
    ### Quick Start
    1. Enter repository owner (e.g., `kubernetes`)
    2. Enter repository name (e.g., `kubernetes`)
    3. Click **Fetch Data**
    4. View health metrics and alerts
    
    ### What This Shows
    - **Health Score**: Overall repository health (0-100)
    - **Activity Score**: Recency of commits and pushes
    - **Contributor Score**: Diversity of contributors
    - **Issue Score**: Issue management efficiency
    - **Release Score**: Release frequency
    - **Popularity Score**: Community interest (stars)
    """)

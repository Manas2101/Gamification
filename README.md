# 🚀 DevOps Gamification Dashboard

A stunning, modern gamification dashboard for tracking DevOps team performance with beautiful animations, interactive elements, and real-time metrics.

## ✨ Features

- **🎨 Modern UI Design**: Beautiful gradient backgrounds, glassmorphism effects, and smooth animations
- **🏆 Podium Display**: Animated podium showcasing top 3 performing teams
- **📊 Interactive Metrics**: Real-time performance tracking with animated progress bars
- **🎖️ Achievement Badges**: Earn badges for excellence in specific metrics
- **📈 Trend Analysis**: Visual performance trends over the last 5 weeks
- **🎯 Team Deep Dive**: Detailed analytics for individual team performance
- **💫 Animations**: Smooth transitions, hover effects, and engaging visual feedback

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run app.py
```

3. Open your browser and navigate to the URL shown in the terminal (typically `http://localhost:8501`)

## 🎮 How to Use

1. **Overview Tab**: View overall performance metrics and team statistics
2. **Leaderboard Tab**: See rankings with podium display for top performers
3. **Badges Tab**: Track achievements and top/bottom performing teams
4. **Team Tab**: Deep dive into individual team performance
5. **Docs Tab**: Learn about scoring rules and how to use the dashboard

## 📊 Scoring System

- **Velocity (RF)**: 35 points - Release Frequency target: 280
- **Flow (LTDD)**: 25 points - Lead Time target: <2 days
- **Stability**: 20 points - CFR, MTTR, and Privileged Access
- **Automation**: 20 points - CI/CD, IaC, Rollback, Self-service

## 🎖️ Available Badges

- 🏆 **Release Champion**: RF ≥ 250
- ⚡ **High Velocity**: RF ≥ 180
- 💨 **Flow Master**: LTDD < 2 days
- 🛡️ **Stability Shield**: CFR < 5%
- 🤖 **Automation Pro**: Full automation coverage

## 🎨 Design Highlights

- Custom Poppins font for modern typography
- Gradient backgrounds with purple/blue theme
- Glassmorphism cards with backdrop blur
- Smooth CSS animations and transitions
- Responsive layout for all screen sizes
- Interactive hover effects throughout

## 📁 File Structure

- `app.py` - Main application with all UI enhancements
- `requirements.txt` - Python dependencies
- `metrics_history.csv` - Auto-generated sample data (70 teams, 5 weeks)

## 🔄 Data Upload

Upload your team data via the sidebar:
1. Prepare CSV with required columns
2. Upload and validate
3. Publish to add to history
4. Data persists across sessions

Enjoy your gamified DevOps transformation journey! 🎉


python3 -c "import sqlite3; conn = sqlite3.connect('metrics.db'); cursor = conn.cursor(); cursor.execute('SELECT pod_id, rf, lttd, cfr, mttr, rf_score, flow_score, cfr_score, mttr_score, dpi FROM weekly_metrics LIMIT 5'); print('pod_id | rf | lttd | cfr | mttr | rf_score | flow_score | cfr_score | mttr_score | dpi'); print('-' * 100); [print(f'{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]} | {row[7]} | {row[8]} | {row[9]}') for row in cursor.fetchall()]; conn.close()"
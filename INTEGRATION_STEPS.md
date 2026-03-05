Complete Setup and Run Instructions
Here are all the commands you need to run, line by line:

Step 1: Navigate to Project Directory
bash
cd /Users/kritikapandey/Desktop/Gamification
Step 2: Install Python Dependencies
bash
pip install -r requirements.txt
Or if you're using pip3:

bash
pip3 install -r requirements.txt
Step 3: Create .env File with Your Bearer Tokens
bash
cp .env.example .env
Now edit the .env file:

bash
nano .env
Add your actual bearer tokens (replace the placeholder values):

env
TEAMBOOK_BEARER_TOKEN=your_actual_teambook_token_here
DATASIGHT_BEARER_TOKEN=your_actual_datasight_token_here
MAX_WEEKS_TO_KEEP=5
DB_PATH=metrics.db
SERVICE_LINE_ID=449
Save and exit:

Press Ctrl + O (save)
Press Enter (confirm)
Press Ctrl + X (exit)
Step 4: Initialize Database and Fetch Initial Data
bash
python setup_database.py
Or:

bash
python3 setup_database.py
Follow the interactive prompts:

Press Enter to continue
Enter your bearer token when asked (or it will use from .env)
Choose y to fetch data now
Choose y to backfill historical data (optional)
Enter number of months (e.g., 3)
Step 5: Run the Streamlit Dashboard
bash
streamlit run app.py
The dashboard will open automatically in your browser at http://localhost:8501

Step 6: (Optional) Set Up Weekly Auto-Refresh
For Mac/Linux - Using Cron:
bash
crontab -e
Add this line (runs every Monday at 9 AM):

cron
0 9 * * 1 cd /Users/kritikapandey/Desktop/Gamification && /usr/local/bin/python3 weekly_refresh.py >> weekly_refresh.log 2>&1
Save and exit (:wq if using vim, or Ctrl+O then Ctrl+X if using nano)

Quick Reference Commands
Manual Data Refresh (anytime):
bash
python weekly_refresh.py
Check Database Contents:
bash
python -c "from database import MetricsDatabase; db = MetricsDatabase(); print(db.get_latest_metrics())"
Verify Tokens are Loaded:
bash
python -c "import config; print('TeamBook:', bool(config.TEAMBOOK_BEARER_TOKEN)); print('DataSight:', bool(config.DATASIGHT_BEARER_TOKEN))"
Check How Many Weeks are Stored:
bash
python -c "from database import MetricsDatabase; import sqlite3; db = MetricsDatabase(); conn = sqlite3.connect(db.db_path); weeks = conn.execute('SELECT DISTINCT week_date FROM weekly_metrics ORDER BY week_date DESC').fetchall(); print(f'Weeks: {len(weeks)}'); [print(w[0]) for w in weeks]; conn.close()"
Troubleshooting
If you get "Module not found" error:
bash
pip install streamlit pandas numpy requests python-dotenv
If database is locked:
bash
rm metrics.db
python setup_database.py
If you need to clear cache:
In the dashboard sidebar, click "Clear Cache" button

Summary of What Happens:
✅ Dependencies installed
✅ .env file created with your tokens
✅ Database initialized (metrics.db)
✅ Initial data fetched from APIs
✅ Dashboard running at http://localhost:8501
✅ Weekly auto-refresh (if cron set up)
✅ Only last 5 weeks kept automatically
Your dashboard is now live with real-time API data! 🎉
import sqlite3 # Using SQLite for local development instead of PostgreSQL
import urllib.parse # For URL manipulation
from fastapi import FastAPI, HTTPException, Request # For handling incoming requests and errors
from fastapi.responses import RedirectResponse # For redirecting users to the target URL
from datetime import datetime # For timestamping click events

app = FastAPI(title="AkadVerse Resource Tracker")

DB_FILE = "tracker_logs.db"

def setup_database():
    """
    Initializes the SQLite database to store our click events.
    This acts as our PostgreSQL replacement for local development.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # Create a table for logging click events
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS click_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                target_url TEXT NOT NULL,
                source_page TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        print("Database setup complete.")
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")

# Run the database setup when the file is loaded
setup_database()

@app.get("/redirect")
async def handle_redirect(target_url: str, user_id: str, source: str):
    """
    Captures the click event, logs it to the database, and redirects the user.
    """
    try:
        # 1. Log the event to our database
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO click_events (user_id, target_url, source_page, timestamp) VALUES (?, ?, ?, ?)",
            (user_id, target_url, source, now)
        )
        conn.commit()
        conn.close()
        
        print(f"Logged click: User '{user_id}' clicked '{target_url}' from '{source}'")

        # 2. Append UTM(Urchin Tracking Module) parameters to the target URL for conversion tracking
        # This tells the external site that AkadVerse sent the traffic
        parsed_url = urllib.parse.urlparse(target_url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Add our custom tracking tags
        query_params['utm_source'] = ['akadverse']
        query_params['utm_medium'] = ['platform_redirect']
        query_params['utm_campaign'] = [source]
        
        # Rebuild the final URL
        new_query = urllib.parse.urlencode(query_params, doseq=True)
        final_url = urllib.parse.urlunparse((
            parsed_url.scheme, 
            parsed_url.netloc, 
            parsed_url.path, 
            parsed_url.params, 
            new_query, 
            parsed_url.fragment
        ))
        
        # 3. Redirect the user seamlessly
        return RedirectResponse(url=final_url, status_code=307)

    except sqlite3.Error as e:
        # If the database fails, we should still try to redirect the user so their experience isn't broken
        print(f"Database error during logging: {e}")
        return RedirectResponse(url=target_url, status_code=307)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redirect service failed: {str(e)}")

@app.get("/analytics/clicks")
async def get_click_stats():
    """
    A simple admin endpoint to view all tracked clicks.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM click_events ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()
        
        # Format the output into a clean list of dictionaries
        results = [
            {"id": row[0], "user_id": row[1], "target_url": row[2], "source_page": row[3], "timestamp": row[4]}
            for row in rows
        ]
        return {"total_clicks": len(results), "data": results}
        
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    #binding the microservice to port 8006
    uvicorn.run(app, host="127.0.0.1", port=8006)
    
# run with:  uvicorn main:app --host 127.0.0.1 --port 8006 --reload
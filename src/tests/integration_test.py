import unittest
import os
import sys
import json
import sqlite3

# --- SETUP PATHS ---
# Add 'src' to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import database
import app
from collector import collector
from analyzer import analyzer

class GridironIntegrationTest(unittest.TestCase):
    
    def setUp(self):
        """
        Runs BEFORE every test.
        Switches the database to a temporary test file.
        """
        # Point the database to a test file
        self.test_db_path = os.path.join(os.path.dirname(__file__), 'test_fieldvision.db')
        database.DB_PATH = self.test_db_path
        
        # Initialize the fresh test DB
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        database.init_db()

        # Setup the Flask Test Client
        self.app = app.app.test_client()
        self.app.testing = True

    def tearDown(self):
        """
        Runs AFTER every test.
        Cleans up the file system.
        """
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_full_pipeline(self):
        """
        Tests the entire flow: Collector -> DB -> Analyzer -> API
        """
        print("\n--- Running Integration Test: Full Pipeline ---")

        # Instead of hitting the real API, we force the collector to use mock data.
        print("1. Running Collector...")
        
        # Override the API Key to force the 'Mock Data' path in your collector.py
        original_key = collector.API_KEY
        collector.API_KEY = "TEST_KEY_FORCE_MOCK" 
        
        # Run the actual collector function
        collector.collect_and_save()
        
        # Restore key
        collector.API_KEY = original_key

        # Verify if raw data is in the DB
        conn = database.get_db_connection()
        raw_count = conn.execute("SELECT count(*) FROM raw_weather").fetchone()[0]
        self.assertGreater(raw_count, 0, "Collector failed to save raw data to DB")
        print(f"   (Pass) Collector saved {raw_count} records.")

        # Analyze the mock data
        print("2. Running Analyzer...")
        analyzer.run_analysis()

        # Verify if refined risk scores appear
        risk_count = conn.execute("SELECT count(*) FROM game_risk").fetchone()[0]
        self.assertGreater(risk_count, 0, "Analyzer failed to save risk scores")
        print(f"   (Pass) Analyzer generated {risk_count} risk records.")
        conn.close()

        # Query the Web API
        print("3. Testing Web API Endpoint...")
        response = self.app.get('/api/risk')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check Business Logic
        # Our mock data in collector.py had High Wind (22mph) and Cold Temp (25.5F).
        # So we expect the analyzer to have labeled it "HIGH" or "MEDIUM".
        first_game = data[0]
        print(f"   API Returned: {first_game['team']} -> Risk: {first_game['risk_label']}")
        
        self.assertIn(first_game['risk_label'], ['HIGH', 'MEDIUM'])
        self.assertTrue(first_game['risk_score'] > 0)
        
        print("--- Integration Test Passed! ---")

if __name__ == '__main__':
    unittest.main()
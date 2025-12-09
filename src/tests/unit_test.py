import unittest
import sys
import os
import json

# --- PATH SETUP ---
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from analyzer import analyzer

class TestAnalyzerLogic(unittest.TestCase):

    # --- 1. BASIC LOGIC TESTS ---

    def test_perfect_weather(self):
        """Test: Ideal conditions (72F, 5mph wind) = 0 Risk."""
        raw_json = json.dumps({
            "list": [{
                "main": {"temp": 72.0},
                "wind": {"speed": 5.0},
                "weather": [{"description": "Clear sky"}]
            }]
        })
        score, label, details = analyzer.analyze_weather(raw_json)
        self.assertEqual(score, 0)
        self.assertEqual(label, "LOW")

    def test_high_wind_only(self):
        """Test: Wind > 20mph = 80 Risk (High)."""
        raw_json = json.dumps({
            "list": [{
                "main": {"temp": 50.0},
                "wind": {"speed": 25.0}, 
                "weather": [{"description": "Windy"}]
            }]
        })
        score, label, details = analyzer.analyze_weather(raw_json)
        self.assertEqual(score, 80)
        self.assertEqual(label, "HIGH")

    def test_freezing_only(self):
        """Test: Temp < 32F = 10 Risk (Low/Medium depending on logic)."""
        raw_json = json.dumps({
            "list": [{
                "main": {"temp": 30.0}, 
                "wind": {"speed": 5.0},
                "weather": [{"description": "Snow"}]
            }]
        })
        score, label, details = analyzer.analyze_weather(raw_json)
        self.assertEqual(score, 10)
        # 10 is < 20, so it should still be LOW
        self.assertEqual(label, "LOW") 

    # --- 2. MIXED CONDITION TESTS ---

    def test_blizzard_conditions(self):
        """Test: High Wind (80) + Deep Freeze (30) = 110 -> Cap at 100."""
        # Wind 35mph (+80)
        # Temp 5F    (+30)
        # Total calc = 110, Should cap at 100
        raw_json = json.dumps({
            "list": [{
                "main": {"temp": 5.0},
                "wind": {"speed": 35.0},
                "weather": [{"description": "Blizzard"}]
            }]
        })
        score, label, details = analyzer.analyze_weather(raw_json)
        self.assertEqual(score, 100) # Must cap at 100
        self.assertEqual(label, "HIGH")
        self.assertTrue("Extreme Wind" in details and "Deep Freeze" in details)

    def test_moderate_mix(self):
        """Test: Medium Wind (40) + Freezing (10) = 50 Risk (High)."""
        # Wind 18mph (+40)
        # Temp 30F   (+10)
        # Total = 50
        raw_json = json.dumps({
            "list": [{
                "main": {"temp": 30.0},
                "wind": {"speed": 18.0},
                "weather": [{"description": "Chilly Breeze"}]
            }]
        })
        score, label, details = analyzer.analyze_weather(raw_json)
        self.assertEqual(score, 50)
        self.assertEqual(label, "HIGH")

    # --- 3. BOUNDARY / EDGE CASE TESTS ---

    def test_exact_boundaries(self):
        """Test: Exactly 15mph wind (Should be safe) vs 15.1mph (Risk)."""
        # Case A: Exactly 15.0 mph -> Score 0
        json_safe = json.dumps({"list": [{"main": {"temp": 60}, "wind": {"speed": 15.0}, "weather": [{"description": "ok"}]}]})
        score, _, _ = analyzer.analyze_weather(json_safe)
        self.assertEqual(score, 0, "15.0 mph should be safe")

        # Case B: 15.1 mph -> Score 40
        json_risk = json.dumps({"list": [{"main": {"temp": 60}, "wind": {"speed": 15.1}, "weather": [{"description": "ok"}]}]})
        score, _, _ = analyzer.analyze_weather(json_risk)
        self.assertEqual(score, 40, "15.1 mph should trigger wind risk")

    def test_zero_values(self):
        """Test: 0 Wind and 0 Temp."""
        # Wind 0 is safe. Temp 0 is Deep Freeze (+30).
        raw_json = json.dumps({
            "list": [{
                "main": {"temp": 0.0},
                "wind": {"speed": 0.0},
                "weather": [{"description": "Still Cold"}]
            }]
        })
        score, label, _ = analyzer.analyze_weather(raw_json)
        self.assertEqual(score, 30)
        self.assertEqual(label, "MEDIUM")

    # --- 4. DATA INTEGRITY TESTS ---

    def test_missing_fields(self):
        """Test: Partial JSON where 'wind' exists but 'speed' is missing."""
        # Use the Standard Nested format but omit specific keys
        # This will trigger the KeyError and fall into the 'Mock' check
        # Since it's not a mock, it should return Parse Error
        raw_json = json.dumps({
            "list": [{
                "main": {"temp": 70},
                "wind": {}, # Missing speed!
                "weather": [{"description": "Error"}]
            }]
        })
        score, label, details = analyzer.analyze_weather(raw_json)
        self.assertEqual(score, 0)
        self.assertEqual(label, "Unknown")
        self.assertEqual(details, "Parse Error")

    def test_malformed_json_string(self):
        """Test: Input is not even valid JSON."""
        # analyzer.analyze_weather expects a valid JSON string
        # json.loads() will raise JSONDecodeError.
        # Ideally, our function might not handle this, so let's see if it crashes.
        # A robust function would catch this, but currently ours lets it crash.
        # We will wrap it in assertRaises to prove it fails as expected.
        with self.assertRaises(ValueError):
            analyzer.analyze_weather("{ bad json ")

    def test_mock_fallback_structure(self):
        """Test: Ensure the flat Mock fallback still works."""
        raw_json = json.dumps({
            "mock": True,
            "wind": 22.0,
            "temp": 70.0
        })
        score, label, _ = analyzer.analyze_weather(raw_json)
        self.assertEqual(score, 80) # High Wind

if __name__ == '__main__':
    unittest.main()
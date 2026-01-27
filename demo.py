#!/usr/bin/env python3
"""
Demo script to simulate various load scenarios
Shows how the AI predicts different power modes
"""

import requests
import time

SERVER_URL = "http://localhost:5000/predict"

def test_scenario(name, process_count, cpu_usage):
    """Test a specific scenario"""
    print(f"\n{'='*60}")
    print(f"🧪 Testing: {name}")
    print(f"{'='*60}")
    print(f"📊 Input: {process_count} processes, {cpu_usage}% CPU")
    
    try:
        response = requests.post(
            SERVER_URL,
            json={"process_count": process_count, "cpu_usage": cpu_usage},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Prediction: {data['mode']}")
            print(f"   Nice Value: {data['nice']}")
            print(f"   Stress Score: {data['stress_score']:.3f}")
            return True
        else:
            print(f"❌ Server error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Start it with: python3 master_server.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🎯 AI Battery Saver - Demo Scenarios")
    print("Make sure master_server.py is running!")
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    scenarios = [
        ("Idle System (Low Load)", 50, 10.0),
        ("Light Usage (Web Browsing)", 100, 30.0),
        ("Moderate Load (Multi-tasking)", 150, 50.0),
        ("Heavy Load (Development)", 200, 70.0),
        ("Critical Load (Compilation)", 250, 90.0),
        ("Extreme Load (Stress Test)", 300, 100.0),
    ]
    
    print("\n" + "="*60)
    print("Running 6 test scenarios...")
    print("="*60)
    
    for scenario in scenarios:
        if not test_scenario(*scenario):
            print("\n❌ Demo stopped due to error")
            break
        time.sleep(2)
    
    print("\n" + "="*60)
    print("✅ Demo complete!")
    print("="*60)
    print("\n📊 View results on dashboard: http://localhost:5000")
    print("📜 Check prediction history for all test results")

if __name__ == "__main__":
    main()


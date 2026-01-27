#!/usr/bin/env python3
"""
AI Battery Agent - Sends system stats to master server
Runs on Ubuntu VM and communicates with kernel module
"""

import requests
import time
import subprocess
import re

MASTER_SERVER = "http://localhost:5000/predict"
PROC_STATS = "/proc/ai_battery_stats"
PROC_CONTROL = "/proc/ai_battery_control"

def get_cpu_usage():
    """Get current CPU usage percentage"""
    try:
        # Read /proc/stat for CPU usage
        with open('/proc/stat', 'r') as f:
            cpu_line = f.readline()
            cpu_values = [int(x) for x in cpu_line.split()[1:]]
            
            # Calculate CPU usage
            idle = cpu_values[3]
            total = sum(cpu_values)
            
            time.sleep(0.1)
            
            # Read again
            f.seek(0)
            cpu_line = f.readline()
            cpu_values2 = [int(x) for x in cpu_line.split()[1:]]
            
            idle2 = cpu_values2[3]
            total2 = sum(cpu_values2)
            
            # Calculate percentage
            total_diff = total2 - total
            idle_diff = idle2 - idle
            
            if total_diff == 0:
                return 0.0
            
            usage = 100.0 * (1.0 - idle_diff / total_diff)
            return max(0.0, min(100.0, usage))
    except Exception as e:
        print(f"⚠️ Error getting CPU usage: {e}")
        return 0.0

def get_process_count():
    """Get number of running processes from kernel module"""
    try:
        with open(PROC_STATS, 'r') as f:
            content = f.read()
            # Parse: "Number of running processes: 123"
            match = re.search(r'Number of running processes: (\d+)', content)
            if match:
                return int(match.group(1))
    except Exception as e:
        print(f"⚠️ Error reading kernel module: {e}")
        print(f"   Make sure kernel module is loaded: sudo insmod ai_battery_module.ko")
    
    # Fallback: count from /proc
    try:
        proc_count = len([d for d in os.listdir('/proc') if d.isdigit()])
        return proc_count
    except:
        return 0

def send_to_master(process_count, cpu_usage):
    """Send stats to master server and get prediction"""
    try:
        payload = {
            "process_count": process_count,
            "cpu_usage": cpu_usage
        }
        
        response = requests.post(MASTER_SERVER, json=payload, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"❌ Server error: {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to master server. Is it running?")
        return None
    except Exception as e:
        print(f"❌ Error sending data: {e}")
        return None

def apply_mode(mode):
    """Write mode to kernel module control interface"""
    try:
        with open(PROC_CONTROL, 'w') as f:
            f.write(mode)
        print(f"✅ Applied mode to kernel: {mode}")
        return True
    except Exception as e:
        print(f"⚠️ Could not write to kernel module: {e}")
        return False

def main():
    print("🤖 AI Battery Agent Starting...")
    print(f"📡 Master Server: {MASTER_SERVER}")
    print(f"📊 Kernel Stats: {PROC_STATS}")
    print(f"🎛️  Kernel Control: {PROC_CONTROL}")
    print("-" * 50)
    
    iteration = 0
    
    while True:
        try:
            iteration += 1
            
            # Get system stats
            process_count = get_process_count()
            cpu_usage = get_cpu_usage()
            
            print(f"\n[{iteration}] 📊 Processes: {process_count}, CPU: {cpu_usage:.1f}%")
            
            # Send to master server
            prediction = send_to_master(process_count, cpu_usage)
            
            if prediction:
                mode = prediction['mode']
                nice = prediction['nice']
                
                print(f"   🎯 Prediction: {mode} (nice={nice})")
                
                # Apply to kernel module
                apply_mode(mode)
            
            # Wait before next iteration
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\n\n👋 Agent stopped by user")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    import os
    main()


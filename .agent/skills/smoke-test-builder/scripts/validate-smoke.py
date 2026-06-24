import sys
import json
import time

def check_smoke_duration(steps_file):
    """
    Parses a JSON/CSV list of steps and flags any steps exceeding 15 seconds.
    Ensures the total execution time is under 5 minutes (300 seconds).
    """
    try:
        with open(steps_file, 'r') as f:
            data = json.load(f)
        
        total_duration = 0
        slow_steps = []
        
        for step in data.get("steps", []):
            duration = step.get("duration_seconds", 0)
            total_duration += duration
            if duration > 15:
                slow_steps.append((step.get("name"), duration))
                
        print(f"Total Smoke Test Duration: {total_duration}s")
        if total_duration > 300:
            print("WARNING: Total smoke test duration exceeds 5 minutes limit!")
            
        if slow_steps:
            print("Slow steps detected (>15s):")
            for name, dur in slow_steps:
                print(f"  - {name}: {dur}s")
                
        return total_duration <= 300
    except Exception as e:
        print(f"Error parsing steps: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate-smoke.py <steps.json>")
        sys.exit(1)
    
    success = check_smoke_duration(sys.argv[1])
    sys.exit(0 if success else 1)
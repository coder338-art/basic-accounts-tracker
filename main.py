import json
import sys
from monitor import run_monitor

def load_config(path="config.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to load config: {e}")
        return {}

def main():
    config = load_config()
    if not config:
        print("No valid config found. Create config.json and try again.")
        sys.exit(1)
    run_monitor(config)

if __name__ == "__main__":
    main()

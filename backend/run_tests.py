import os
import subprocess
import datetime

def main():
    print("Running tests...")
    result = subprocess.run(
        ["python", "-m", "pytest", "-v", "tests/"],
        capture_output=True,
        text=True
    )
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summary = result.stdout
    
    md_content = f"""# Test Results

**Run Date:** {timestamp}
**Status:** {'PASS' if result.returncode == 0 else 'FAIL'}

## Log Output
```
{summary}
```
"""
    
    with open("TEST_RESULTS.md", "w", encoding="utf-8") as f:
        f.write(md_content)
        
    with open("test_results.txt", "w", encoding="utf-8") as f:
        f.write(summary)
        
    print(f"Tests finished. Generated TEST_RESULTS.md and test_results.txt.")
    print("Return code:", result.returncode)

if __name__ == "__main__":
    main()

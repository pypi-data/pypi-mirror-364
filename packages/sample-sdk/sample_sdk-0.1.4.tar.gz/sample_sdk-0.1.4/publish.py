import os
import subprocess
import sys

def publish_package():
    # Get token from environment variable or prompt user
    token = os.getenv("PYPI_TOKEN")
    if not token:
        print("PYPI_TOKEN environment variable not set.")
        print("Please set it with: $env:PYPI_TOKEN='your_token'")
        print("Or enter your token now:")
        token = input("Token: ").strip()
    
    if not token:
        print("No token provided. Exiting.")
        sys.exit(1)
    
    print(f"Token loaded: {token[:20]}...")
    
    # Clear any conflicting environment variables
    env = os.environ.copy()
    env.pop("UV_PUBLISH_USERNAME", None)
    env.pop("UV_PUBLISH_PASSWORD", None)
    
    # Run uv publish with token only
    result = subprocess.run(
        ["uv", "publish", "--token", token], 
        capture_output=True, 
        text=True,
        env=env
    )
    
    return result

if __name__ == "__main__":
    result = publish_package()
    
    # Print output
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    print("Return code:", result.returncode)

# Print output
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode) 
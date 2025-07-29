import os
import subprocess

# Set the token directly
token = "pypi-AgEIcHlwaS5vcmcCJGUwNzZmZmIwLWQzMDUtNGNlMC04NjBiLWVlYTIzOGViNTQ0NAACKlszLCJlOTcwNmY4Zi0xYzVjLTQyYjgtOTI4Ny0zMDIyNGUxYzcyOTQiXQAABiCGlQnFaWD-Tmj3_tKZt-6hLgpZxkUc_UnTSxk307GOUw"

print(f"Token loaded: {token[:20]}...")

# Run uv publish with token only
result = subprocess.run(["uv", "publish", "--token", token], capture_output=True, text=True)

# Print output
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode) 
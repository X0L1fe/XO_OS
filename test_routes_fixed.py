from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Get OpenAPI schema
response = client.get("/openapi.json")
if response.status_code == 200:
    schema = response.json()
    paths = schema.get("paths", {})
    print("Available paths:")
    for path in sorted(paths.keys()):
        print(f"  {path}")
    # Check for the four expected paths
    expected = [
        "/api/export",
        "/api/obsidian/status",
        "/api/obsidian/path",
    ]
    print("\nChecking expected paths:")
    for exp in expected:
        if exp in paths:
            print(f"  [FOUND] {exp}")
            # Show methods for this path
            methods = list(paths[exp].keys())
            print(f"        Methods: {', '.join(methods).upper()}")
        else:
            print(f"  [MISSING] {exp}")
else:
    print("Failed to get OpenAPI schema")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
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
            print(f"  ✓ {exp}")
        else:
            print(f"  ✗ {exp} (missing)")
    # Also check for POST on /api/obsidian/path
    if "/api/obsidian/path" in paths:
        methods = paths["/api/obsidian/path"]
        if "post" in methods:
            print("  ✓ POST /api/obsidian/path")
        else:
            print("  ✗ POST /api/obsidian/path (missing)")
else:
    print("Failed to get OpenAPI schema")

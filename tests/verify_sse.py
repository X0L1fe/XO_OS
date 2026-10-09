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
    # Check for the SSE path
    expected = "/api/events"
    if expected in paths:
        print(f"\n[FOUND] {expected}")
        # Show methods for this path
        methods = list(paths[expected].keys())
        print(f"    Methods: {', '.join(methods).upper()}")
        # Check that it's exactly one (no duplicate with different path)
        # Also check that there's no other path that maps to the same function? Not needed.
    else:
        print(f"\n[MISSING] {expected}")
else:
    print("Failed to get OpenAPI schema")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
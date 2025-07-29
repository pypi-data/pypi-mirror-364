from dataclasses import dataclass
from autocrud import AutoCRUD, MemoryStorage
from fastapi.testclient import TestClient


@dataclass
class TestItem:
    name: str
    value: int


storage = MemoryStorage()
crud = AutoCRUD(model=TestItem, storage=storage, resource_name="items")

# 建立項目
crud.create({"name": "item1", "value": 1})
crud.create({"name": "item2", "value": 2})

app = crud.create_fastapi_app()

print("Routes:")
for route in app.routes:
    if hasattr(route, "methods") and hasattr(route, "path"):
        for method in route.methods:
            if method not in ["HEAD", "OPTIONS"]:
                print(f"{method} {route.path}")

# 測試 API
client = TestClient(app)

print("\nTesting count endpoint:")
response = client.get("/api/v1/items/count")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

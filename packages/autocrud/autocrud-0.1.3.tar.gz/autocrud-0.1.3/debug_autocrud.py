#!/usr/bin/env python3

from tests.test_models import Product
from autocrud import SingleModelCRUD, MemoryStorage
from autocrud.metadata import MetadataConfig

# 創建 SingleModelCRUD
storage = MemoryStorage()
metadata_config = MetadataConfig(id_field="id")
crud = SingleModelCRUD(
    model=Product,
    storage=storage,
    resource_name="products",
    metadata_config=metadata_config,
)

print("Field types in schema analyzer:")
for field_name, field_type in crud.schema_analyzer.field_types.items():
    print(f"  {field_name}: {field_type}")

print()
print("Field optionality check:")
for field_name in crud.schema_analyzer.field_types.keys():
    is_optional = crud.schema_analyzer._is_optional_field(field_name)
    print(f"  {field_name}: optional={is_optional}")

# 檢查 create model
create_model = crud.schema_analyzer.get_create_model()
print()
print(f"Create model: {create_model}")
print("Create model fields:")
for field_name, field in create_model.model_fields.items():
    print(f"  {field_name}: required={field.is_required()}, default={field.default}")

# 測試創建實例
print()
print("Testing create model:")
try:
    instance = create_model(name="Test", price=99.99)
    print(f"Success: {instance}")
except Exception as e:
    print(f"Failed: {e}")

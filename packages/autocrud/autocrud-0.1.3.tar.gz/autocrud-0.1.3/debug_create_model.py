#!/usr/bin/env python3

import dataclasses
from pydantic import create_model
from tests.test_models import Product

# 檢查 Product dataclass 字段
print("Product dataclass fields:")
for field in dataclasses.fields(Product):
    print(f"  {field.name}: type={field.type}, default={field.default}")
    has_default = field.default is not dataclasses.MISSING
    print(f"    has_default: {has_default}")

print()

# 手動創建一個類似的 Pydantic model
field_definitions = {}

for field in dataclasses.fields(Product):
    field_name = field.name
    field_type = field.type

    # 跳過 ID 字段
    if field_name == "id":
        continue

    # 檢查是否有默認值
    has_default = field.default is not dataclasses.MISSING

    if has_default:
        print(f"Field {field_name} has default: {field.default}")
        # 使用 (type, default_value) 語法
        field_definitions[field_name] = (field_type, field.default)
    else:
        print(f"Field {field_name} is required")
        field_definitions[field_name] = (field_type, ...)

print()
print("Field definitions for create_model:")
for name, definition in field_definitions.items():
    print(f"  {name}: {definition}")

# 創建 Pydantic model
CreateModel = create_model("ProductCreateRequest", **field_definitions)

print()
print("Created model fields:")
for field_name, field in CreateModel.model_fields.items():
    print(f"  {field_name}: required={field.is_required()}, default={field.default}")

# 測試創建實例
print()
print("Testing model creation:")
try:
    # 只提供必需字段
    instance = CreateModel(name="Test", price=99.99)
    print(f"Success: {instance}")
except Exception as e:
    print(f"Failed: {e}")

try:
    # 提供所有字段
    instance = CreateModel(name="Test", price=99.99, description="desc", category="cat")
    print(f"Success with all fields: {instance}")
except Exception as e:
    print(f"Failed with all fields: {e}")

Checklist
- Explain `Field(...)`
- Explain `Field(None)`
- Explain `Field(default_factory=...)`

Here’s the difference:

## 1) `Field(...)` = required
```python
name: str = Field(..., description="unique name for the model")
```

Means:
- must be provided
- no default
- validation fails if missing

Example:
```python
ModelConfig(name="gpt-4")  # OK
ModelConfig()              # error
```

---

## 2) `Field(None)` = optional, default is `None`
```python
name: str | None = Field(None, description="unique name for the model")
```

Means:
- field may be omitted
- if omitted, value becomes `None`

Example:
```python
ModelConfig()              # OK, name=None
ModelConfig(name="gpt-4")  # OK
```

If you keep type as plain `str`, then `None` is not a valid value.

---

## 3) `Field(default_factory=...)` = create default dynamically
Used when the default should be generated each time.

Example:
```python
from pydantic import BaseModel, Field
from datetime import datetime

class ModelConfig(BaseModel):
    created_at: datetime = Field(default_factory=datetime.now)
```

Each instance gets a fresh value.

Common uses:
- lists
- dicts
- timestamps
- nested objects

Example:
```python
class X(BaseModel):
    tags: list[str] = Field(default_factory=list)
```

This avoids sharing the same list between instances.

---

## Quick summary

| Syntax | Meaning |
|---|---|
| `Field(...)` | required |
| `Field(None)` | optional, default `None` |
| `Field(default_factory=...)` | generate default dynamically |


ConfigDict is class-level configuration (like Pydantic v1's class Config:) — e.g., extra="allow" controls unknown-field behavior.
You can instantiate the model via kwargs or via a dict; ConfigDict just affects validation/serialization rules.
Extras are stored on the instance (accessible via __pydantic_extra__) and appear in model_dump() if extra="allow".

lambda is used with default_factory because default_factory expects a callable (a function) that it can call to generate the default value.
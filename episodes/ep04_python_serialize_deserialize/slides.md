---
marp: true
theme: default
paginate: true
backgroundColor: #ffffff
---

# Serialize & Deserialize in Python
## Episode 4 — Protobuf for Embedded & Mobile Developers
**The Debugger Diary**

---

# What We'll Build Today

- Define an `Employee` message in `.proto`
- Generate Python code from it
- **Serialize** a list of employees → binary file
- **Deserialize** the file → back to Python objects

> Goal: understand the full round-trip in code

---

# Setup

```bash
# Install the protobuf Python library
pip install protobuf

# Verify protoc is installed
protoc --version
```

Project structure:
```
ep04_python/
├── employee.proto
├── employee_pb2.py       ← generated
├── serialize_demo.py
└── deserialize_demo.py
```

---

# employee.proto

```protobuf
syntax = "proto3";
package company;

enum Department {
  DEPARTMENT_UNKNOWN = 0;
  ENGINEERING = 1;
  MARKETING = 2;
  HR = 3;
}

message Employee {
  string employee_id = 1;
  string name        = 2;
  int32  age         = 3;
  Department department = 4;
  double salary      = 5;
  bool   is_active   = 6;
  repeated string skills = 8;
}

message EmployeeList {
  repeated Employee employees  = 1;
  int32            total_count = 2;
}
```

---

# Generate Python Code

```bash
protoc --python_out=. employee.proto
```

This creates **`employee_pb2.py`** — never edit it manually.

```python
# What gets created inside employee_pb2.py:
# - Descriptor objects (schema metadata)
# - Employee class
# - EmployeeList class
# - Department enum constants
```

Import in your script:
```python
from employee_pb2 import Employee, EmployeeList, Department
```

---

# Create a Message Object

```python
from employee_pb2 import Employee, Department

emp = Employee()
```

Or use keyword arguments:
```python
emp = Employee(
    employee_id = "EMP001",
    name        = "Alice Johnson",
    age         = 28,
    department  = Department.ENGINEERING,
    salary      = 95000.0,
    is_active   = True,
)
```

---

# Populate All Fields

```python
emp = Employee()

# Scalar fields — assign directly
emp.employee_id = "EMP001"
emp.name        = "Alice Johnson"
emp.age         = 28
emp.salary      = 95000.0
emp.is_active   = True

# Enum field
emp.department  = Department.ENGINEERING

# Repeated field (list) — use .extend() or .append()
emp.skills.extend(["Python", "Go", "Kubernetes"])
emp.skills.append("Docker")
```

---

# SerializeToString()

```python
# Serialize to raw bytes
data = emp.SerializeToString()

print(type(data))      # <class 'bytes'>
print(len(data))       # e.g. 62 bytes

# Compare to JSON
import json
json_str = '{"employeeId":"EMP001","name":"Alice Johnson",...}'
print(len(json_str))   # ~180 bytes
```

Protobuf: **~62 bytes** vs JSON: **~180 bytes** — 3× smaller

---

# Writing to a Binary File

```python
# Serialize all employees into a wrapper message
emp_list = EmployeeList()
emp_list.employees.extend([emp1, emp2, emp3])
emp_list.total_count = 3

# Write to file — MUST use "wb" (binary write mode)
with open("employees.bin", "wb") as f:
    f.write(emp_list.SerializeToString())

print("Saved to employees.bin")
```

> Never use `"w"` (text mode) — binary data will be corrupted

---

# Reading from a Binary File

```python
from employee_pb2 import EmployeeList

# Read raw bytes — MUST use "rb" (binary read mode)
with open("employees.bin", "rb") as f:
    raw_bytes = f.read()

# Parse bytes back into the message object
emp_list = EmployeeList()
emp_list.ParseFromString(raw_bytes)
```

---

# ParseFromString() — Back to Objects

```python
# Now emp_list.employees is a list of Employee objects
for emp in emp_list.employees:
    print(emp.name)
    print(emp.salary)
    print(list(emp.skills))
```

Output:
```
Alice Johnson
95000.0
['Python', 'Go', 'Kubernetes', 'Docker']
```

---

# Multiple Records with EmployeeList

```python
emp_list = EmployeeList()

# Add multiple employees
emp_list.employees.add(
    employee_id="EMP001", name="Alice", age=28,
    department=Department.ENGINEERING, salary=95000.0
)
emp_list.employees.add(
    employee_id="EMP002", name="Bob", age=35,
    department=Department.MARKETING, salary=72000.0
)

emp_list.total_count = len(emp_list.employees)
```

---

# JSON Output — MessageToJson()

```python
from google.protobuf.json_format import MessageToJson, Parse

# Convert protobuf → JSON string
json_str = MessageToJson(emp)
print(json_str)
# {
#   "employeeId": "EMP001",
#   "name": "Alice Johnson",
#   "department": "ENGINEERING",
#   "salary": 95000.0
# }

# Convert JSON string → protobuf
emp2 = Parse(json_str, Employee())
```

---

# Hex Dump — What's in the Binary?

```
Field 1 (employee_id): 0a 07 45 4d 50 30 30 31
  └─ tag=0x0a (field 1, wire type 2=length-delimited)
  └─ len=0x07 (7 bytes)
  └─ "EMP001" in UTF-8

Field 2 (name): 12 0d 41 6c 69 63 65 20 4a 6f 68 6e 73 6f 6e
  └─ tag=0x12 (field 2, wire type 2)
  └─ len=0x0d (13 bytes)
  └─ "Alice Johnson" in UTF-8

Field 3 (age=28): 18 1c
  └─ tag=0x18 (field 3, wire type 0=varint)
  └─ value=0x1c (28 decimal)
```

---

# The Full Round-Trip

```
employee.proto
      │
      ▼  protoc --python_out=.
employee_pb2.py
      │
      ▼  emp = Employee(...)
Python object
      │
      ▼  SerializeToString()
bytes (binary)
      │
      ▼  open("employees.bin", "wb")
Binary file
      │
      ▼  open("employees.bin", "rb") + ParseFromString()
Python object  ✓
```

---

# What's Next

## Episode 5 — C/C++ with nanopb
- Same concept, but on a **microcontroller**
- nanopb: protobuf for tiny devices (< 5 KB footprint)
- Serialize to a fixed-size buffer (no heap allocation)
- Target: ESP32, STM32, Arduino

> If Python is the tooling side, C is the device side

---
marp: true
theme: default
paginate: true
backgroundColor: #ffffff
---

# Your First .proto File & Message Types
## Episode 3 — Protobuf for Embedded & Mobile Developers
**The Debugger Diary**

---

## Installing protoc

**Windows:**
```bash
# Download from github.com/protocolbuffers/protobuf/releases
# Extract and add bin/ folder to PATH
protoc --version
```

**macOS:**
```bash
brew install protobuf
protoc --version
```

**Linux (Ubuntu/Debian):**
```bash
apt install protobuf-compiler
protoc --version
```

Expected output: `libprotoc 27.x`

---

## Anatomy of a .proto File

```protobuf
syntax = "proto3";          // ← must be first non-comment line

package school;             // ← namespacing (prevents name collisions)

import "google/protobuf/timestamp.proto";  // ← import other protos

option java_package = "com.example.school"; // ← language-specific options

// ↓ messages are the core building block
message Student {
  string name = 1;
}
```

---

## Your First Message

```protobuf
syntax = "proto3";

package school;

message Student {
  string  name        = 1;
  int32   age         = 2;
  string  student_id  = 3;
}
```

- Each field: **type  name  =  field_number;**
- Field numbers are permanent — never change them
- Types are strongly enforced

---

## Scalar Types — Integers

| Type | Size | Use When |
|------|------|----------|
| `int32` | variable (varint) | positive integers, general use |
| `int64` | variable (varint) | large positive integers |
| `uint32` | variable (varint) | unsigned 32-bit |
| `uint64` | variable (varint) | unsigned 64-bit |
| `sint32` | variable (zigzag) | **negative numbers** |
| `sint64` | variable (zigzag) | **large negative numbers** |
| `fixed32` | 4 bytes always | values often > 2²⁸ |
| `fixed64` | 8 bytes always | values often > 2⁵⁶ |

---

## Scalar Types — Others

| Type | Default | Notes |
|------|---------|-------|
| `float` | 0.0 | 32-bit IEEE 754 |
| `double` | 0.0 | 64-bit IEEE 754 |
| `bool` | false | true or false |
| `string` | `""` | UTF-8 encoded text |
| `bytes` | `""` | arbitrary binary data |

---

## Varint Encoding — Why sint32 Matters

```
int32  value = -1  →  10 bytes on wire  ❌
sint32 value = -1  →   1 byte on wire   ✅
```

**Why?** `int32` encodes negative numbers as large 64-bit values.
`sint32` uses **zigzag encoding**: maps negatives to small positive integers.

```
zigzag(0)  = 0    →  1 byte
zigzag(-1) = 1    →  1 byte
zigzag(1)  = 2    →  1 byte
zigzag(-2) = 3    →  1 byte
```

**Rule:** Use `sint32` / `sint64` when a field can be **negative**.

---

## Field Numbers

```protobuf
message Student {
  string name       = 1;   // ← field number 1
  int32  age        = 2;   // ← field number 2
  string student_id = 3;   // ← field number 3
}
```

- Must be **unique** within a message
- Range: **1 to 536,870,911** (19000–19999 reserved)
- Fields **1–15**: encoded in **1 byte** → use for frequent fields
- Fields **16–2047**: encoded in **2 bytes**
- **Never reuse or change a field number** once data exists

---

## Nested Messages

```protobuf
message Address {
  string street   = 1;
  string city     = 2;
  string state    = 3;
  string zip_code = 4;
}

message Student {
  string  name      = 1;
  int32   age       = 2;
  Address address   = 3;   // ← nested message
}
```

Nested messages serialize inline — no extra overhead.

---

## Enums

```protobuf
enum Department {
  DEPARTMENT_UNKNOWN     = 0;   // ← first value MUST be 0
  COMPUTER_SCIENCE       = 1;
  ELECTRICAL_ENGINEERING = 2;
  MECHANICAL_ENGINEERING = 3;
  MATHEMATICS            = 4;
}

message Student {
  string     name       = 1;
  Department department = 2;
}
```

> Always name the zero value `_UNKNOWN` or `_UNSPECIFIED` — it's the default.

---

## repeated Fields (Lists)

```protobuf
message Student {
  string          name    = 1;
  repeated string courses = 2;   // ← list of strings
}
```

**Usage in Python:**
```python
student = Student()
student.name = "Alice"
student.courses.append("Data Structures")
student.courses.append("Algorithms")
student.courses.extend(["OS", "Networks"])

print(student.courses[0])  # "Data Structures"
print(len(student.courses))  # 4
```

---

## oneof — Mutually Exclusive Fields

```protobuf
message Student {
  string name = 1;

  oneof financial_aid {
    float scholarship_amount = 2;
    float stipend_amount     = 3;
  }
  // Only ONE of scholarship_amount or stipend_amount can be set
}
```

**Use case:** When a field can be one of several types — like a payment method (card OR bank transfer, not both).

---

## map Fields

```protobuf
message Student {
  string name = 1;

  map<string, int32> grades = 2;
  // course name → grade (0–100)
}
```

**Usage in Python:**
```python
student.grades["Data Structures"] = 92
student.grades["Algorithms"] = 87

print(student.grades["Data Structures"])  # 92
```

> `map` fields cannot be `repeated`.

---

## Well-Known Types

```protobuf
import "google/protobuf/timestamp.proto";
import "google/protobuf/duration.proto";
import "google/protobuf/any.proto";

message Student {
  string name = 1;
  google.protobuf.Timestamp enrollment_date = 2;
  google.protobuf.Duration  study_duration  = 3;
}
```

| Type | Use For |
|------|---------|
| `Timestamp` | Date/time (seconds + nanos since Unix epoch) |
| `Duration` | Time intervals |
| `Any` | Embed any message type dynamically |
| `Struct` | Dynamic JSON-like key-value data |

---

## Complete student.proto

```protobuf
syntax = "proto3";
package school;
import "google/protobuf/timestamp.proto";

enum Department {
  DEPARTMENT_UNKNOWN = 0;
  COMPUTER_SCIENCE = 1;
  ELECTRICAL_ENGINEERING = 2;
}

message Address {
  string street = 1; string city = 2;
  string state = 3;  string zip_code = 4;
}

message Student {
  string student_id = 1;   string name = 2;
  int32 age = 3;            Department department = 4;
  repeated string courses = 5;   double gpa = 6;
  Address address = 7;     map<string, int32> grades = 8;
  google.protobuf.Timestamp enrollment_date = 9;
  oneof financial_aid {
    float scholarship_amount = 10;
    float stipend_amount = 11;
  }
}
```

---

## Generating Code

**Python:**
```bash
protoc --python_out=. student.proto
# generates: student_pb2.py
```

**C (nanopb for embedded):**
```bash
protoc --nanopb_out=. student.proto
# generates: student.pb.c  student.pb.h
```

**Go:**
```bash
protoc --go_out=. student.proto
# generates: student.pb.go
```

---

## Summary — Message Types

| Type | Keyword | Example |
|------|---------|---------|
| Basic fields | scalar types | `string name = 1;` |
| Nested message | message name | `Address address = 3;` |
| List/array | `repeated` | `repeated string courses = 5;` |
| Enumeration | `enum` | `Department dept = 4;` |
| Exclusive choice | `oneof` | `oneof aid { ... }` |
| Dictionary | `map<K,V>` | `map<string, int32> grades = 8;` |
| Date/time | `Timestamp` | `Timestamp enrolled = 9;` |

---

## What's Next

### Episode 4: Serialize & Deserialize in Python

- Generate Python code from student.proto
- Create Employee records in Python
- Serialize to bytes → write to binary file
- Read file → deserialize back to objects
- Inspect the binary format (hex dump)
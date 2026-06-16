# Episode 3: Your First .proto File & Message Types

**Series:** Protobuf for Embedded & Mobile Developers  
**Channel:** The Debugger Diary  
**Prerequisites:** Episodes 1 & 2

---

## Episode Overview

This episode is the hands-on foundation of the series. You'll install the protoc compiler, write your first `.proto` file from scratch, and learn every message type proto3 supports. By the end, you'll have a complete `student.proto` that demonstrates all features, and you'll know how to compile it to generate code in Python and C.

---

## Section 1: Installing protoc

The protoc compiler reads `.proto` files and generates source code in your target language.

### Windows

1. Go to: `github.com/protocolbuffers/protobuf/releases`
2. Download `protoc-XX.X-win64.zip`
3. Extract the zip
4. Add the `bin/` folder to your system PATH
5. Open a new terminal and verify:

```bash
protoc --version
# libprotoc 27.x
```

### macOS

```bash
brew install protobuf
protoc --version
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install protobuf-compiler
protoc --version
```

For the latest version on Linux, download the binary directly from the GitHub releases page instead of using apt (apt may have an older version).

---

## Section 2: .proto File Anatomy

Every `.proto` file follows this structure:

```protobuf
syntax = "proto3";                           // (1) syntax declaration
package school;                              // (2) package name
import "google/protobuf/timestamp.proto";    // (3) imports
option java_package = "com.example.school"; // (4) options
option java_outer_classname = "StudentProto";

message Student {                            // (5) message definitions
  string name = 1;
}
```

**1. Syntax declaration**  
Must be the first non-comment, non-blank line. Declares proto3 format. Without this, protoc defaults to proto2.

**2. Package**  
Namespaces your messages. Prevents naming collisions when multiple `.proto` files are imported. In Python, this doesn't create a module; in Go, it maps to Go packages. Convention: use lowercase, dot-separated (e.g., `school`, `com.example.analytics`).

**3. Imports**  
Import other `.proto` files to use their message types. Google ships a set of well-known types under `google/protobuf/`.

**4. Options**  
File-level hints to the code generator. Language-specific:
- `java_package` — Java package name
- `java_outer_classname` — wrapping Java class name
- `go_package` — Go import path
- `objc_class_prefix` — Objective-C class prefix

**5. Messages**  
The core unit. Each message maps to a class/struct in generated code.

---

## Section 3: Scalar Types — Complete Reference

Scalar types are the primitive building blocks. Every field is either a scalar type, a message type, an enum, or a map.

| Proto3 Type | C++ Type | Python Type | Default Value | Notes |
|-------------|----------|-------------|---------------|-------|
| `double` | double | float | 0.0 | 64-bit IEEE 754 |
| `float` | float | float | 0.0 | 32-bit IEEE 754 |
| `int32` | int32_t | int | 0 | Variable-length; inefficient for negatives |
| `int64` | int64_t | int | 0 | Variable-length; inefficient for negatives |
| `uint32` | uint32_t | int | 0 | Unsigned 32-bit varint |
| `uint64` | uint64_t | int | 0 | Unsigned 64-bit varint |
| `sint32` | int32_t | int | 0 | **Zigzag encoding; use for negative values** |
| `sint64` | int64_t | int | 0 | **Zigzag encoding; use for negative values** |
| `fixed32` | uint32_t | int | 0 | Always 4 bytes; efficient if values often > 2²⁸ |
| `fixed64` | uint64_t | int | 0 | Always 8 bytes; efficient if values often > 2⁵⁶ |
| `sfixed32` | int32_t | int | 0 | Signed fixed 4 bytes |
| `sfixed64` | int64_t | int | 0 | Signed fixed 8 bytes |
| `bool` | bool | bool | false | |
| `string` | string | str | `""` | Must be UTF-8 encoded |
| `bytes` | string | bytes | `b""` | Arbitrary binary data |

### Choosing the right integer type

```
Need to store age (always positive 0–150)?    → int32
Need to store temperature (can be -40 to 80)? → sint32
Need a Unix timestamp (always positive)?       → int64 or fixed64
Storing a hash or UUID (fixed size)?           → fixed32 / fixed64
```

---

## Section 4: Varint Encoding Deep Dive

Understanding varint encoding helps you choose the right integer type for embedded use cases where every byte matters.

### How varints work

Instead of always using 4 or 8 bytes for integers, protobuf uses **variable-length encoding**: small numbers use fewer bytes.

```
value 1    → 1 byte
value 127  → 1 byte
value 128  → 2 bytes
value 300  → 2 bytes
value 16383 → 2 bytes
value 16384 → 3 bytes
```

This is great for small positive numbers. A field like `age = 25` is just 1 byte.

### The problem with negative int32

`int32` is stored internally as a 64-bit two's complement number. A value of `-1` in two's complement is `0xFFFFFFFFFFFFFFFF` — that's 10 bytes as a varint.

```
int32  field = -1;  →  10 bytes on wire
sint32 field = -1;  →   1 byte  on wire
```

### Zigzag encoding (sint32 / sint64)

`sint32` and `sint64` use zigzag encoding: they map negative numbers to small positive integers before varint-encoding.

```
zigzag(0)   = 0     →  1 byte
zigzag(-1)  = 1     →  1 byte
zigzag(1)   = 2     →  1 byte
zigzag(-2)  = 3     →  1 byte
zigzag(2)   = 4     →  1 byte
zigzag(-64) = 127   →  1 byte
```

**Rule:** Use `sint32` / `sint64` whenever a field can hold negative values.

### fixed32 / fixed64

These always occupy 4 or 8 bytes regardless of value. Use them when:
- Values are frequently large (close to the 32-bit max)
- You need predictable message sizes (important for some embedded protocols)

---

## Section 5: Field Numbers

Field numbers are the most important concept for long-lived protobuf schemas.

```protobuf
message Student {
  string name       = 1;   // field number 1
  int32  age        = 2;   // field number 2
  string student_id = 3;   // field number 3
}
```

### Why field numbers matter

Protobuf does **not** encode field names on the wire. It encodes field numbers. When deserializing, the decoder uses the field number to look up the field in the schema.

This means:
- You can **rename a field** without breaking compatibility (the number stays the same)
- You **cannot change a field number** without breaking old data
- You **cannot reuse a field number** for a different field

### Field number ranges

| Range | Tag size | Notes |
|-------|----------|-------|
| 1–15 | 1 byte | Use for the most frequently populated fields |
| 16–2047 | 2 bytes | |
| 2048–536,870,911 | 3+ bytes | |
| 19000–19999 | — | Reserved by protobuf — do not use |

**Best practice:** Assign low field numbers (1–15) to fields that will always be present, since they cost 1 byte for the tag. Reserve higher numbers for rare or optional fields.

---

## Section 6: Nested Messages

Messages can contain other messages as fields. This is the primary way to model complex, hierarchical data.

```protobuf
message Address {
  string street   = 1;
  string city     = 2;
  string state    = 3;
  string zip_code = 4;
}

message Student {
  string  student_id = 1;
  string  name       = 2;
  int32   age        = 3;
  Address address    = 4;   // nested message
}
```

**Usage in Python:**
```python
from school_pb2 import Student, Address

student = Student()
student.student_id = "STU001"
student.name = "Alice"
student.age = 20

student.address.street  = "123 Main St"
student.address.city    = "Springfield"
student.address.state   = "IL"
student.address.zip_code = "62701"
```

Nested messages are serialized inline — there is no extra pointer indirection cost in the binary format.

---

## Section 7: Enums

Enums let you define a set of named integer constants.

```protobuf
enum Department {
  DEPARTMENT_UNKNOWN     = 0;   // MUST be 0
  COMPUTER_SCIENCE       = 1;
  ELECTRICAL_ENGINEERING = 2;
  MECHANICAL_ENGINEERING = 3;
  MATHEMATICS            = 4;
}

message Student {
  string     student_id = 1;
  string     name       = 2;
  Department department = 3;
}
```

### Rules for enums in proto3

1. **The first value must be 0.** This is the default value for any unset enum field. Convention: name it `_UNKNOWN` or `_UNSPECIFIED`.
2. Enum values must be unique within the enum (unless you use `allow_alias = true`).
3. Enum names are scoped to the message they're defined in (or global if defined at the top level).

**Why the zero value matters:** If you receive a message with an enum field set to a value you don't recognize (from a newer schema), it will be preserved during deserialization and re-serialization. But if the field is missing entirely, it defaults to `0` — that's why `0` should mean "unknown/unset," not a real value.

---

## Section 8: repeated Fields

`repeated` declares a list (zero or more values). It works with scalars, messages, and enums.

```protobuf
message Student {
  string          student_id = 1;
  string          name       = 2;
  repeated string courses    = 3;
  repeated float  test_scores = 4;
}
```

**Usage in Python:**
```python
student = Student()
student.name = "Alice"

# Append one at a time
student.courses.append("Data Structures")
student.courses.append("Algorithms")

# Add multiple at once
student.courses.extend(["Operating Systems", "Networks"])

# Access like a list
print(student.courses[0])       # "Data Structures"
print(len(student.courses))     # 4

# Iterate
for course in student.courses:
    print(course)
```

**In C (nanopb):**  
Because nanopb uses static allocation, repeated fields require you to specify a maximum count in a `.options` file:
```
Student.courses max_count:10
```

---

## Section 9: oneof

`oneof` declares that only one of the listed fields can be set at a time. Setting one field automatically clears the others.

```protobuf
message Student {
  string student_id = 1;
  string name       = 2;

  oneof financial_aid {
    float scholarship_amount = 3;
    float stipend_amount     = 4;
  }
}
```

**Usage in Python:**
```python
student = Student()
student.name = "Bob"

student.scholarship_amount = 5000.0
print(student.WhichOneof("financial_aid"))   # "scholarship_amount"

# Setting stipend clears scholarship
student.stipend_amount = 800.0
print(student.WhichOneof("financial_aid"))   # "stipend_amount"
print(student.scholarship_amount)            # 0.0 (cleared)
```

**Common use cases:**
- Payment method: card OR bank transfer
- ID type: email OR phone number OR username
- Result type: success payload OR error details

---

## Section 10: map Fields

`map<KeyType, ValueType>` declares a dictionary/hash map.

```protobuf
message Student {
  string student_id            = 1;
  string name                  = 2;
  map<string, int32> grades    = 3;  // course → grade (0–100)
  map<string, string> metadata = 4;  // arbitrary key-value tags
}
```

**Constraints:**
- Key types: any scalar type **except** float, double, and bytes
- Value types: any type (scalar, message, enum)
- `map` fields **cannot** be `repeated`
- Order is not guaranteed

**Usage in Python:**
```python
student = Student()
student.name = "Alice"
student.grades["Data Structures"] = 92
student.grades["Algorithms"] = 87
student.grades["Operating Systems"] = 95

print(student.grades["Algorithms"])  # 87

for course, grade in student.grades.items():
    print(f"{course}: {grade}")
```

---

## Section 11: Well-Known Types

Google ships a set of standard message types with the protobuf library. Import them with `import "google/protobuf/<name>.proto"`.

### Timestamp

```protobuf
import "google/protobuf/timestamp.proto";

message Student {
  string name = 1;
  google.protobuf.Timestamp enrollment_date = 2;
}
```

Represents a point in time: `int64 seconds` (since Unix epoch) + `int32 nanos`.

```python
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime, timezone

student = Student()
ts = Timestamp()
ts.FromDatetime(datetime(2024, 9, 1, tzinfo=timezone.utc))
student.enrollment_date.CopyFrom(ts)
```

### Duration

```protobuf
import "google/protobuf/duration.proto";

message Session {
  google.protobuf.Duration length = 1;
}
```

Represents a signed duration: `int64 seconds` + `int32 nanos`.

### Any

```protobuf
import "google/protobuf/any.proto";

message Notification {
  string  title   = 1;
  google.protobuf.Any payload = 2;  // can hold any message
}
```

Lets you embed any message type without knowing the type at schema definition time. The receiver uses the type URL to decode it.

### Struct

```protobuf
import "google/protobuf/struct.proto";

message Config {
  google.protobuf.Struct properties = 1;  // dynamic JSON-like data
}
```

Represents a JSON object. Useful when you need flexible key-value data without a fixed schema.

---

## Section 12: Complete student.proto

This file combines every concept from this episode:

```protobuf
syntax = "proto3";

package school;

import "google/protobuf/timestamp.proto";

option java_package = "com.example.school";
option java_outer_classname = "StudentProto";

// Enum for academic department
enum Department {
  DEPARTMENT_UNKNOWN     = 0;
  COMPUTER_SCIENCE       = 1;
  ELECTRICAL_ENGINEERING = 2;
  MECHANICAL_ENGINEERING = 3;
  MATHEMATICS            = 4;
}

// Nested message for physical address
message Address {
  string street   = 1;
  string city     = 2;
  string state    = 3;
  string zip_code = 4;
}

// Main student message — demonstrates all message types
message Student {
  string     student_id = 1;             // scalar string
  string     name       = 2;             // scalar string
  int32      age        = 3;             // scalar int
  Department department = 4;             // enum
  repeated string courses = 5;           // repeated (list)
  double     gpa       = 6;             // scalar double
  Address    address   = 7;             // nested message
  map<string, int32> grades = 8;        // map (dict)
  google.protobuf.Timestamp enrollment_date = 9;  // well-known type

  oneof financial_aid {                 // oneof (exclusive choice)
    float scholarship_amount = 10;
    float stipend_amount     = 11;
  }
}

// A collection of students with a count
message StudentList {
  repeated Student students    = 1;
  int32           total_count  = 2;
}
```

---

## Section 13: Generating Code

Once you have a `.proto` file, run `protoc` to generate source code.

### Python

```bash
protoc --python_out=. student.proto
# Output: student_pb2.py
```

Install the runtime:
```bash
pip install protobuf
```

### C with nanopb (for embedded)

```bash
# Install nanopb first (see Episode 5)
python nanopb_generator.py student.proto
# Output: student.pb.c, student.pb.h
```

### Go

```bash
protoc --go_out=. student.proto
# Output: student.pb.go
```

### Java / Kotlin

```bash
protoc --java_out=. student.proto
# Output: StudentProto.java (or per message)
```

---

## Key Takeaways

- A `.proto` file has: syntax declaration, package, imports, options, and messages
- Field numbers are permanent — they're what's actually on the wire, not names
- Use `sint32`/`sint64` for fields that can be negative (zigzag encoding saves space)
- Fields 1–15 use 1-byte tags — assign them to your most common fields
- `repeated` = list, `map` = dictionary, `oneof` = exclusive choice
- Always start enums with a `_UNKNOWN = 0` value
- Well-known types (Timestamp, Duration, Any) are pre-built standard messages

---

## Common Mistakes

1. **Reusing a field number** after it's been in production — breaks deserialization of old data
2. **Using `sint32` for always-positive values** — no benefit, use `int32` instead
3. **Forgetting `UNKNOWN = 0` in enums** — proto3 requires the first enum value to be `0`
4. **Using `int32` for values that can be negative** (like temperatures) — wastes 10 bytes per field
5. **Putting high-frequency fields at numbers > 15** — costs 1 extra byte per field per message

---

## Further Reading

- Proto3 Language Guide (protobuf.dev)
- Encoding documentation — explains varint, zigzag, wire types in depth (protobuf.dev/programming-guides/encoding)
- Well-known types reference (protobuf.dev/reference/protobuf/google.protobuf)
- Protoc installation guide for all platforms (grpc.io/docs/protoc-installation)
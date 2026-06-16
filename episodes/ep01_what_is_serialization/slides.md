---
marp: true
theme: default
paginate: true
backgroundColor: #ffffff
---

# What is Serialization?

### Episode 1 — Protobuf for Embedded & Mobile
**The Debugger Diary**

---

## The Problem

You have a Student object in memory:

```
name:       "Alice"
age:        20
student_id: "STU001"
department: "Computer Science"
courses:    ["Data Structures", "Algorithms", "OS"]
gpa:        3.8
```

How do you **save it to a file**?
How do you **send it over a network or UART**?

---

## Serialization = Packing a Suitcase

```
Your Object                    Byte Stream
┌─────────────┐               ┌──────────────────┐
│ name: Alice │               │ 0A 05 41 6C 69 63│
│ age:  20    │  ──────────►  │ 65 10 14 1A 06 53│
│ gpa:  3.8   │               │ 54 55 30 30 31...│
└─────────────┘               └──────────────────┘
   In-Memory                      On disk / wire
```

**Serialization** = converting an in-memory object → byte stream

**Deserialization** = byte stream → back to in-memory object

---

## Why Do We Need It?

| Scenario | Need |
|----------|------|
| Save to disk / flash | Data must outlive the process |
| Send over UART / BLE / HTTP | Wire accepts only bytes |
| Inter-process communication | Processes don't share memory |
| Embedded: store config in EEPROM | Flash stores raw bytes only |

---

## Option 1: JSON

```json
{
  "name": "Alice",
  "age": 20,
  "student_id": "STU001",
  "department": "Computer Science",
  "courses": ["Data Structures", "Algorithms", "OS"],
  "gpa": 3.8
}
```

**Size: ~175 bytes**
Human readable ✅  |  Easy to debug ✅  |  Large size ❌  |  Slow to parse ❌

---

## Option 2: XML

```xml
<student>
  <name>Alice</name>
  <age>20</age>
  <student_id>STU001</student_id>
  <department>Computer Science</department>
  <courses>
    <course>Data Structures</course>
    <course>Algorithms</course>
    <course>OS</course>
  </courses>
  <gpa>3.8</gpa>
</student>
```

**Size: ~280 bytes**
Very verbose ❌  |  Hard to parse on MCU ❌

---

## The Size Problem

```
Same Student data:

JSON  ████████████████████  ~175 bytes
XML   ████████████████████████████  ~280 bytes
Protobuf  ████  ~35 bytes
```

For embedded devices with **limited flash, RAM, and bandwidth** — size matters.

---

## Binary Formats Overview

| Format | By | Schema? | Size |
|--------|----|---------|------|
| MessagePack | Community | No | Small |
| CBOR | IETF | No | Small |
| Apache Avro | Apache | Yes | Very Small |
| Apache Thrift | Facebook | Yes | Small |
| **Protocol Buffers** | **Google** | **Yes** | **Very Small** |

---

## Full Comparison

| Format | Type | Schema | Human Readable | Typical Size | Parse Speed |
|--------|------|--------|----------------|-------------|-------------|
| JSON | Text | No | ✅ | ~175 B | Medium |
| XML | Text | Optional | ✅ | ~280 B | Slow |
| CSV | Text | No | ✅ | Varies | Fast |
| MessagePack | Binary | No | ❌ | ~90 B | Fast |
| CBOR | Binary | No | ❌ | ~85 B | Fast |
| Avro | Binary | Yes | ❌ | ~40 B | Very Fast |
| **Protobuf** | **Binary** | **Yes** | **❌** | **~35 B** | **Very Fast** |

---

## Why Protobuf Wins for Embedded & Mobile

- **3–10x smaller** than JSON for the same data
- **No text parsing** — decoded directly from bytes
- **Typed schema** — bugs caught at compile time, not runtime
- **Code generated** for C, Python, Java, Kotlin, Swift, Go, Rust...
- **nanopb** runs on MCUs with < 5 KB flash footprint
- **Language-agnostic** — MCU writes, mobile app reads

---

## When NOT to Use Protobuf

- **Config files** humans need to read and edit (use TOML/YAML/JSON)
- **Logging / debugging output** (not human readable)
- **Single-value data** (just send the int directly)
- **Quick prototypes** where schema overhead isn't worth it

> Rule of thumb: if a human needs to open and read the file, don't use protobuf.

---

## Key Takeaways

1. Serialization = converting objects ↔ bytes
2. JSON and XML are human-readable but wasteful in size
3. Binary formats are smaller and faster to parse
4. Protobuf combines a strict schema with compact binary encoding
5. Ideal for embedded (flash/RAM constrained) and mobile (bandwidth constrained)

---

## What's Next

### Episode 2 — History & Versions of Protobuf

- Where protobuf came from (Google, 2001)
- proto1 → proto2 → proto3 → Editions
- What changed in each version
- Which version you should use today

---

# Thanks for Watching!

**The Debugger Diary**

Code and notes: github.com/thedebuggerdiary/learn_protobuf

---
marp: true
theme: default
paginate: true
backgroundColor: #ffffff
---

# Schema Evolution & Best Practices
### Episode 6 — Protobuf for Embedded & Mobile Developers
**The Debugger Diary**

---

# The Real-World Problem

You shipped **Firmware v1** six months ago.
10,000 devices are in the field.
Each device has stored employee records as protobuf binary in flash.

Now Product says: _"We need to add a bonus field."_

**Question:** Can you change the `.proto` without breaking those stored records?

> This episode answers that question.

---

# Two Types of Compatibility

```
┌──────────────────────────────────────────────────────┐
│  Backward Compatible                                 │
│  New code can read OLD data                          │
│  (v2 firmware reads v1 stored records) ✓             │
├──────────────────────────────────────────────────────┤
│  Forward Compatible                                  │
│  Old code can read NEW data                          │
│  (v1 firmware reads v2 records from server) ✓        │
└──────────────────────────────────────────────────────┘
```

Proto3 gives you **both** — as long as you follow the rules.

---

# Safe Change #1: Adding a New Field

```protobuf
// v1
message Employee {
  string id     = 1;
  string name   = 2;
  double salary = 3;
}

// v2 — added department (new field number 4)
message Employee {
  string id         = 1;
  string name       = 2;
  double salary     = 3;
  string department = 4;   // ← new field, new number ✓
}
```

Old readers ignore field 4. New readers get empty string `""` for old data.

---

# Safe Change #2: Renaming a Field

```protobuf
// v1
message Employee {
  double salary = 3;
}

// v2 — renamed salary → base_salary (SAME field number)
message Employee {
  double base_salary = 3;   // ← name changed, number unchanged ✓
}
```

**Wire format only uses field numbers, not names.**
Renaming is safe — it only affects generated code identifiers.

---

# Safe Change #3: Adding an Enum Value

```protobuf
// v1
enum Department {
  DEPARTMENT_UNKNOWN = 0;
  ENGINEERING = 1;
  MARKETING   = 2;
}

// v2 — added SALES
enum Department {
  DEPARTMENT_UNKNOWN = 0;
  ENGINEERING = 1;
  MARKETING   = 2;
  SALES       = 3;   // ← safe to add ✓
}
```

Old code reading value `3` gets `DEPARTMENT_UNKNOWN` (0 fallback in proto3).

---

# Unsafe Change #1: Changing a Field Number

```protobuf
// v1 — salary is field 3
message Employee {
  double salary = 3;   // wire tag: field=3, type=64-bit → 0x19
}

// v2 — DANGEROUS: moved salary to field 5
message Employee {
  double salary = 5;   // wire tag: field=5, type=64-bit → 0x29
}
```

Old data has bytes tagged as field 3.
New code looks for field 5 — gets 0.0 instead of actual salary.

**Never change a field number once you have data in production.**

---

# Unsafe Change #2: Changing a Field Type

```protobuf
// v1
message Employee {
  int32 employee_code = 4;   // wire type: varint (0)
}

// v2 — DANGEROUS: changed to string
message Employee {
  string employee_code = 4;  // wire type: length-delimited (2)
}
```

The wire type is encoded in the tag byte.
A varint tag and a length-delimited tag are **different bytes**.
Old data will be misinterpreted or cause a parse error.

---

# Unsafe Change #3: Removing Without Reserving

```protobuf
// v1
message Employee {
  string id     = 1;
  string name   = 2;
  double salary = 3;
  string ssn    = 4;   // removed in v2 (privacy reasons)
}

// v2 — DANGEROUS: field 4 deleted, number 4 now available
message Employee {
  string id     = 1;
  string name   = 2;
  double salary = 3;
  // ssn removed — but nothing stops someone from adding field 4 later!
}
```

---

# The `reserved` Keyword — The Fix

```protobuf
// v2 — SAFE: reserved field number AND name
message Employee {
  string id     = 1;
  string name   = 2;
  double salary = 3;

  reserved 4;          // no one can ever use field number 4 again
  reserved "ssn";      // no one can ever use the name "ssn" again
}
```

`protoc` will give a **compile error** if anyone tries to use field 4 or the name `ssn`.

---

# Real Migration: Employee v1 → v2 → v3

```protobuf
// v1 (original)
message Employee {
  string id     = 1;
  string name   = 2;
  double salary = 3;
}

// v2 (added department + manager)
message Employee {
  string id         = 1;
  string name       = 2;
  double salary     = 3;
  string department = 4;   // new ✓
  string manager_id = 5;   // new ✓
}

// v3 (renamed salary, added bonus, removed manager_id)
message Employee {
  string id              = 1;
  string name            = 2;
  double base_salary     = 3;   // renamed ✓ (same number)
  string department      = 4;
  double bonus_percentage = 6;  // new ✓
  reserved 5; reserved "manager_id";  // removed safely ✓
}
```

---

# Backward Compatibility in Practice

**Scenario:** v2 firmware reads a v1 record from flash.

```
v1 binary: field 1 (id), field 2 (name), field 3 (salary)
                                      ← fields 4, 5 are missing

v2 reader result:
  id         = "EMP001"   ✓  (present in data)
  name       = "Bob"      ✓  (present in data)
  salary     = 75000.0    ✓  (present in data)
  department = ""         ✓  (missing → proto3 zero value = empty string)
  manager_id = ""         ✓  (missing → zero value)
```

New code gracefully handles missing fields — they get zero/empty defaults.

---

# Forward Compatibility in Practice

**Scenario:** v1 firmware reads a v2 record from a server response.

```
v2 binary: field 1, field 2, field 3, field 4, field 5

v1 reader result:
  id     = "EMP001"  ✓  (knows about field 1)
  name   = "Bob"     ✓  (knows about field 2)
  salary = 75000.0   ✓  (knows about field 3)
  
  Fields 4, 5 → UNKNOWN FIELDS → silently skipped ✓
```

Old code ignores fields it doesn't know about. No crash, no error.

---

# Best Practices Checklist

1. **Never reuse a field number** — even after deleting the field
2. **Always `reserved` deleted fields** (number AND name)
3. **Never change a field's type** once data is in production
4. **Never change a field's number** once data is in production
5. **Start enum values at 0** with an `UNKNOWN` sentinel
6. **Use fields 1–15 for the most frequent fields** (1-byte tag)
7. **Add a `schema_version` int32 field** for embedded stored data
8. **Document every field** with what it means and when it was added
9. **Rename freely** — only field numbers matter on the wire
10. **Test both directions**: new code reads old data, old code reads new data

---

# Embedded-Specific Warning

Flash-stored data can outlive your firmware by **years**.

```
Device manufactured: 2024
Firmware v1 stores protobuf records in flash
Firmware v7 released: 2027
Factory reset is not an option

→ v7 must still read v1 records from 2024
```

**Rule:** In embedded projects, treat field numbers as permanent IDs.
Never change or reuse them. Add `schema_version` to every persistent message.

---

# Summary

- Proto3 is backward AND forward compatible — by design
- Safe: add fields (new numbers), rename fields, add enum values
- Unsafe: change field numbers, change field types, delete without `reserved`
- `reserved` is your safety net — use it every time you remove a field
- For embedded: field numbers are forever; stored data outlives firmware

---

# What's Next

## Episode 7 — gRPC: A Quick Intro

> You've mastered protobuf as a data format.
> Now see how it powers gRPC — Google's RPC framework.

- What is RPC and why gRPC?
- service + rpc definitions in .proto
- The 4 call types
- gRPC on Android and iOS

**See you there!**

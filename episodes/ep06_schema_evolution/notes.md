# Episode 6 — Schema Evolution & Best Practices

**Series:** Protobuf for Embedded & Mobile Developers  
**Channel:** The Debugger Diary  
**Prerequisites:** Episodes 1–5

---

## Episode Overview

Schema evolution is the process of changing a `.proto` file after data has already been serialized with an older version of that schema. This is one of the most practically important topics in protobuf — especially for embedded systems where devices in the field may hold binary data for years.

---

## Section 1: Why Schema Evolution Matters

**Three real scenarios where this comes up:**

1. **Deployed firmware** — A device has been storing protobuf records in SPI flash since firmware v1. Firmware v5 is being released. The v5 code must still read the v1 binary records.

2. **API versioning** — A mobile app sends protobuf messages to a server. App v3 users haven't updated yet while the server is running v5. Both must interoperate.

3. **Long-lived files** — You're logging sensor or student data to SD cards. Files written today must be readable by software written two years from now.

Proto3 is designed to handle all three — but only if you follow a set of rules.

---

## Section 2: Compatibility Defined

**Backward compatible:** new code (firmware/app/server) can correctly read data serialized by old code.  
**Forward compatible:** old code can read data serialized by new code (unknown fields are ignored).

Proto3 is both backward and forward compatible **by default**, as long as you never:
- Reuse a field number
- Change a field's type
- Change a field's number

---

## Section 3: Safe Changes

### 3.1 Adding a New Field

Always use a **new, previously unused field number**.

```protobuf
// v1
message Employee {
  string employee_id = 1;
  string name        = 2;
  double salary      = 3;
}

// v2 — department added with field number 4 (never used before)
message Employee {
  string employee_id = 1;
  string name        = 2;
  double salary      = 3;
  string department  = 4;   // new ✓
}
```

**What happens with old data:** Old binary doesn't have field 4. When new code reads it, `department` gets its zero value: `""`. No error.

**What happens with old code:** Old code reads new data that includes field 4. Field 4 is unknown — it's silently skipped. No error.

### 3.2 Renaming a Field

Field names don't exist on the wire — only field numbers do. Renaming is purely a source code change.

```protobuf
// v1
message Employee {
  double salary = 3;
}

// v2 — renamed, same number
message Employee {
  double base_salary = 3;   // renamed ✓ — wire format unchanged
}
```

The generated code identifier changes (`employee.salary` → `employee.base_salary`), but the binary encoding is identical.

### 3.3 Adding a New Enum Value

```protobuf
// v1
enum Department {
  DEPARTMENT_UNKNOWN = 0;
  ENGINEERING = 1;
  MARKETING   = 2;
}

// v2
enum Department {
  DEPARTMENT_UNKNOWN = 0;
  ENGINEERING = 1;
  MARKETING   = 2;
  SALES       = 3;   // new value ✓
}
```

Old code that receives a `SALES` (value 3) from new data will store it as an unknown integer. In proto3, unrecognized enum values are preserved in the message (not silently zeroed as in proto2).

---

## Section 4: Unsafe Changes — Never Do These in Production

### 4.1 Changing a Field Number

```protobuf
// v1 — salary stored as field 3
message Employee {
  double salary = 3;
}

// v2 — BROKEN: salary moved to field 5
message Employee {
  double salary = 5;   // ← DON'T DO THIS
}
```

The wire encoding of field 3 (tag byte `0x19`) is completely different from field 5 (tag byte `0x29`). New code looking for field 5 won't find the old data tagged as field 3. The salary reads as `0.0`.

### 4.2 Changing a Field Type

```protobuf
// v1
message Employee {
  int32 employee_code = 4;   // wire type 0: varint
}

// v2 — BROKEN: changed to string
message Employee {
  string employee_code = 4;  // wire type 2: length-delimited
}
```

The wire type is encoded in the tag byte. `int32` uses wire type 0 (varint). `string` uses wire type 2 (length-delimited). When new code tries to decode old varint bytes as a string, the parse will fail or produce garbage.

**Types that ARE safely interchangeable** (same wire encoding):
- `int32`, `int64`, `uint32`, `uint64`, `bool`, `enum` → all use wire type 0 (varint)
- `fixed32`, `sfixed32`, `float` → all use wire type 5 (32-bit)
- `fixed64`, `sfixed64`, `double` → all use wire type 1 (64-bit)
- `string`, `bytes`, embedded messages → all use wire type 2 (length-delimited)

### 4.3 Removing a Field Without Reserving

```protobuf
// v1
message Employee {
  string employee_id = 1;
  string name        = 2;
  double salary      = 3;
  string tax_id      = 4;   // removed in v2 for compliance
}

// v2 — DANGEROUS: field 4 silently gone
message Employee {
  string employee_id = 1;
  string name        = 2;
  double salary      = 3;
  // tax_id removed — but field number 4 is now "free"
}
```

Six months later, a new developer adds a field and reuses number 4 for something completely different. Any device that has old data with field 4 (tax_id) will silently interpret it as the new field — with potentially garbage values.

---

## Section 5: The `reserved` Keyword

`reserved` prevents field numbers and field names from being reused.

```protobuf
// v2 — correct removal of tax_id
message Employee {
  string employee_id = 1;
  string name        = 2;
  double salary      = 3;

  reserved 4;           // field number 4 is permanently retired
  reserved "tax_id";    // field name "tax_id" is permanently retired
}
```

If anyone tries to use field number 4 or the name `tax_id` in a future version, `protoc` will produce a compile-time error.

**Reserving ranges:**
```protobuf
reserved 10, 11, 12;    // individual numbers
reserved 20 to 30;      // range
reserved "old_field_a", "old_field_b";  // multiple names
```

---

## Section 6: Real Migration Example — Employee v1 → v2 → v3

```protobuf
// employee_v1.proto
syntax = "proto3";

message Employee {
  string employee_id = 1;
  string name        = 2;
  double salary      = 3;
}
```

```protobuf
// employee_v2.proto — added two fields
syntax = "proto3";

message Employee {
  string employee_id = 1;
  string name        = 2;
  double salary      = 3;
  string department  = 4;   // added in v2
  string manager_id  = 5;   // added in v2
}
```

```protobuf
// employee_v3.proto — renamed salary, added bonus, removed manager_id
syntax = "proto3";

message Employee {
  string employee_id     = 1;
  string name            = 2;
  double base_salary     = 3;   // renamed from salary (safe — same field number)
  string department      = 4;
  double bonus_percentage = 6;  // added in v3 (skipped 5 because it's reserved)

  reserved 5;
  reserved "manager_id";        // manager_id removed safely
}
```

**Reading v1 data with v3 code:**
- `employee_id`, `name`, `base_salary` → present in v1 data, read correctly
- `department`, `bonus_percentage` → absent in v1 data, return `""` and `0.0`

**Reading v3 data with v1 code:**
- Fields 4, 6 → unknown, silently skipped
- v1 code sees only `employee_id`, `name`, and `salary` (now called `base_salary` internally)

---

## Section 7: Proto3 Default Values and Compatibility

In proto3, all fields are implicitly optional and have zero defaults:

| Type | Default Value |
|---|---|
| int32, int64, uint32, etc. | 0 |
| float, double | 0.0 |
| bool | false |
| string | `""` (empty string) |
| bytes | empty bytes |
| enum | first value (must be 0) |
| message | null / not set |
| repeated | empty list |

This is why proto3 removed `required` — a required field that is missing in old data would cause a parse failure, breaking backward compatibility.

---

## Section 8: Embedded-Specific Concerns

Flash memory on devices in the field holds data long after the firmware is updated. This creates a uniquely challenging compatibility scenario:

**Timeline example:**
```
2024-01: Firmware v1 ships. Writes Employee records to flash with fields 1–3.
2024-06: Firmware v2 ships. Employee has fields 1–5.
2025-03: Firmware v3 ships. Employee has fields 1, 2, 3 (renamed), 4, 6.
2027-01: Device still running v1 firmware (update failed) has 3-year-old binary data.
```

**Embedded best practices:**
1. **Add a `schema_version` field** (field number 15 to use a 1-byte tag):
   ```protobuf
   message Employee {
     int32 schema_version = 15;   // set to 1, 2, 3... per release
     // ... other fields
   }
   ```
2. **Never reuse field numbers** — treat them as permanent identifiers
3. **Reserve ALL deleted fields** immediately when removing them
4. **Test with the oldest data you must support** before each firmware release
5. **Document field history** in comments: when added, when deprecated

---

## Best Practices Checklist

1. Never reuse a field number, even after deleting the field
2. Always `reserved` a field number (and name) when removing it
3. Never change a field's type once data is in production
4. Never change a field's number once data is in production
5. Always start enum definitions with `UNKNOWN = 0`
6. Use field numbers 1–15 for the most frequently transmitted fields (1-byte tag)
7. Add `schema_version int32 = 15` to any message persisted to flash/disk
8. Document when each field was added and what it means
9. Run compatibility tests: old-schema data through new-schema decoder and vice versa
10. In embedded: review schema changes at the PR level before merging

---

## Key Takeaways

- Proto3 is forward and backward compatible by design — but only if you follow the field number rules
- The field **number** is the true identity of a field on the wire — names are just for humans and generated code
- `reserved` is your safety net: use it every time you remove or retire a field
- For embedded systems, treat field numbers as permanent hardware-level identifiers — they outlive the firmware

# Episode 2: History & Versions of Protobuf

**Series:** Protobuf for Embedded & Mobile Developers  
**Channel:** The Debugger Diary  
**Prerequisites:** Episode 1 (What is Serialization)

---

## Episode Overview

This episode covers where Protocol Buffers came from, how it evolved through proto1, proto2, and proto3, what changed in each version, and where the ecosystem stands today. Understanding the history helps you make better decisions — especially around which syntax to use and why certain design choices exist.

---

## Section 1: Origin Story — Google 2001

In 2001, Google's internal infrastructure was growing rapidly. Teams were writing services that needed to communicate with each other — passing structured data back and forth for search indexes, ad serving, user data, and configuration.

**The problem with the existing approach:**

Engineers were hand-writing code to serialize and deserialize data, often using XML or custom text formats. Every time a service added or renamed a field, other teams had to update their parsing code manually. There was no schema, no type safety, and no standard.

Some specifics:
- XML was **CPU-intensive** to parse — bad for high-throughput services
- No compile-time checking — wrong field names silently produced bugs
- Evolving the schema (adding a field) required a coordinated update across all consumers
- Different teams invented incompatible custom formats

Google engineers, primarily **Jeff Dean** and **Sanjay Ghemawat** among others, designed Protocol Buffers as the internal solution: a schema-driven, binary serialization format with generated code.

---

## Section 2: Proto1 — Internal Only (2001–2008)

Proto1 was the first internal version of Protocol Buffers at Google. It was:

- **Never publicly released**
- C++ only in its initial form
- Used to power **Stubby**, Google's internal RPC framework (the predecessor to gRPC)
- Tightly coupled to Google's internal build system (Blaze, later open-sourced as Bazel)

Proto1 proved the core idea: define your schema once in a `.proto` file, run the compiler, get generated code that handles serialization automatically. It spread rapidly inside Google because it was simply better than the alternatives.

> There is no public documentation or release for proto1. Everything you'll work with is proto2 or proto3.

---

## Section 3: Proto2 — First Open Source Release (2008)

In July 2008, Google open-sourced Protocol Buffers as **proto2** on Google Code (later moved to GitHub).

### Syntax

```protobuf
syntax = "proto2";

package school;

message Address {
  required string street = 1;
  optional string city = 2;
  optional string state = 3;
}

message Student {
  required string name = 1;
  required string student_id = 2;
  optional int32 age = 3 [default = 18];
  optional string department = 4 [default = "Undeclared"];
  repeated string courses = 5;
  optional Address address = 6;
}
```

### Key Features of Proto2

**Field labels:**
- `required` — field MUST be present; if missing during deserialization, an error is thrown
- `optional` — field may or may not be present; you can check `has_field()` to know
- `repeated` — a list (zero or more values)

**Custom default values:**
```protobuf
optional int32 age = 3 [default = 18];
optional string status = 4 [default = "active"];
```
If a field is not set, it returns its custom default instead of the zero value.

**Extensions:**
Proto2 had an `extensions` mechanism that allowed external `.proto` files to add fields to a message:
```protobuf
message Student {
  // ...
  extensions 100 to 199;
}

extend Student {
  optional string alumni_id = 100;
}
```
This was rarely used cleanly and was replaced by `google.protobuf.Any` in proto3.

**Generated code patterns:**
Proto2 generated `has_field()` methods for optional fields, letting you distinguish "field not set" from "field set to zero/empty":
```python
if student.HasField("age"):
    print("age was explicitly set")
```

### The Problem with `required`

In hindsight, `required` was a mistake. Once deployed, you could never safely remove a required field — old code would fail to deserialize data from new code that omitted the field. Teams found themselves stuck with required fields forever. This is why proto3 removed it entirely.

---

## Section 4: Proto3 — The Modern Standard (2016)

Proto3 launched in 2016 as a major simplification of proto2.

### Syntax

```protobuf
syntax = "proto3";

package school;

message Address {
  string street = 1;
  string city = 2;
  string state = 3;
}

message Student {
  string name = 1;
  string student_id = 2;
  int32 age = 3;
  string department = 4;
  repeated string courses = 5;
  Address address = 6;
}
```

Notice: no field labels (except `repeated`), no defaults, cleaner syntax.

### What Changed in Proto3

**Removed `required`:**  
All fields are implicitly optional. This enables safe schema evolution — you can add and remove fields without breaking old/new code combinations.

**Removed custom defaults:**  
All unset fields return their type's zero value:
- Numeric types → `0`
- Strings → `""`
- Booleans → `false`
- Messages → `null` / not set
- Enums → first value (must be `0`)

**Added built-in JSON mapping:**  
Proto3 messages can be serialized to/from JSON canonically. Field names map to `camelCase` JSON keys automatically.

**Removed extensions:**  
Use `google.protobuf.Any` instead.

**Widened language support:**  
Added official generators for Go, Ruby, C#, JavaScript, PHP. Community support for Swift, Kotlin, Dart, Rust followed.

---

## Section 5: Proto2 vs Proto3 Comparison Table

| Feature | Proto2 | Proto3 |
|---------|--------|--------|
| `required` fields | ✅ Yes | ❌ Removed |
| `optional` keyword | ✅ Explicit | ✅ Implicit (all fields) |
| `repeated` fields | ✅ Yes | ✅ Yes |
| Custom default values | ✅ `[default = x]` | ❌ Zero values only |
| `has_field()` check | ✅ For optional fields | ❌ Not available (unless `optional` keyword used in proto3) |
| Extensions | ✅ Yes | ❌ Use `Any` |
| JSON mapping | ❌ No built-in | ✅ Built-in |
| Enums first value | Any value | Must be `0` |
| `oneof` | ✅ Basic | ✅ Enhanced |
| Languages | C++, Java, Python | + Go, C#, Ruby, JS, PHP, Swift, Kotlin, Dart |

### When to use proto2 today
Only if you're maintaining an existing proto2 codebase or need `has_field()` semantics for distinguishing "not set" from "set to zero." For all new projects, use proto3.

---

## Section 6: gRPC & Ecosystem Growth (2015 Onwards)

The launch of **gRPC in 2015** was a turning point for protobuf adoption outside Google.

gRPC is an open-source RPC framework that uses:
- Protocol Buffers as its **Interface Definition Language (IDL)** and wire format
- HTTP/2 as the transport protocol
- Bidirectional streaming support

With gRPC, protobuf went from "Google's internal tool" to "the standard for service-to-service communication" across the industry. Companies like Netflix, Lyft, Cisco, CoreOS, and Square adopted it.

**Timeline of growth:**

| Year | Event |
|------|-------|
| 2015 | gRPC open-sourced — protobuf becomes its default wire format |
| 2016 | CNCF (Cloud Native Computing Foundation) adopts gRPC |
| 2017 | Kubernetes uses protobuf for internal API serialization |
| 2018 | Envoy proxy uses protobuf for all configuration (xDS API) |
| 2020 | Android Jetpack **DataStore** (replaces SharedPreferences) uses proto3 |
| 2021 | Buf CLI launched — modern build tooling for .proto files |
| 2022 | Protobuf repository moved to github.com/protocolbuffers/protobuf |

---

## Section 7: Protobuf Editions (2023)

Protobuf Editions is a new approach introduced in 2023 that replaces the `syntax = "proto2"` / `syntax = "proto3"` distinction.

### The Problem Editions Solves

Proto2 and proto3 are really just **presets** of feature flags. Some teams want proto3's simplicity but proto2's `has_field()` semantics. With the old system, you had to choose one or the other.

Editions lets you specify exactly which behaviors you want using `features`:

```protobuf
edition = "2023";

package school;

message Student {
  string name = 1;
  int32 age = 2;

  // Explicit presence tracking (like proto2 optional)
  string student_id = 3 [features.field_presence = EXPLICIT];

  repeated string courses = 4;
}
```

### Key Concepts

- `edition = "2023"` replaces `syntax = "proto2/proto3"`
- Feature flags control individual behaviors (field presence, enum semantics, JSON mapping, etc.)
- Proto2 and proto3 will eventually be "compiled down" to editions internally
- **Current status (2024):** Editions is stable but proto3 remains the recommended default for new projects

> For this series, we use **proto3**. Editions is worth knowing exists, but you won't encounter it in most projects yet.

---

## Section 8: Where Protobuf Is Used Today

**At Google:**
- Billions of internal RPC calls per day
- Most internal services define their APIs as `.proto` files
- Google Cloud APIs are published as `.proto` files in the `googleapis` repository

**In the Android ecosystem:**
- **Jetpack DataStore** (the modern replacement for SharedPreferences) uses proto3 for typed persistent storage
- **Firebase** uses protobuf internally

**In cloud-native infrastructure:**
- **Kubernetes API server** uses protobuf for internal communication (alongside JSON for the external API)
- **Envoy proxy** — the entire xDS configuration protocol is protobuf
- **Istio** service mesh — built on Envoy, all protobuf

**In embedded/IoT:**
- **nanopb** brings proto3 to microcontrollers (STM32, ESP32, Arduino)
- Used in drone firmware, industrial sensors, wearables

---

## Key Takeaways

- Protobuf started at Google in 2001 to solve the problem of hand-written, schema-less serialization
- **Proto1** was never public; **proto2** was the first open source release (2008)
- **Proto3** (2016) simplified the syntax, removed `required`, added JSON mapping and more languages
- The main difference you'll feel day-to-day: proto3 has no `required`, no custom defaults, and has built-in JSON support
- **gRPC** (2015) massively expanded protobuf's reach beyond Google
- **Protobuf Editions** (2023) is the future, but proto3 is the standard today
- Use **proto3** for all new projects

---

## Further Reading

- Official protobuf GitHub repository: `github.com/protocolbuffers/protobuf`
- Proto2 vs Proto3 language guide (protobuf.dev)
- gRPC history and motivation (grpc.io)
- Buf CLI and modern protobuf tooling (buf.build)
- Protobuf Editions design docs (protobuf.dev/editions)
- Android Jetpack DataStore with Proto (developer.android.com)
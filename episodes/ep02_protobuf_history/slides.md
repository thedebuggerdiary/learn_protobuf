---
marp: true
theme: default
paginate: true
backgroundColor: #ffffff
---

# History & Versions of Protobuf
## Episode 2 — Protobuf for Embedded & Mobile Developers
**The Debugger Diary**

---

## The Problem Google Faced (2001)

Before protobuf, Google engineers wrote **hand-crafted code** to marshal/unmarshal data for every internal service.

**Pain points:**
- XML parsing was slow and CPU-heavy
- No schema enforcement — bugs from mismatched field names
- Adding a new field required updating parsers everywhere
- Thousands of internal services, no standard

> *"We need something faster, smaller, and easier to evolve."*

---

## Proto1: Google Internal (2001–2008)

- Developed internally at Google around **2001**
- Never released publicly
- Designed for Google's internal RPC system (**Stubby**)
- C++ only initially
- Proved the concept: schema-driven binary serialization works

---

## Proto2: First Public Release (2008)

```protobuf
syntax = "proto2";

message Student {
  required string name = 1;
  optional int32 age = 2 [default = 18];
  repeated string courses = 3;
}
```

**Key features:**
- `required` / `optional` / `repeated` field labels
- Custom default values
- Extensions mechanism
- Generated code for C++, Java, Python

---

## Proto3: The Modern Standard (2016)

```protobuf
syntax = "proto3";

message Student {
  string name = 1;
  int32 age = 2;
  repeated string courses = 3;
}
```

**What changed:**
- Removed `required` (caused deployment headaches)
- No custom defaults — all fields use zero values
- Cleaner, simpler syntax
- Built-in JSON mapping

---

## Proto3: What's New vs Proto2

| Change | Proto2 | Proto3 |
|--------|--------|--------|
| Field labels | required/optional/repeated | only repeated kept |
| Custom defaults | ✅ `[default = x]` | ❌ zero values only |
| required fields | ✅ | ❌ removed |
| JSON mapping | ❌ manual | ✅ built-in |
| Extensions | ✅ | ❌ use `Any` instead |
| `oneof` improvements | basic | enhanced |

---

## Language Support Growth

**Proto2 (2008):** C++, Java, Python

**Proto3 (2016) added:**
- Go, Ruby, C#, JavaScript, PHP

**Community & official additions:**
- Swift (Apple), Kotlin, Dart (Flutter), Rust

**Today:** 10+ officially supported languages

---

## Key Milestones in the Ecosystem

| Year | Milestone |
|------|-----------|
| 2001 | Proto1 — Google internal |
| 2008 | Proto2 — open sourced on Google Code |
| 2015 | **gRPC launched** — uses protobuf as default wire format |
| 2016 | Proto3 released |
| 2020 | Android Jetpack DataStore adopts protobuf |
| 2022 | Protobuf moved to GitHub (github.com/protocolbuffers) |
| 2023 | **Protobuf Editions** introduced |

---

## Protobuf Editions (2023)

The next evolution — replaces `syntax = "proto2/proto3"` with **feature flags**.

```protobuf
edition = "2023";

message Student {
  string name = 1;
  int32 age = 2 [features.field_presence = EXPLICIT];
  repeated string courses = 3;
}
```

**Why?** Proto2 and proto3 are just presets of features. Editions let you pick exactly what you need.

> Still stabilizing — **use proto3 for new projects today**

---

## The Modern Ecosystem

| Tool | Purpose |
|------|---------|
| `protoc` | Official compiler |
| `buf` CLI | Modern build tool for .proto files |
| `protoc-gen-go` | Go code generator |
| `protoc-gen-validate` | Validation rules for messages |
| `connect-go` | Modern gRPC alternative |
| `nanopb` | Protobuf for microcontrollers (C) |

---

## Why Protobuf Is Still Everywhere

- Google processes **billions of RPC calls per day** using protobuf
- **gRPC** (used by Kubernetes, Envoy, Netflix, etc.) defaults to protobuf
- **Android Jetpack DataStore** uses proto3 for typed storage
- **Envoy Proxy** — all config via protobuf
- **Kubernetes API** — internal communication uses protobuf

> Battle-tested at the largest scale in the world.

---

## Summary

```
2001  →  Proto1 (Google internal)
2008  →  Proto2 (open source, required/optional/repeated)
2016  →  Proto3 (simplified, JSON mapping, more languages)
2023  →  Editions (feature flags, the future)
```

**For this series:** We use **proto3** — the current standard.

---

## What's Next

### Episode 3: Your First .proto File & Message Types

- Install protoc
- Write a Student message from scratch
- All scalar types, nested messages, enums, oneof, repeated, maps
- Generate code for Python and C
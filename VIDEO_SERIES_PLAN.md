# Protobuf for Embedded & Mobile Developers
**Channel:** The Debugger Diary

## Series Goal

This series teaches Protocol Buffers (protobuf) from the ground up, with a focus on developers working on embedded systems (ESP32, STM32, Arduino) and mobile platforms (Android, iOS). You will learn what serialization is, why protobuf exists, how to define schemas, and how to serialize and deserialize structured data in both Python and C/C++. Each episode is standalone — you can watch them in order or jump to the topic you need.

---

## Episode Plan

| # | Title | Key Topics | Demo | Duration Est. |
|---|-------|-----------|------|--------------|
| 1 | What is Serialization & Why Protobuf? | Serialization concept, JSON/XML/binary formats compared, where protobuf wins | Student struct as JSON vs XML vs protobuf bytes | 12–15 min |
| 2 | History & Versions of Protobuf | proto1 → proto2 → proto3 → Editions, Google origin, open-source timeline | Side-by-side proto2 vs proto3 syntax | 10–12 min |
| 3 | Your First .proto File & Message Types | protoc, scalar types, nested messages, enum, oneof, repeated, map, well-known types | student.proto with all major constructs | 18–22 min |
| 4 | Serialize & Deserialize in Python | pip install protobuf, protoc --python_out, SerializeToString, ParseFromString, write/read binary file | Write 5 Employee records to employees.bin, read back | 15–18 min |
| 5 | C/C++ with nanopb (Embedded) | Why nanopb, .options file, pb_encode, pb_decode, static memory, ESP32/STM32 | Serialize Student struct to buffer in C, decode and print | 18–22 min |
| 6 | Schema Evolution & Best Practices | Safe vs unsafe changes, reserved fields, backward/forward compatibility | Evolve employee.proto across two versions | 12–15 min |
| 7 | gRPC: A Quick Intro | What is gRPC, protobuf as IDL, service definition, 4 call types | Show a .proto service definition | 10–12 min |

**Total series:** ~95–116 minutes across 7 episodes

---

## Prerequisites

### Knowledge
- Basic programming experience (any language)
- Understanding of what a struct/class/object is
- For Episode 5: basic C syntax (structs, pointers, arrays)

### Tools to Install

**protoc (Protocol Buffer Compiler)**
- Download from the official protobuf GitHub releases page
- Version: 25.x or later (proto3 support)
- Add to PATH so `protoc --version` works in terminal

**Python** (Episodes 1, 4)
- Python 3.8 or later
- `pip install protobuf` (version 4.x or 5.x)
- `pip install grpcio-tools` (for protoc Python plugin)

**nanopb** (Episode 5)
- Download from the nanopb GitHub repository
- Requires Python (for the generator script)
- C compiler: GCC, Clang, or any embedded toolchain (arm-none-eabi-gcc, xtensa-esp32-elf-gcc)

**Marp** (for presenting slides)
- VS Code extension: "Marp for VS Code"
- Or CLI: `npm install -g @marp-team/marp-cli`

---

## Repository Structure

```
learn_protobuf/
├── VIDEO_SERIES_PLAN.md       ← You are here
├── README.md
├── episodes/
│   ├── ep01_what_is_serialization/
│   │   ├── slides.md          ← Marp presentation
│   │   └── notes.md           ← Full reference + source code
│   ├── ep02_protobuf_history/
│   ├── ep03_proto_syntax_message_types/
│   ├── ep04_python_serialize_deserialize/
│   ├── ep05_cpp_nanopb_embedded/
│   ├── ep06_schema_evolution/
│   └── ep07_grpc_intro/
└── demos/
    ├── ep03_basics/
    │   └── student.proto
    ├── ep04_python/
    │   ├── employee.proto
    │   ├── serialize_demo.py
    │   └── deserialize_demo.py
    └── ep05_cpp/
        ├── student.proto
        ├── student.options
        └── main.c
```

---

## How to Use This Repo

- **Slides** (`slides.md`): Open in VS Code with the Marp extension to get a live preview. Export to PDF or HTML for recording.
- **Notes** (`notes.md`): Full script/reference. Read before recording. Contains all source code, explanations, and talking points.
- **Demos**: Runnable code for each episode. Follow the README in each demo folder.

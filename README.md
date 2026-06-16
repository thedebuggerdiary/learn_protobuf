# Protobuf for Embedded & Mobile Developers

A YouTube video series by **The Debugger Diary** that teaches Protocol Buffers from scratch, with a focus on embedded systems (ESP32, STM32, Arduino) and mobile development (Android, iOS).

You will learn how to define structured data schemas, serialize them to compact binary, save to files, and deserialize — all in Python and C/C++.

---

## Who This Is For

- Embedded developers working with MCUs who need efficient data storage or transmission
- Mobile developers who want to understand binary serialization beyond JSON
- Anyone curious about how Google's data format works under the hood

No prior protobuf knowledge needed. Basic programming experience (any language) is enough for Episodes 1–3. Episode 5 requires basic C.

---

## Episodes

| # | Folder | Title |
|---|--------|-------|
| 1 | [ep01_what_is_serialization](episodes/ep01_what_is_serialization/) | What is Serialization & Why Protobuf? |
| 2 | [ep02_protobuf_history](episodes/ep02_protobuf_history/) | History & Versions of Protobuf |
| 3 | [ep03_proto_syntax_message_types](episodes/ep03_proto_syntax_message_types/) | Your First .proto File & Message Types |
| 4 | [ep04_python_serialize_deserialize](episodes/ep04_python_serialize_deserialize/) | Serialize & Deserialize in Python |
| 5 | [ep05_cpp_nanopb_embedded](episodes/ep05_cpp_nanopb_embedded/) | C/C++ with nanopb (Embedded) |
| 6 | [ep06_schema_evolution](episodes/ep06_schema_evolution/) | Schema Evolution & Best Practices |
| 7 | [ep07_grpc_intro](episodes/ep07_grpc_intro/) | gRPC: A Quick Intro |

---

## How to Use This Repo

Each episode folder contains two files:

- **`slides.md`** — Marp Markdown presentation. Open in VS Code with the [Marp for VS Code](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode) extension for a live slide preview. Export to PDF/HTML for screen recording.
- **`notes.md`** — Complete reference document with full explanations, all source code, talking points, and further reading.

---

## Setup

### Install protoc (Protocol Buffer Compiler)

Download the latest release from the protobuf GitHub releases page. Add the `bin/` folder to your PATH.

```bash
protoc --version
# libprotoc 25.x
```

### Python (Episodes 1, 4)

```bash
pip install protobuf
pip install grpcio-tools
```

### nanopb for C/C++ (Episode 5)

Download nanopb from its GitHub repository. You need:
- `nanopb/` source directory
- Python (already installed) for the `.proto` → `.pb.c/.pb.h` generator

### Marp (for slides)

Install the **Marp for VS Code** extension, or use the CLI:

```bash
npm install -g @marp-team/marp-cli
marp episodes/ep01_what_is_serialization/slides.md --pdf
```

---

## Demos

Runnable code is in the `demos/` folder:

```
demos/
├── ep03_basics/      student.proto
├── ep04_python/      employee.proto, serialize_demo.py, deserialize_demo.py
└── ep05_cpp/         student.proto, student.options, main.c
```

---

## See Also

- `VIDEO_SERIES_PLAN.md` — full episode breakdown with topics, demos, and duration estimates

---
marp: true
theme: default
paginate: true
backgroundColor: #ffffff
---

# gRPC: A Quick Intro
### Episode 7 — Protobuf for Embedded & Mobile Developers
**The Debugger Diary**

---

# What is RPC?

**RPC = Remote Procedure Call**

The idea: call a function that runs on a different machine, but make it look like a local function call.

```
// Without RPC — manual HTTP + JSON
response = http_post("/api/getStudent", json.dumps({"id": "STU001"}))
student = json.loads(response.text)

// With gRPC — feels like a local function call
student = stub.GetStudent(GetStudentRequest(student_id="STU001"))
```

The complexity of serialization, HTTP, and deserialization is hidden from you.

---

# What is gRPC?

- **g**oogle **R**emote **P**rocedure **C**all
- Open-sourced by Google in **2015**
- Built on **HTTP/2** (multiplexing, streaming, low latency)
- Uses **Protocol Buffers** as both:
  - The **IDL** (Interface Definition Language) — define your API in `.proto`
  - The **wire format** — protobuf binary is what travels over the network

```
Your .proto file defines BOTH the data AND the API.
```

---

# The Role of Protobuf in gRPC

```
student.proto
    │
    ├── message Student { ... }         ← data format (Ep 3–6)
    ├── message GetStudentRequest { ... }
    │
    └── service StudentService {        ← API definition (this episode)
          rpc GetStudent(...) ...
        }
```

The same `.proto` file you've been writing now also describes your API endpoints.

---

# Service Definition Syntax

```protobuf
syntax = "proto3";

package school;

service StudentService {
  rpc GetStudent      (GetStudentRequest)  returns (Student);
  rpc CreateStudent   (Student)            returns (CreateResponse);
  rpc ListStudents    (ListRequest)        returns (stream Student);
  rpc UploadStudents  (stream Student)     returns (UploadSummary);
}

message GetStudentRequest {
  string student_id = 1;
}

message ListRequest {
  string department = 1;
}

message CreateResponse { bool success = 1; string id = 2; }
message UploadSummary  { int32 created = 1; int32 failed = 2; }
```

---

# The 4 Call Types

```
┌─────────────────────────────────────────────────────────┐
│ 1. Unary          Client ──► Server ──► Client          │
│    One request, one response.                           │
│    Like a regular function call.                        │
│                                                         │
│ 2. Server Stream  Client ──► Server ══► Client          │
│    One request, stream of responses.                    │
│    e.g., live data feed from a device                   │
│                                                         │
│ 3. Client Stream  Client ══► Server ──► Client          │
│    Stream of requests, one response.                    │
│    e.g., bulk upload / batch create                     │
│                                                         │
│ 4. Bidirectional  Client ══► Server ══► Client          │
│    Both sides stream simultaneously.                    │
│    e.g., real-time chat or command+telemetry            │
└─────────────────────────────────────────────────────────┘
```

---

# Unary — Most Common

```protobuf
rpc GetStudent (GetStudentRequest) returns (Student);
```

```python
# Client side (Python)
stub = StudentServiceStub(channel)
request = GetStudentRequest(student_id="STU001")
student = stub.GetStudent(request)

print(student.name)   # "Alice"
print(student.gpa)    # 3.8
```

One request → one response. Protobuf handles serialization on both sides.

---

# Server Streaming

```protobuf
rpc ListStudents (ListRequest) returns (stream Student);
```

```python
# Client receives a stream of Student messages
request = ListRequest(department="Computer Science")
for student in stub.ListStudents(request):
    print(f"{student.name} — GPA: {student.gpa}")
```

Server sends one Student at a time as they're retrieved.
Client processes each as it arrives — no waiting for the full list.

---

# Generating Code from .proto

```bash
# Install gRPC tools for Python
pip install grpcio grpcio-tools

# Generate both protobuf + gRPC stubs
python -m grpc_tools.protoc \
    --python_out=. \
    --grpc_python_out=. \
    student.proto
```

Output files:
```
student_pb2.py       ← message classes (same as before)
student_pb2_grpc.py  ← StudentServiceStub (client) + StudentServiceServicer (server)
```

The stub is the client. The servicer is the server base class you implement.

---

# Where gRPC Is Used

```
┌───────────────────────────────────────────────────────┐
│  Mobile App (Android/iOS)                             │
│      ↕ gRPC over HTTP/2                               │
│  Backend Service (Go / Java / Python)                 │
│      ↕ gRPC internal                                  │
│  Microservices (hundreds of them at Google scale)     │
└───────────────────────────────────────────────────────┘
```

- Android: `grpc-java` / `grpc-kotlin`
- iOS: `grpc-swift`
- Kubernetes: internal service mesh uses gRPC
- Google Cloud APIs: all exposed via gRPC (and transcoded to REST)

---

# gRPC vs REST

| | gRPC | REST |
|---|---|---|
| Protocol | HTTP/2 | HTTP/1.1 (usually) |
| Format | Protobuf (binary) | JSON (text) |
| Schema | Strict (generated) | Optional (OpenAPI) |
| Streaming | Native | Workarounds (SSE, WS) |
| Type safety | Strong | Weak |
| Human readable | No | Yes |
| Browser support | Limited (grpc-web) | Native |
| Performance | Faster | Slower |

gRPC wins on performance and type safety. REST wins on simplicity and browser support.

---

# gRPC on Mobile

**Android**
```kotlin
// grpc-kotlin
val channel = ManagedChannelBuilder.forAddress("api.school.com", 443)
    .useTransportSecurity().build()
val stub = StudentServiceGrpcKt.StudentServiceCoroutineStub(channel)
val student = stub.getStudent(getStudentRequest { studentId = "STU001" })
```

**iOS**
```swift
// grpc-swift
let channel = ClientConnection.usingTLSBackedByNIOSSL(on: group)
    .connect(host: "api.school.com", port: 443)
let client = School_StudentServiceClient(channel: channel)
let request = School_GetStudentRequest.with { $0.studentID = "STU001" }
let student = try await client.getStudent(request)
```

---

# What This Series Didn't Cover (Next Series)

This was just an intro. A full gRPC series would cover:

- TLS / mTLS authentication
- Interceptors and middleware
- Deadlines, timeouts, and cancellation
- Error codes and rich error details
- Load balancing and service discovery
- gRPC-web (browser support)
- Connect protocol (gRPC-compatible, REST-friendly)

---

# Series Recap

| Episode | Topic |
|---|---|
| 1 | What is serialization? Why protobuf? |
| 2 | History: proto1 → proto2 → proto3 → Editions |
| 3 | .proto syntax and all message types |
| 4 | Serialize/deserialize in Python |
| 5 | nanopb for embedded C (ESP32, STM32) |
| 6 | Schema evolution & best practices |
| 7 | gRPC quick intro (this episode) |

---

# Thank You!

## What's Next for You

- Try Episode 4's Python demo: `python serialize_demo.py`
- Build the C demo from Episode 5
- Define your own `.proto` for a project you're working on
- Subscribe for the **gRPC Deep Dive** series coming soon

**The Debugger Diary** — Embedded & Mobile Development

_"Understand the tools, not just the syntax."_

# Episode 7 — gRPC: A Quick Intro

**Series:** Protobuf for Embedded & Mobile Developers  
**Channel:** The Debugger Diary  
**Prerequisites:** Episodes 1–6 (especially Ep3 — .proto syntax)

---

## Episode Overview

This final episode of the series gives a high-level introduction to gRPC — showing how Protocol Buffers serve as the foundation for defining and calling remote services. This is not a deep dive; a dedicated gRPC series will cover implementation in detail. The goal here is to connect what you've learned about protobuf to the broader ecosystem it powers.

---

## Section 1: What is RPC?

**RPC (Remote Procedure Call)** is the concept of calling a function that executes on a different process or machine, but making it feel like a local function call.

**History of RPC systems:**
- **CORBA (1991)** — complex, language-agnostic, largely obsolete
- **SOAP / XML-RPC (late 1990s)** — XML-based, verbose, browser-friendly
- **Apache Thrift (2007)** — Facebook's solution, similar to protobuf+gRPC
- **gRPC (2015)** — Google's solution, built on HTTP/2 and protobuf

**Without RPC (raw HTTP + JSON):**
```python
import requests, json

payload = json.dumps({"student_id": "STU001"})
response = requests.post("https://api.school.com/v1/students/get",
                         data=payload,
                         headers={"Content-Type": "application/json"})
student = json.loads(response.text)
print(student["name"])
```

**With gRPC:**
```python
student = stub.GetStudent(GetStudentRequest(student_id="STU001"))
print(student.name)
```

The gRPC version handles serialization, HTTP/2, TLS, and deserialization for you. It also gives you a type-safe API with IDE autocomplete.

---

## Section 2: What is gRPC?

gRPC was developed at Google (open-sourced in February 2015). It is built on:

- **HTTP/2** — multiplexed streams, binary framing, header compression, persistent connections
- **Protocol Buffers** — both the IDL (how you define the API) and the wire format (what travels over the network)

**Supported languages:**
C, C++, Java, Kotlin, Python, Go, Swift, Dart, JavaScript (Node.js), Ruby, PHP, C#

**Key advantages over REST:**
- Strict schema → generated client and server code in any language
- Binary wire format → smaller payloads, faster parsing
- HTTP/2 multiplexing → multiple in-flight RPCs on a single connection
- Native streaming → server push, client upload streams, bidirectional

---

## Section 3: Service Definition in .proto

A gRPC API is defined directly in your `.proto` file using a `service` block.

```protobuf
syntax = "proto3";

package school;

import "google/protobuf/empty.proto";

// --- Message definitions (same as always) ---

message Student {
  string student_id  = 1;
  string name        = 2;
  int32  age         = 3;
  double gpa         = 4;
  string department  = 5;
}

message GetStudentRequest {
  string student_id = 1;
}

message ListStudentsRequest {
  string department = 1;    // filter by department
  int32  page_size  = 2;
}

message CreateStudentResponse {
  bool   success    = 1;
  string student_id = 2;
  string error_msg  = 3;
}

message BatchUploadSummary {
  int32 created = 1;
  int32 updated = 2;
  int32 failed  = 3;
}

message ChatMessage {
  string sender  = 1;
  string content = 2;
  int64  timestamp_ms = 3;
}

// --- Service definition ---

service StudentService {
  // Unary: get one student by ID
  rpc GetStudent (GetStudentRequest) returns (Student);

  // Unary: create a student
  rpc CreateStudent (Student) returns (CreateStudentResponse);

  // Server streaming: list students, one at a time
  rpc ListStudents (ListStudentsRequest) returns (stream Student);

  // Client streaming: bulk upload students
  rpc BatchUpload (stream Student) returns (BatchUploadSummary);

  // Bidirectional: real-time chat (not typical for student APIs, shown for demo)
  rpc LiveChat (stream ChatMessage) returns (stream ChatMessage);
}
```

---

## Section 4: The 4 Call Types

### 4.1 Unary RPC
One request → one response. This is the most common type — equivalent to a single HTTP GET or POST.

```
Client                    Server
  │── GetStudentRequest ──►│
  │◄── Student ────────────│
```

```python
# Python client
student = stub.GetStudent(GetStudentRequest(student_id="STU001"))
```

### 4.2 Server Streaming RPC
One request → a stream of responses. The server sends multiple messages back before closing.

```
Client                    Server
  │── ListStudentsRequest ►│
  │◄── Student 1 ──────────│
  │◄── Student 2 ──────────│
  │◄── Student 3 ──────────│
  │◄── (stream closes) ────│
```

```python
# Client iterates over the stream
for student in stub.ListStudents(ListStudentsRequest(department="CS")):
    print(f"{student.name}: {student.gpa}")
```

**Embedded use case:** A mobile app subscribes to a stream of live sensor readings from a gateway device.

### 4.3 Client Streaming RPC
The client sends a stream of messages → server processes all of them and returns a single response.

```
Client                    Server
  │── Student 1 ──────────►│
  │── Student 2 ──────────►│
  │── Student 3 ──────────►│
  │── (stream closes) ─────│
  │◄── BatchUploadSummary ─│
```

```python
def generate_students():
    for row in csv_file:
        yield Student(name=row["name"], gpa=float(row["gpa"]))

summary = stub.BatchUpload(generate_students())
print(f"Created {summary.created}, failed {summary.failed}")
```

### 4.4 Bidirectional Streaming RPC
Both sides stream simultaneously. Neither side waits for the other to finish.

```
Client                    Server
  │═══════════════════════►│
  │◄═══════════════════════│
```

Used for: real-time command+telemetry, collaborative editing, live bidirectional device control.

---

## Section 5: Generating Code

```bash
# Install Python gRPC tools
pip install grpcio grpcio-tools

# Generate protobuf + gRPC stubs together
python -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. \
    student.proto
```

**Output:**
- `student_pb2.py` — message classes (same as Episode 4)
- `student_pb2_grpc.py` — contains:
  - `StudentServiceStub` — client class (call this from app code)
  - `StudentServiceServicer` — server base class (implement this in your server)
  - `add_StudentServiceServicer_to_server()` — registration function

**Minimal server example:**
```python
import grpc
from concurrent import futures
import student_pb2, student_pb2_grpc

class StudentServiceServicer(student_pb2_grpc.StudentServiceServicer):
    def GetStudent(self, request, context):
        # In real code: query a database
        return student_pb2.Student(
            student_id=request.student_id,
            name="Alice",
            gpa=3.8
        )

server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
student_pb2_grpc.add_StudentServiceServicer_to_server(StudentServiceServicer(), server)
server.add_insecure_port('[::]:50051')
server.start()
server.wait_for_termination()
```

**Minimal client example:**
```python
import grpc
import student_pb2, student_pb2_grpc

channel = grpc.insecure_channel('localhost:50051')
stub = student_pb2_grpc.StudentServiceStub(channel)

response = stub.GetStudent(student_pb2.GetStudentRequest(student_id="STU001"))
print(f"Name: {response.name}, GPA: {response.gpa}")
```

---

## Section 6: gRPC vs REST

| Property | gRPC | REST |
|---|---|---|
| Protocol | HTTP/2 | HTTP/1.1 (or HTTP/2 with REST) |
| Wire format | Protobuf (binary) | JSON (text) |
| Schema | Strict (.proto) | Optional (OpenAPI/Swagger) |
| Code generation | Native | Via OpenAPI tools |
| Streaming | Native (4 modes) | Workarounds (SSE, WebSocket) |
| Type safety | Strong (compile-time) | Weak (runtime) |
| Human readable | No | Yes |
| Browser support | Limited (grpc-web) | Native |
| Latency | Lower | Higher |
| Payload size | Smaller | Larger |

**When to choose REST over gRPC:**
- Public API consumed by browsers
- Team is unfamiliar with protobuf/gRPC
- You need human-readable wire format for debugging
- Third-party integrations that only support JSON

**When to choose gRPC:**
- Mobile-to-backend with performance constraints
- Microservices talking to each other
- Bidirectional streaming requirements
- You want strict, enforced API contracts

---

## Section 7: gRPC on Mobile

### Android (grpc-kotlin)
```kotlin
// build.gradle
implementation("io.grpc:grpc-kotlin-stub:1.4.1")
implementation("io.grpc:grpc-android:1.61.0")

// Create channel
val channel = ManagedChannelBuilder
    .forAddress("api.school.com", 443)
    .useTransportSecurity()
    .build()

// Create stub
val stub = StudentServiceGrpcKt.StudentServiceCoroutineStub(channel)

// Make a call (inside a coroutine)
val student = stub.getStudent(getStudentRequest {
    studentId = "STU001"
})
println(student.name)
```

### iOS (grpc-swift)
```swift
// Package.swift dependency: grpc-swift

import GRPC
import NIOCore
import NIOPosix

let group = MultiThreadedEventLoopGroup(numberOfThreads: 1)
let channel = try GRPCChannelPool.with(
    target: .host("api.school.com", port: 443),
    transportSecurity: .tls(.makeClientDefault()),
    eventLoopGroup: group
)

let client = School_StudentServiceClient(channel: channel)
let request = School_GetStudentRequest.with { $0.studentID = "STU001" }
let response = try await client.getStudent(request)
print(response.name)
```

---

## Section 8: What This Series Didn't Cover (gRPC Teaser)

A full gRPC series would include:

- **Authentication** — TLS certificates, mTLS, token-based auth with interceptors
- **Interceptors** — middleware for logging, metrics, auth, retry logic
- **Deadlines and cancellation** — setting timeouts on calls
- **Error handling** — gRPC status codes (`NOT_FOUND`, `UNAVAILABLE`, etc.) and rich error details
- **Load balancing** — client-side and server-side, service mesh integration
- **gRPC-web** — enabling gRPC from browsers (Envoy proxy or Connect protocol)
- **buf CLI** — modern alternative to protoc for managing .proto files and plugins
- **Reflection** — querying a running gRPC server for its schema at runtime

---

## Section 9: Series Recap

| Episode | Title | Key Skill |
|---|---|---|
| 1 | What is Serialization? | Understand why binary formats exist |
| 2 | History of Protobuf | Know proto2 vs proto3 vs Editions |
| 3 | .proto Syntax & Message Types | Write .proto files with all field types |
| 4 | Serialize/Deserialize in Python | Read/write binary files with protobuf |
| 5 | nanopb for Embedded C | Use protobuf on ESP32/STM32 without heap |
| 6 | Schema Evolution | Safely change .proto without breaking data |
| 7 | gRPC Quick Intro | Understand how protobuf powers gRPC APIs |

---

## Key Takeaways

- gRPC = HTTP/2 transport + protobuf wire format + generated client/server code
- Your `.proto` file defines both the data schema AND the API contract
- 4 call types: unary, server stream, client stream, bidirectional
- gRPC beats REST on performance and type safety; REST beats gRPC on browser support and simplicity
- The same `.proto` message types you learned in Episodes 3–6 are used directly in gRPC service definitions

---

## Next Steps

- Run the Python demo from Episode 4 end-to-end
- Build a simple gRPC server and client using the StudentService from this episode
- Explore `buf.build` — a modern, hosted registry and toolchain for protobuf
- Try protobuf with Android DataStore (Jetpack) for local storage
- Subscribe for the gRPC Deep Dive series

---
marp: true
theme: default
paginate: true
backgroundColor: #ffffff
---

# Protobuf in C with nanopb
## Embedded Edition
### Episode 5 — Protobuf for Embedded & Mobile Developers
**The Debugger Diary**

---

# The Problem with Full Protobuf on MCUs

| Library | ROM Footprint | Dynamic Memory |
|---|---|---|
| protobuf-c (full) | ~300 KB | Yes (malloc) |
| nanopb | ~3–5 KB | **No** |

Most MCUs have **64–256 KB flash total.**

Full protobuf-c takes more space than the entire available flash.

---

# Enter nanopb

- Pure C99 — runs on **any** MCU with a C compiler
- < 5 KB ROM, < 300 bytes RAM
- **Zero dynamic memory** — no malloc, no heap
- Generates plain C structs from your `.proto` file
- Works with: **ESP32, STM32, Arduino, RP2040, nRF52, AVR**

> nanopb = protobuf protocol + embedded constraints

---

# Target Hardware

```
┌──────────────────────────────────────┐
│  ESP32      → WiFi/BLE IoT devices   │
│  STM32      → Industrial, motor ctrl │
│  Arduino    → Prototyping, learning  │
│  RP2040     → Raspberry Pi Pico      │
│  nRF52840   → BLE wearables          │
└──────────────────────────────────────┘
```

All of these can run nanopb with the same generated code.

---

# Installing nanopb

**Option 1 — via pip (generates code from .proto)**
```bash
pip install nanopb
```

**Option 2 — download release (for build system integration)**
```
nanopb/
  pb.h
  pb_encode.h / pb_encode.c
  pb_decode.h / pb_decode.c
  pb_common.h / pb_common.c
```

Add those 6 files to your project. That's it.

---

# The .options File — Why It Exists

Protobuf strings and repeated fields have **variable length**.

On a PC, nanopb can use callbacks (dynamic-ish).
On an MCU, **we need static allocation** — fixed max sizes.

The `.options` file tells nanopb the max sizes:

```
# student.options
Student.name         max_size:64
Student.student_id   max_size:16
Student.courses      max_count:10
Student.courses      max_size:32
```

Without this file → nanopb uses callback-based (heap-like) approach.

---

# student.proto + student.options

```protobuf
// student.proto
syntax = "proto3";
message Student {
  string student_id = 1;
  string name       = 2;
  int32  age        = 3;
  float  gpa        = 6;
}
```

```
# student.options
Student.student_id  max_size:16
Student.name        max_size:64
```

Simple, clean, MCU-friendly.

---

# Generating C Code

```bash
# Install nanopb generator plugin
pip install nanopb

# Generate C files from proto
protoc --nanopb_out=. student.proto
```

Output:
```
student.pb.h   ← struct definition + init macros
student.pb.c   ← field descriptor tables
```

Include both in your MCU project.

---

# Generated Files — What's Inside

**student.pb.h (simplified)**
```c
typedef struct _Student {
    char student_id[16];
    char name[64];
    int32_t age;
    float gpa;
} Student;

#define Student_init_zero  {"", "", 0, 0}
extern const pb_msgdesc_t Student_msg;
```

Plain C structs — no C++, no exceptions, no RTTI.

---

# pb_ostream_t and pb_istream_t

nanopb uses **stream abstractions** for encode/decode.

```c
// Output stream — writes INTO a buffer
pb_ostream_t out = pb_ostream_from_buffer(buffer, sizeof(buffer));

// Input stream — reads FROM a buffer
pb_istream_t in = pb_istream_from_buffer(buffer, bytes_written);
```

Streams can also wrap UART, SPI flash, or any byte sink/source.

---

# Encoding a Student

```c
uint8_t buffer[128];
Student student = Student_init_zero;

strncpy(student.student_id, "STU001", sizeof(student.student_id));
strncpy(student.name, "Alice", sizeof(student.name));
student.age = 20;
student.gpa = 3.8f;

pb_ostream_t stream = pb_ostream_from_buffer(buffer, sizeof(buffer));

if (!pb_encode(&stream, Student_fields, &student)) {
    printf("Encode failed: %s\n", PB_GET_ERROR(&stream));
}

size_t encoded_size = stream.bytes_written; // e.g., 22 bytes
```

---

# Decoding a Student

```c
Student decoded = Student_init_zero;

pb_istream_t stream = pb_istream_from_buffer(buffer, encoded_size);

if (!pb_decode(&stream, Student_fields, &decoded)) {
    printf("Decode failed: %s\n", PB_GET_ERROR(&stream));
    return;
}

printf("Name: %s\n", decoded.name);
printf("ID:   %s\n", decoded.student_id);
printf("Age:  %d\n", decoded.age);
printf("GPA:  %.1f\n", decoded.gpa);
```

---

# Full Round-Trip Demo

```
[Encode]
  Student { id="STU001", name="Alice", age=20, gpa=3.8 }
  → pb_encode()
  → buffer: 0A 06 53 54 55 30 30 31 12 05 41 6C 69 63 65 18 14 35 9A 99 73 40
  → 22 bytes (vs ~60 bytes as JSON)

[Transmit]
  UART / BLE / flash write → buffer bytes

[Decode]
  buffer → pb_decode()
  → Student { id="STU001", name="Alice", age=20, gpa=3.8 }
```

---

# Sending the Buffer Anywhere

```c
// UART (STM32 HAL)
HAL_UART_Transmit(&huart1, buffer, encoded_size, HAL_MAX_DELAY);

// Arduino Serial
Serial.write(buffer, encoded_size);

// Write to SPI Flash (pseudocode)
flash_write(address, buffer, encoded_size);

// BLE characteristic update (ESP-IDF)
esp_ble_gatts_set_attr_value(attr_handle, encoded_size, buffer);
```

The buffer is just bytes — send it anywhere.

---

# Memory Layout — No malloc

```c
// Everything is on the stack or in static memory
static uint8_t tx_buffer[256];   // static = survives across calls
static Student student;           // static = no stack pressure

// NOT needed:
// Student* s = malloc(sizeof(Student));  ← never in embedded nanopb
```

**Rule:** declare large buffers and structs as `static` or global to avoid stack overflow on MCUs with limited stack (often 1–4 KB).

---

# nanopb vs Alternatives

| Library | ROM | Heap | C Only | MCU-Ready |
|---|---|---|---|---|
| **nanopb** | ~5 KB | No | Yes | Yes |
| protobuf-c | ~300 KB | Yes | Yes | No |
| FlatBuffers | ~50 KB | No | C++ | Partial |
| MessagePack-C | ~10 KB | Optional | Yes | Yes |

nanopb is the clear winner for strict resource-constrained embedded.

---

# Summary & Tips

- nanopb = protobuf for embedded — tiny, static, pure C
- Always use a `.options` file for static allocation
- Zero-initialize structs: `Student s = Student_init_zero;`
- Check all `pb_encode` / `pb_decode` return values
- Declare large structs as `static` to avoid stack overflow
- Same `.proto` file works for both PC (Python/Go) and MCU (nanopb)

---

# What's Next

## Episode 6 — Schema Evolution & Best Practices

> What happens when you need to change your .proto after you've already deployed firmware and stored data?

- Safe vs unsafe schema changes
- The `reserved` keyword
- Backward and forward compatibility
- Embedded-specific concerns

**See you there!**

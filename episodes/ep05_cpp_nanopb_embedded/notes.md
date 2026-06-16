# Episode 5 — Protobuf in C with nanopb (Embedded Focus)

**Series:** Protobuf for Embedded & Mobile Developers  
**Channel:** The Debugger Diary  
**Prerequisites:** Episodes 1–4 (especially Ep3 — .proto syntax)

---

## Episode Overview

This episode covers using Protocol Buffers on resource-constrained microcontrollers using **nanopb** — a pure C implementation designed specifically for embedded systems. You will learn to encode a Student struct into a compact binary buffer and decode it back, using the same `.proto` file that works on desktop Python or server Go.

---

## Section 1: Why nanopb?

Full `protobuf-c` (the official C implementation) links in roughly **300 KB** of code and requires dynamic memory allocation (`malloc`/`free`). This is a problem for microcontrollers where:

- Total flash is often 64–512 KB
- RAM is 16–256 KB
- There is no heap (or using the heap is explicitly forbidden by safety guidelines like MISRA-C)

**nanopb** solves this by:

| Property | Full protobuf-c | nanopb |
|---|---|---|
| ROM footprint | ~300 KB | ~3–5 KB |
| RAM footprint | Dynamic | ~200–300 bytes |
| Dynamic allocation | Required | Optional (off by default) |
| C++ required | No | No |
| C standard | C99 | C99 |

**Supported hardware (non-exhaustive):**
- ESP32 / ESP8266
- STM32 (all families: F1, F4, H7, G0, etc.)
- Arduino Mega, Due, Zero, Nano 33
- Raspberry Pi Pico (RP2040)
- Nordic nRF52840 / nRF5340
- Microchip PIC32, SAM series
- Any platform with a C99 compiler and ~5 KB flash

---

## Section 2: Installation

### Option 1 — pip (recommended for code generation)

```bash
pip install nanopb
```

This installs the nanopb Python generator plugin for `protoc`. After this, `protoc --nanopb_out=.` works.

### Option 2 — Download release ZIP from GitHub

Download the nanopb release from the GitHub releases page. You only need these files in your MCU project:

```
nanopb/
  pb.h          ← core types and macros
  pb_encode.h
  pb_encode.c   ← encoding logic
  pb_decode.h
  pb_decode.c   ← decoding logic
  pb_common.h
  pb_common.c   ← shared utilities
```

Add `pb_encode.c`, `pb_decode.c`, and `pb_common.c` to your build system (Makefile, CMakeLists.txt, or Arduino sketch folder).

### CMakeLists.txt snippet (STM32/ESP-IDF style)

```cmake
set(NANOPB_DIR ${CMAKE_SOURCE_DIR}/third_party/nanopb)

target_sources(my_app PRIVATE
    ${NANOPB_DIR}/pb_encode.c
    ${NANOPB_DIR}/pb_decode.c
    ${NANOPB_DIR}/pb_common.c
    student.pb.c   # generated from student.proto
)

target_include_directories(my_app PRIVATE
    ${NANOPB_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}
)
```

---

## Section 3: .proto File for Embedded

When writing `.proto` files for MCU use, prefer:

- `int32`, `uint32`, `float` — fixed-size native types
- Short `string` fields (specify max length in `.options`)
- Avoid `map<>` (requires dynamic allocation in nanopb)
- Avoid `google.protobuf.Timestamp` unless your MCU has the full well-known types bundle

**demos/ep05_cpp/student.proto:**

```protobuf
syntax = "proto3";

package school;

enum Department {
  DEPARTMENT_UNKNOWN = 0;
  COMPUTER_SCIENCE = 1;
  ELECTRICAL_ENGINEERING = 2;
  MECHANICAL_ENGINEERING = 3;
  MATHEMATICS = 4;
}

message Student {
  string student_id = 1;          // max 16 chars — set in .options
  string name = 2;                // max 64 chars — set in .options
  int32 age = 3;
  Department department = 4;
  repeated string courses = 5;   // max 10 courses, max 32 chars each
  float gpa = 6;
  bool is_enrolled = 7;
}
```

---

## Section 4: The .options File

Without the `.options` file, nanopb generates callback-based (effectively dynamic) handling for strings and repeated fields. On a bare-metal MCU with no heap, this fails at runtime or requires a custom allocator.

The `.options` file lives next to your `.proto` file and has the **same base name**:

```
student.proto
student.options   ← same directory, same base name
```

**demos/ep05_cpp/student.options:**

```
# nanopb options — static size limits
Student.student_id   max_size:16
Student.name         max_size:64
Student.courses      max_count:10
Student.courses      max_size:32
```

| Directive | Meaning |
|---|---|
| `max_size:N` | Max bytes for a string field (including null terminator) |
| `max_count:N` | Max number of elements in a repeated field |

With this file in place, nanopb generates fixed-size arrays — no heap needed.

---

## Section 5: Generated Files

After running `protoc --nanopb_out=. student.proto`, you get:

**student.pb.h (simplified for readability):**

```c
#include <pb.h>

typedef enum {
    school_Department_DEPARTMENT_UNKNOWN = 0,
    school_Department_COMPUTER_SCIENCE   = 1,
    school_Department_ELECTRICAL_ENGINEERING = 2,
    school_Department_MECHANICAL_ENGINEERING = 3,
    school_Department_MATHEMATICS        = 4
} school_Department;

typedef struct _school_Student {
    char    student_id[16];
    char    name[64];
    int32_t age;
    school_Department department;
    pb_size_t courses_count;
    char    courses[10][32];
    float   gpa;
    bool    is_enrolled;
} school_Student;

/* Initializer macro — zero all fields */
#define school_Student_init_zero { "", "", 0, _school_Department_MIN, 0, {""}, 0, 0 }

/* Field descriptor table — used by pb_encode/pb_decode */
extern const pb_msgdesc_t school_Student_msg;
#define school_Student_fields &school_Student_msg
```

Key points:
- It's a plain C struct — no classes, no vtables
- `courses_count` tracks how many entries are actually filled
- `school_Student_init_zero` is the safe zero-initializer macro

---

## Section 6: Encoding

```c
#include "pb_encode.h"
#include "student.pb.h"
#include <string.h>
#include <stdio.h>

int main(void) {
    /* 1. Declare and zero-initialize the struct */
    school_Student student = school_Student_init_zero;

    /* 2. Populate fields */
    strncpy(student.student_id, "STU001", sizeof(student.student_id) - 1);
    strncpy(student.name, "Alice", sizeof(student.name) - 1);
    student.age = 20;
    student.department = school_Department_COMPUTER_SCIENCE;
    student.gpa = 3.8f;
    student.is_enrolled = true;

    /* Repeated field: set count + fill array */
    student.courses_count = 2;
    strncpy(student.courses[0], "Algorithms", sizeof(student.courses[0]) - 1);
    strncpy(student.courses[1], "OS Design",  sizeof(student.courses[1]) - 1);

    /* 3. Allocate a buffer */
    uint8_t buffer[256];
    memset(buffer, 0, sizeof(buffer));

    /* 4. Create output stream */
    pb_ostream_t stream = pb_ostream_from_buffer(buffer, sizeof(buffer));

    /* 5. Encode */
    bool status = pb_encode(&stream, school_Student_fields, &student);
    if (!status) {
        printf("Encode error: %s\n", PB_GET_ERROR(&stream));
        return 1;
    }

    size_t encoded_size = stream.bytes_written;
    printf("Encoded %zu bytes\n", encoded_size);

    /* 6. Print hex for inspection */
    for (size_t i = 0; i < encoded_size; i++) {
        printf("%02X ", buffer[i]);
    }
    printf("\n");

    return 0;
}
```

**`stream.bytes_written`** gives the exact number of valid bytes in the buffer. Only send/store these bytes — not the entire buffer.

---

## Section 7: Decoding

```c
#include "pb_decode.h"
#include "student.pb.h"
#include <stdio.h>

void decode_student(const uint8_t *buffer, size_t length) {
    /* 1. Zero-initialize the destination struct */
    school_Student decoded = school_Student_init_zero;

    /* 2. Create input stream */
    pb_istream_t stream = pb_istream_from_buffer(buffer, length);

    /* 3. Decode */
    bool status = pb_decode(&stream, school_Student_fields, &decoded);
    if (!status) {
        printf("Decode error: %s\n", PB_GET_ERROR(&stream));
        return;
    }

    /* 4. Access fields */
    printf("Student ID:  %s\n",  decoded.student_id);
    printf("Name:        %s\n",  decoded.name);
    printf("Age:         %d\n",  decoded.age);
    printf("GPA:         %.1f\n", decoded.gpa);
    printf("Enrolled:    %s\n",  decoded.is_enrolled ? "Yes" : "No");
    printf("Courses (%d):\n", decoded.courses_count);
    for (int i = 0; i < decoded.courses_count; i++) {
        printf("  - %s\n", decoded.courses[i]);
    }
}
```

**Always zero-initialize** the destination struct before calling `pb_decode`. Uninitialized memory can cause undefined behavior if a field is missing from the stream.

---

## Section 8: Sending the Buffer Anywhere

The encoded `buffer` is just a byte array. You can pass it to any transport:

```c
/* STM32 HAL UART */
HAL_UART_Transmit(&huart1, buffer, (uint16_t)encoded_size, HAL_MAX_DELAY);

/* Arduino Serial */
Serial.write(buffer, encoded_size);

/* ESP-IDF BLE GATT characteristic update */
esp_ble_gatts_set_attr_value(char_handle, (uint16_t)encoded_size, buffer);

/* Write to SPI NOR flash at a known address */
flash_write(STUDENT_RECORD_ADDR, buffer, encoded_size);

/* Send over MQTT as binary payload */
esp_mqtt_client_publish(client, "/students/stu001", 
                        (const char*)buffer, (int)encoded_size, 1, 0);
```

The same encoded bytes are readable by a Python, Go, or Java protobuf library on the receiving end — because they all implement the same wire format.

---

## Section 9: Error Handling

Always check the return value of `pb_encode` and `pb_decode`:

```c
if (!pb_encode(&ostream, Student_fields, &student)) {
    const char *err = PB_GET_ERROR(&ostream);
    /* Log the error, send an error code, halt, etc. */
    handle_error(err);
}

if (!pb_decode(&istream, Student_fields, &student)) {
    const char *err = PB_GET_ERROR(&istream);
    handle_error(err);
}
```

**Common encode errors:**
- Buffer too small → increase buffer size or use `pb_get_encoded_size()` first
- String exceeds `max_size` from `.options`

**Common decode errors:**
- Truncated buffer (wrong length passed to `pb_istream_from_buffer`)
- Wire type mismatch (corrupt data or wrong proto version)

---

## Section 10: Memory Tips for Embedded

```c
/* Put large buffers in static storage — NOT on the stack */
static uint8_t tx_buffer[256];   /* Stack on MCUs is often only 1–4 KB */
static school_Student student;

/* Always use the init macro before use */
school_Student student = school_Student_init_zero;

/* Check your buffer size against worst case */
/* pb_get_encoded_size() gives you the exact size before encoding */
size_t required_size;
pb_get_encoded_size(&required_size, school_Student_fields, &student);
if (required_size > sizeof(tx_buffer)) {
    /* Buffer too small — handle gracefully */
}
```

**Rules of thumb:**
1. Large structs and buffers → `static` or global scope
2. Always `_init_zero` before populate
3. Only transmit `stream.bytes_written` bytes, not the whole buffer
4. Test on-target with the smallest RAM configuration you support

---

## Key Takeaways

- nanopb is the right choice for any MCU with < 256 KB flash
- The `.options` file is mandatory for static allocation (no heap)
- `pb_encode` writes into a buffer; `pb_decode` reads from a buffer
- Always zero-initialize structs with `_init_zero`
- The same `.proto` file works across C (nanopb), Python, Go, Java, etc.
- The encoded buffer is transport-agnostic — UART, BLE, flash, MQTT

---

## Comparison: Libraries for Embedded Binary Serialization

| Library | ROM | Heap-free | C only | Proto3 compat | Ecosystem |
|---|---|---|---|---|---|
| **nanopb** | ~5 KB | Yes | Yes | Yes | Large |
| protobuf-c | ~300 KB | No | Yes | Yes | Large |
| FlatBuffers | ~50 KB | Yes | C++ (C wrapper) | No | Medium |
| MessagePack-C | ~10 KB | Optional | Yes | No | Small |
| CBOR (libcbor) | ~20 KB | Optional | Yes | No | Small |

---

## Further Reading

- nanopb official documentation and generator reference
- nanopb GitHub examples (especially the `network_server` example)
- ESP-IDF protobuf component (wraps nanopb)
- STM32 protobuf application note (ST Community)
- "Serialization in Embedded Systems" — embedded.com articles

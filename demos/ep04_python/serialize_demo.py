"""
Episode 4 Demo — Serialize & Deserialize in Python
Series: Protobuf for Embedded & Mobile Developers
Channel: The Debugger Diary

This script:
  1. Creates 5 Employee objects with realistic data
  2. Wraps them in an EmployeeList message
  3. Serializes to binary and writes to employees.bin
  4. Prints size comparison: protobuf vs JSON

Run first, then run deserialize_demo.py to read the data back.

Prerequisites:
  pip install protobuf
  protoc --python_out=. employee.proto
"""

import sys
import json

# -------------------------------------------------------------------
# Import the generated protobuf classes.
# If this fails, run: protoc --python_out=. employee.proto
# -------------------------------------------------------------------
try:
    from employee_pb2 import Employee, EmployeeList, Department
except ModuleNotFoundError:
    print("ERROR: employee_pb2.py not found.")
    print("Generate it by running:")
    print("  protoc --python_out=. employee.proto")
    sys.exit(1)

from google.protobuf.json_format import MessageToJson


def create_employees():
    """Build a list of sample Employee messages."""

    # Each tuple: (id, name, age, department, salary, is_active, email, skills)
    sample_data = [
        (
            "EMP001", "Alice Johnson", 28,
            Department.ENGINEERING, 95000.0, True,
            "alice@company.com",
            ["Python", "Go", "Kubernetes", "Docker"],
        ),
        (
            "EMP002", "Bob Smith", 35,
            Department.MARKETING, 72000.0, True,
            "bob@company.com",
            ["SEO", "Google Ads", "Content Strategy"],
        ),
        (
            "EMP003", "Charlie Davis", 42,
            Department.HR, 68000.0, False,
            "charlie@company.com",
            ["Recruitment", "HRIS", "Conflict Resolution"],
        ),
        (
            "EMP004", "Diana Patel", 30,
            Department.ENGINEERING, 105000.0, True,
            "diana@company.com",
            ["C++", "Embedded Linux", "RTOS", "CAN Bus"],
        ),
        (
            "EMP005", "Eve Chen", 26,
            Department.FINANCE, 80000.0, True,
            "eve@company.com",
            ["Excel", "Power BI", "SQL", "Python"],
        ),
    ]

    employees = []
    for emp_id, name, age, dept, salary, active, email, skills in sample_data:
        emp = Employee(
            employee_id=emp_id,
            name=name,
            age=age,
            department=dept,
            salary=salary,
            is_active=active,
            email=email,
        )
        emp.skills.extend(skills)
        employees.append(emp)

    return employees


def main():
    # 1. Create employee objects
    employees = create_employees()

    # 2. Wrap in an EmployeeList message
    emp_list = EmployeeList()
    emp_list.employees.extend(employees)
    emp_list.total_count = len(employees)

    # 3. Serialize to binary bytes
    binary_data = emp_list.SerializeToString()

    # 4. Write to file in BINARY mode ("wb" — NOT "w")
    output_file = "employees.bin"
    with open(output_file, "wb") as f:
        f.write(binary_data)

    print(f"Saved {emp_list.total_count} employees to '{output_file}'")

    # -------------------------------------------------------------------
    # Size comparison: protobuf binary vs equivalent JSON
    # -------------------------------------------------------------------
    protobuf_size = len(binary_data)

    # Build equivalent JSON manually for fair comparison
    json_data = MessageToJson(emp_list, including_default_value_fields=True)
    json_size = len(json_data.encode("utf-8"))

    print(f"\n--- Size Comparison ---")
    print(f"Protobuf binary : {protobuf_size:>6} bytes")
    print(f"JSON equivalent : {json_size:>6} bytes")
    print(f"Protobuf is {json_size / protobuf_size:.1f}x smaller than JSON")

    # -------------------------------------------------------------------
    # Show hex dump of the first 40 bytes (educational)
    # -------------------------------------------------------------------
    print(f"\n--- First 40 bytes (hex) ---")
    hex_str = binary_data[:40].hex(" ")
    print(hex_str)
    print("(field tags, lengths, and UTF-8 encoded strings)")

    print(f"\nRun deserialize_demo.py to read the data back.")


if __name__ == "__main__":
    main()

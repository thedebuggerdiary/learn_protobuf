"""
Episode 4 Demo — Deserialize from Binary File
Series: Protobuf for Embedded & Mobile Developers
Channel: The Debugger Diary

This script:
  1. Reads employees.bin (written by serialize_demo.py)
  2. Parses the binary data back into an EmployeeList message
  3. Prints every employee's details in a readable format

Run serialize_demo.py first to generate employees.bin.

Prerequisites:
  pip install protobuf
  protoc --python_out=. employee.proto
"""

import sys

try:
    from employee_pb2 import Employee, EmployeeList, Department
except ModuleNotFoundError:
    print("ERROR: employee_pb2.py not found.")
    print("Generate it by running:")
    print("  protoc --python_out=. employee.proto")
    sys.exit(1)


def department_name(dept_value):
    """Convert a Department enum integer to its string name."""
    return Department.Name(dept_value)


def print_employee(index, emp):
    """Print a single employee record in a formatted layout."""
    active_str = "Yes" if emp.is_active else "No"
    dept_str   = department_name(emp.department)
    skills_str = ", ".join(emp.skills) if emp.skills else "(none)"

    print(f"Employee #{index}")
    print(f"  ID         : {emp.employee_id}")
    print(f"  Name       : {emp.name}")
    print(f"  Age        : {emp.age}")
    print(f"  Department : {dept_str}")
    print(f"  Salary     : ${emp.salary:,.2f}")
    print(f"  Active     : {active_str}")
    print(f"  Email      : {emp.email}")
    print(f"  Skills     : {skills_str}")


def main():
    input_file = "employees.bin"

    # -------------------------------------------------------------------
    # Read raw bytes from file — MUST use "rb" (binary read mode)
    # -------------------------------------------------------------------
    try:
        with open(input_file, "rb") as f:
            raw_bytes = f.read()
    except FileNotFoundError:
        print(f"ERROR: '{input_file}' not found.")
        print("Run serialize_demo.py first to generate the binary file.")
        sys.exit(1)

    print(f"Read {len(raw_bytes)} bytes from '{input_file}'")

    # -------------------------------------------------------------------
    # Deserialize: parse raw bytes back into an EmployeeList message
    # -------------------------------------------------------------------
    emp_list = EmployeeList()
    emp_list.ParseFromString(raw_bytes)

    print(f"Parsed {emp_list.total_count} employee(s)\n")
    print("=" * 45)

    # -------------------------------------------------------------------
    # Iterate and display each employee
    # -------------------------------------------------------------------
    for i, emp in enumerate(emp_list.employees, start=1):
        print_employee(i, emp)
        if i < emp_list.total_count:
            print("-" * 45)

    print("=" * 45)
    print(f"\nDone. Total employees: {emp_list.total_count}")


if __name__ == "__main__":
    main()

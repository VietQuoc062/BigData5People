#!/usr/bin/env python3
import sys
import csv
import re
import io  # Để handle stdin như file

# Top 8 vị trí IT phổ biến
TOP_POSITIONS = [
    "Backend Developer", "Fullstack Developer", "Frontend Developer",
    "DevOps Engineer", "Business Analyst", "Mobile Application Developer",
    "Project Manager", "Automation Tester"
]

# Đọc từ stdin như CSV file
input_data = sys.stdin.read()
reader = csv.reader(io.StringIO(input_data))

for row in reader:
    line = ','.join(row)  # Reconstruct line nếu cần, nhưng reader đã parse
    if not row or len(row) == 0 or row[0].startswith('Job name'):  # Skip header
        continue

    if len(row) < 19:  # Đảm bảo đủ cột (Average Lương ở index 18)
        continue

    job_name = row[0].strip().strip('"')  # Job name, remove quotes
    avg_salary_str = row[18].strip()  # Average Lương

    try:
        avg_salary = float(avg_salary_str) if avg_salary_str else 0
    except ValueError:
        continue  # Skip nếu không parse được lương

    if avg_salary == 0:
        continue

    # Extract/group vị trí bằng regex
    position = "Other"
    for pos in TOP_POSITIONS:
        if re.search(rf'\b{re.escape(pos)}\b', job_name, re.IGNORECASE):
            position = pos
            break

    # Emit: position\tavg_salary
    print(f"{position}\t{avg_salary}")
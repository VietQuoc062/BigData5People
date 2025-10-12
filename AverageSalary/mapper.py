#!/usr/bin/env python3
import sys
import csv
import re

# Top 8 vị trí IT phổ biến
TOP_POSITIONS = [
    "Backend Developer", "Fullstack Developer", "Frontend Developer",
    "DevOps Engineer", "Business Analyst", "Mobile Application Developer",
    "Project Manager", "Automation Tester"
]

# Đọc CSV từ stdin
reader = csv.reader(sys.stdin, delimiter=',')

header_skipped = False
for row in reader:
    if not header_skipped:
        header_skipped = True
        continue

    try:
        # Đảm bảo có đủ cột (Average Salary ở index 18)
        if len(row) < 19:
            continue

        job_name = row[0].strip().strip('"')
        avg_salary_str = row[18].strip()

        # Bỏ qua nếu không có lương
        if not avg_salary_str:
            continue

        # Chuyển lương thành số (float)
        try:
            avg_salary = float(avg_salary_str)
        except ValueError:
            continue

        if avg_salary == 0:
            continue

        # Xác định vị trí IT trong top 8
        position = "Other"
        for pos in TOP_POSITIONS:
            if re.search(rf'\b{re.escape(pos)}\b', job_name, re.IGNORECASE):
                position = pos
                break

        # Xuất kết quả: position\tavg_salary
        print(f"{position}\t{avg_salary}")

    except Exception:
        continue

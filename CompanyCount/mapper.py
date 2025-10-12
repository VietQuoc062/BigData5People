#!/usr/bin/env python3
import sys
import csv

# Đọc dữ liệu từ stdin
reader = csv.reader(sys.stdin, delimiter=',')

header_skipped = False
for row in reader:
    if not header_skipped:
        header_skipped = True
        continue

    try:
        # Cột "Company name" là cột thứ 2 trong dữ liệu (bắt đầu từ 0)
        company_name = row[1].strip()

        if not company_name:
            continue

        # Phát ra (company_name, 1) để đếm số lượng công việc của từng công ty
        print(f"{company_name}\t1")

    except Exception as e:
        continue

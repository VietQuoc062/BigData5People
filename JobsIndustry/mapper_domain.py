#!/usr/bin/env python3
import sys
import csv

# Đọc từ stdin
reader = csv.reader(sys.stdin, delimiter=',')

header_skipped = False
for row in reader:
    if not header_skipped:
        header_skipped = True
        continue

    try:
        # Cột Job Domain là cột thứ 6 trong CSV (bắt đầu từ 0)
        domain_col = row[6].strip()

        if not domain_col:
            continue

        # Tách các domain (ví dụ: "IT Services and IT Consulting, E-commerce")
        domains = [domain.strip() for domain in domain_col.split(',') if domain.strip()]

        for domain in domains:
            print(f"{domain}\t1")

    except Exception:
        continue
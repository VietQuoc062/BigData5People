#!/usr/bin/env python3
import sys
import csv

# Đọc từ stdin (dữ liệu từ HDFS)
for line in sys.stdin:
    try:
        row = next(csv.reader([line.strip()]))  # Đọc dòng CSV
        if len(row) < 5:
            continue
        skills_str = row[4]  # Cột Skills ở index 4
        if skills_str and skills_str.strip():
            skills = [s.strip().lower() for s in skills_str.split(',') if s.strip()]
            for skill in skills:
                skill = ' '.join(skill.split())  # Normalize multiple spaces thành single
                # Emit: skill\t1 (tab-separated)
                print(f"{skill}\t1")
    except csv.Error:
        continue
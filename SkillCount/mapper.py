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
        # Cột Skills là cột thứ 5 trong dữ liệu của bạn (bắt đầu từ 0)
        skills_col = row[4].strip()

        if not skills_col:
            continue

        # Tách các kỹ năng trong cột Skills (có thể có nhiều kỹ năng cách nhau bằng dấu phẩy)
        skills = [skill.strip() for skill in skills_col.split(',') if skill.strip()]

        # Phát ra (kỹ năng, 1) cho mỗi kỹ năng
        for skill in skills:
            print(f"{skill}\t1")

    except Exception:
        continue
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
        # Cột Level là cột thứ 8 trong ví dụ của bạn (bắt đầu từ 0)
        level_col = row[8].strip()

        if not level_col:
            continue

        # Tách các cấp độ (ví dụ: "Junior, Middle" -> ["Junior", "Middle"])
        levels = [lvl.strip() for lvl in level_col.split(',') if lvl.strip()]

        for lvl in levels:
            print(f"{lvl}\t1")

    except Exception:
        continue

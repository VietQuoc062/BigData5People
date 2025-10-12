#!/usr/bin/env python3
import sys

current_position = None
total_salary = 0.0
count = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    position, salary_str = line.split('\t')
    salary = float(salary_str)

    if position == current_position:
        total_salary += salary
        count += 1
    else:
        # Output cho key trước
        if current_position and count > 0:
            avg = total_salary / count
            print(f"{current_position}\t{count}\t{avg:.0f}")  # Làm tròn VND        current_position = position
        total_salary = salary
        count = 1

# Output dòng cuối
if current_position and count > 0:
    avg = total_salary / count
    print(f"{current_position}\t{count}\t{avg:.0f}")
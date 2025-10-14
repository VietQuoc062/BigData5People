#!/usr/bin/env python3
import sys
import math

current_expertise = None
sum_salary = 0.0
sum_salary_sq = 0.0
count = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    parts = line.split("\t")
    if len(parts) != 4:
        continue

    expertise, salary, salary_sq, cnt = parts
    salary = float(salary)
    salary_sq = float(salary_sq)
    cnt = int(cnt)

    if current_expertise == expertise:
        sum_salary += salary
        sum_salary_sq += salary_sq
        count += cnt
    else:
        if current_expertise and count > 1:
            mean = sum_salary / count
            variance = (sum_salary_sq / count) - (mean ** 2)
            stddev = math.sqrt(variance) if variance >= 0 else 0
            print(f"{current_expertise}\t{count}\t{variance:,.2f}\t{stddev:,.2f}")

        current_expertise = expertise
        sum_salary = salary
        sum_salary_sq = salary_sq
        count = cnt

# In dòng cuối cùng
if current_expertise and count > 1:
    mean = sum_salary / count
    variance = (sum_salary_sq / count) - (mean ** 2)
    stddev = math.sqrt(variance) if variance >= 0 else 0
    print(f"{current_expertise}\t{count}\t{variance:,.2f}\t{stddev:,.2f}")

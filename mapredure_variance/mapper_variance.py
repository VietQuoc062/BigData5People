#!/usr/bin/env python3
import sys
import csv

# Đọc CSV từ stdin
reader = csv.reader(sys.stdin)
header = next(reader, None)  # Bỏ qua dòng header nếu có

for row in reader:
    if row[5] is None or row[18] is None:
        continue  # Bỏ qua dòng không đủ cột

    job_expertise = row[5].strip()
    avg_salary_str = row[18].strip()  # cột thứ 18 (index 17)

    if not job_expertise or not avg_salary_str:
        continue  # Bỏ qua dòng rỗng

    # Loại bỏ ký tự phân cách hàng nghìn và khoảng trắng
    avg_salary_str = avg_salary_str.replace(",", "").replace(" ", "")

    try:
        avg_salary = float(avg_salary_str)
        print(f"{job_expertise}\t{avg_salary}\t{avg_salary**2}\t1")
    except ValueError:
        continue  # Bỏ qua dòng không hợp lệ

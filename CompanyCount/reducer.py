#!/usr/bin/env python3
import sys

current_company = None
current_count = 0

# Đọc từng dòng đầu vào từ stdin
for line in sys.stdin:
    line = line.strip()
    
    if not line:
        continue

    company, count = line.split('\t', 1)

    try:
        count = int(count)
    except ValueError:
        continue

    # Nếu công ty giống nhau, cộng dồn số lượng công việc
    if current_company == company:
        current_count += count
    else:
        # In ra kết quả cho công ty trước đó
        if current_company:
            print(f"{current_company}\t{current_count}")
        current_company = company
        current_count = count

# In dòng cuối cùng nếu còn công ty
if current_company:
    print(f"{current_company}\t{current_count}")

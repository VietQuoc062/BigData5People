#!/usr/bin/env python3
import sys

current_skill = None
current_count = 0

for line in sys.stdin:
    line = line.strip()
    
    if not line:
        continue

    # Tách key (kỹ năng) và value (số lượng công việc yêu cầu)
    skill, count = line.split('\t', 1)

    try:
        count = int(count)
    except ValueError:
        continue

    # Nếu kỹ năng giống nhau, cộng dồn số lượng
    if current_skill == skill:
        current_count += count
    else:
        # In ra kết quả cho kỹ năng trước đó
        if current_skill:
            print(f"{current_skill}\t{current_count}")
        current_skill = skill
        current_count = count

# In dòng cuối cùng nếu còn kỹ năng
if current_skill:
    print(f"{current_skill}\t{current_count}")
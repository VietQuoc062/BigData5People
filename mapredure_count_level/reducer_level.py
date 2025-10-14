#!/usr/bin/env python3
import sys

current_level = None
current_count = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    level, count = line.split('\t', 1)
    try:
        count = int(count)
    except:
        continue

    if current_level == level:
        current_count += count
    else:
        if current_level:
            print(f"{current_level}\t{current_count}")
        current_level = level
        current_count = count

# In dòng cuối cùng
if current_level:
    print(f"{current_level}\t{current_count}")

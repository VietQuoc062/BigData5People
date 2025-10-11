#!/usr/bin/env python3
import sys
from collections import defaultdict

current_skill = None
current_count = 0
skill = None

# Đọc từ stdin (output từ mapper)
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        skill, count = line.split('\t', 1)
        count = int(count)
    except ValueError:
        continue

    if current_skill == skill:
        current_count += count
    else:
        if current_skill:
            # Emit: skill\tcount
            print(f"{current_skill}\t{current_count}")
        current_skill = skill
        current_count = count

# Emit dòng cuối
if current_skill == skill:
    print(f"{current_skill}\t{current_count}")
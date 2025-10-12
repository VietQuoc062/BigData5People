#!/usr/bin/env python3
import sys

current_domain = None
current_count = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    domain, count = line.split('\t', 1)
    try:
        count = int(count)
    except:
        continue

    if current_domain == domain:
        current_count += count
    else:
        if current_domain:
            print(f"{current_domain}\t{current_count}")
        current_domain = domain
        current_count = count

# In dòng cuối cùng
if current_domain:
    print(f"{current_domain}\t{current_count}")
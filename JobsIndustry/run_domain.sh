#!/bin/bash

# Script chạy MapReduce job: Phân tích số lượng công việc theo lĩnh vực ngành nghề (Job Domain) từ final.csv
# Chạy từ thư mục chứa mapper_domain.py và reducer_domain.py

# Tạo timestamp cho output (tránh trùng)
TIMESTAMP=$(date +%s)
INPUT_PATH="/input/final_cleaned.csv"
OUTPUT_PATH="/output/domain_count_${TIMESTAMP}"

echo "Bắt đầu chạy MapReduce job cho Job Domain..."
echo "Input: ${INPUT_PATH}"
echo "Output: ${OUTPUT_PATH}"

# Xóa output cũ
hdfs dfs -rm -r /output/domain_count_*

# Xóa file local cũ (nếu có)
echo "Xóa file local cũ (nếu tồn tại)..."
rm -f ~/domain_count_*.txt

# Kiểm tra input tồn tại
hdfs dfs -test -e ${INPUT_PATH}
if [ $? -ne 0 ]; then
    echo "Lỗi: File input ${INPUT_PATH} không tồn tại trên HDFS!"
    exit 1
fi

# Chạy job Hadoop Streaming
HADOOP_STREAMING_JAR="$HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-3.3.6.jar" # Hoặc phiên bản khác

hadoop jar $HADOOP_STREAMING_JAR \
    -files mapper_domain.py,reducer_domain.py \
    -mapper 'python3 mapper_domain.py' \
    -reducer 'python3 reducer_domain.py' \
    -input ${INPUT_PATH} \
    -output ${OUTPUT_PATH}

# Tải output về local
hdfs dfs -get ${OUTPUT_PATH}/part-00000 ~/domain_count_${TIMESTAMP}.txt

# Kiểm tra kết quả
if [ $? -eq 0 ]; then
    echo "Job thành công! Tải output về local:"
    echo "Xem top lĩnh vực ngành nghề có số lượng công việc cao nhất (sắp xếp giảm dần theo count):"
    sed 's/[[:space:]]*$//' ~/domain_count_${TIMESTAMP}.txt | sort -t $'\t' -k2 -n -r | head -10 | column -t -s $'\t'
else
    echo "Job thất bại! Kiểm tra log: yarn logs -applicationId <app_id> (từ console khi chạy)"
fi
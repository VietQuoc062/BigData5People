#!/bin/bash

# Script chạy MapReduce job: Phân tích tần suất kỹ năng từ final.csv
# Chạy từ thư mục chứa mapper.py và reducer.py


# Tạo timestamp cho output (tránh trùng)
TIMESTAMP=$(date +%s)
INPUT_PATH="/input/final.csv"
OUTPUT_PATH="/output/skills_frequency_${TIMESTAMP}"

echo "Bắt đầu chạy MapReduce job..."
echo "Input: ${INPUT_PATH}"
echo "Output: ${OUTPUT_PATH}"

# Xóa output cũ
hdfs dfs -rm -r /output/skills_frequency_*
# Xóa file local cũ (nếu có)
echo "Xóa file local cũ (nếu tồn tại)..."
rm -f ~/output_skills_*.txt

# Kiểm tra input tồn tại
hdfs dfs -test -e ${INPUT_PATH}
if [ $? -ne 0 ]; then
    echo "Lỗi: File input ${INPUT_PATH} không tồn tại trên HDFS!"
    exit 1
fi

# Chạy job Hadoop Streaming
HADOOP_STREAMING_JAR="$HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-3.3.6.jar" # Hoặc phiên bản khác

hadoop jar $HADOOP_STREAMING_JAR \
    -files mapper.py,reducer.py \
    -mapper 'python3 mapper.py' \
    -reducer 'python3 reducer.py' \
    -input ${INPUT_PATH} \
    -output ${OUTPUT_PATH}

# Kiểm tra kết quả
if [ $? -eq 0 ]; then
    echo "Job thành công! Tải output về local:"
    hdfs dfs -get ${OUTPUT_PATH}/part-00000 ~/output_skills_${TIMESTAMP}.txt
    echo "Xem top 10 kỹ năng phổ biến (sắp xếp giảm dần theo count):"
    sed 's/[[:space:]]*$//' ~/output_skills_${TIMESTAMP}.txt | sort -t $'\t' -k2 -n -r | head -10 | column -t -s $'\t'
else
    echo "Job thất bại! Kiểm tra log: yarn logs -applicationId <app_id> (từ console khi chạy)"
fi
#!/bin/bash

# Script chạy MapReduce job: Tính lương trung bình theo top vị trí IT từ jobs.csv
# Chạy từ thư mục chứa mapper.py và reducer.py


# Tạo timestamp cho output (tránh trùng)
TIMESTAMP=$(date +%s)
INPUT_PATH="/input/final_cleaned.csv"
OUTPUT_PATH="/output/avg_salary_${TIMESTAMP}"

echo "Bắt đầu chạy MapReduce job..."
echo "Input: ${INPUT_PATH}"
echo "Output: ${OUTPUT_PATH}"

# Xóa output cũ
hdfs dfs -rm -r /output/avg_salary_*

# Xóa file local cũ (nếu có)
echo "Xóa file local cũ (nếu tồn tại)..."
rm -f ~/output_salary_*.txt

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

# Tải output về local
hdfs dfs -get ${OUTPUT_PATH}/part-00000 ~/output_salary_${TIMESTAMP}.txt

# Kiểm tra kết quả
if [ $? -eq 0 ]; then
    echo "Job thành công! Tải output về local:"
    echo "Xem top vị trí có lương trung bình cao nhất (sắp xếp giảm dần theo avg salary):"
    sed 's/[[:space:]]*$//' ~/output_salary_${TIMESTAMP}.txt | sort -t $'\t' -k2 -n -r | head -10 | column -t -s $'\t'
else
    echo "Job thất bại! Kiểm tra log: yarn logs -applicationId <app_id> (từ console khi chạy)"
fi
# Xóa output cũ
hdfs dfs -rm -r /output/company_job_count

# Chạy job Hadoop Streaming
hadoop jar /home/hdoop/hadoop-streaming-3.3.6.jar \
-file /home/hdoop/mapred_son/mapper_company.py \
-file /home/hdoop/mapred_son/reducer_company.py \
-mapper 'python3 /home/hdoop/mapred_son/mapper_company.py' \
-reducer 'python3 /home/hdoop/mapred_son/reducer_company.py' \
-input /input/final_cleaned.csv \
-output /output/company_job_count

# Hiển thị kết quả
hdfs dfs -cat /output/company_job_count/part-00000
# Xóa output cũ
hdfs dfs -rm -r /output/skill_count_py

# Chạy job Hadoop Streaming
hadoop jar /home/hdoop/hadoop-streaming-3.3.6.jar \
-file /home/hdoop/mapred_son/mapper_skills.py \
-file /home/hdoop/mapred_son/reducer_skills.py \
-mapper 'python3 /home/hdoop/mapred_son/mapper_skills.py' \
-reducer 'python3 /home/hdoop/mapred_son/reducer_skills.py' \
-input /input/final_cleaned.csv \
-output /output/skill_count_py

# Hiển thị kết quả
hdfs dfs -cat /output/skill_count_py/part-00000
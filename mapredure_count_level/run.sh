#!/bin/bash

hdfs dfs -rm -r /user/hdoop/output_jobs_level

# Run MapReduce variance calculation
hadoop jar ~/hadoop-streaming-3.4.0.jar \
  -input /user/hdoop/input/final_cleaned.csv \
  -output /user/hdoop/output_jobs_level \
  -mapper "python3 mapper_level.py" \
  -reducer "python3 reducer_level.py" \
  -file mapper_level.py \
  -file reducer_level.py

# Display results
hdfs dfs -cat /user/hdoop/output_jobs_level/part-00000
#!/bin/bash

hdfs dfs -rm -r /user/hdoop/output_variance

# Run MapReduce variance calculation
hadoop jar ~/hadoop-streaming-3.4.0.jar \
  -input /user/hdoop/input/final_cleaned.csv \
  -output /user/hdoop/output_variance \
  -mapper "python3 mapper_variance.py" \
  -reducer "python3 reducer_variance.py" \
  -file mapper_variance.py \
  -file reducer_variance.py

# Display results
hdfs dfs -cat /user/hdoop/output_variance/part-00000
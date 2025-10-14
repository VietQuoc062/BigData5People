from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim, lower, count

# --- 1. Khởi tạo Spark ---
spark = SparkSession.builder.appName("WorkDaysStatistics").getOrCreate()

# --- 2. Đường dẫn HDFS ---
input_path = "hdfs://localhost:9000/input/final_cleaned.csv"
output_path = "hdfs://localhost:9000/output/workdays_stats"

# --- 3. Đọc CSV với delimiter đúng ---
df = (
    spark.read
    .option("header", True)
    .option("delimiter", ",")  # đúng với dữ liệu bạn gửi
    .option("inferSchema", True)
    .csv(input_path)
)

# --- 4. Kiểm tra tên cột ---
print("Tên cột trong DataFrame:", df.columns)

# --- 5. Chọn cột "Work days" ---
workdays_col = "Work days"
if workdays_col not in df.columns:
    raise ValueError(f"Không tìm thấy cột '{workdays_col}' trong DataFrame")

# --- 6. Thống kê số lượng công việc theo Work days ---
workdays_stats = (
    df.withColumn("workdays_type", trim(lower(col(workdays_col))))
      .filter(col("workdays_type").isNotNull() & (col("workdays_type") != ""))
      .groupBy("workdays_type")
      .agg(count("*").alias("total_jobs"))
      .orderBy(col("total_jobs").desc())
)

# --- 7. In kết quả ra console ---
print("=== Thống kê số lượng công việc theo Work days ===")
workdays_stats.show(truncate=False)

# --- 8. Ghi ra HDFS (1 file CSV duy nhất) ---
workdays_stats.coalesce(1).write.mode("overwrite").option("header", True).csv(output_path)
print(f"✅ Đã ghi kết quả ra HDFS tại: {output_path}")

# --- 9. Dừng Spark ---
spark.stop()

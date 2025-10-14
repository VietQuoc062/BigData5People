#!/usr/bin/env python3
from pyspark.sql import SparkSession
import pyspark.sql.functions as F

def main():
    spark = SparkSession.builder \
        .appName("RegionalSalaryAnalysis_Normalized") \
        .getOrCreate()

    hdfs_input_path = "hdfs:///maptospark/input/final_cleaned.csv"
    hdfs_output_path = "hdfs:///maptospark/Job2new"

    try:
        df = spark.read.option("header", "true").option("inferSchema", "true").csv(hdfs_input_path)

        # Lấy phần cuối của Address làm Region
        df_final = (
            df.withColumn(
                "Region",
                F.trim(F.element_at(F.split(F.col("Address"), ","), -1))
            )
            .withColumnRenamed("Average Lương", "avg_salary")
            .filter(
                F.col("avg_salary").isNotNull() &
                (F.col("avg_salary") > 0) &
                F.col("Region").isNotNull() &
                (F.col("Region") != "")
            )
        )

        # Chuẩn hóa tên thành phố + gom nhóm Remote/Overseas
        df_final = df_final.withColumn(
            "Khu Vực",
            F.when(F.col("Region").isin("Ho Chi Minh", "Hồ Chí Minh"), "TP. Hồ Chí Minh")
             .when(F.col("Region").isin("Ha Noi", "Hà Nội"), "Hà Nội")
             .when(F.col("Region").isin("Da Nang", "Đà Nẵng"), "Đà Nẵng")
             .when(F.col("Region").isin("Thành Phố Huế", "Hue"), "Huế")
             .when(F.col("Region").isin("Overseas", "Remote"), "Other")
             .otherwise(F.col("Region"))
        )

        # Tính toán: số lượng tin và lương trung bình (triệu VND)
        result_df = (
            df_final.groupBy("Khu Vực")
            .agg(
                F.count("avg_salary").alias("Số lượng tin tuyển"),
                F.concat(
                    F.round(F.avg("avg_salary") / 1_000_000, 1).cast("string"),
                    F.lit(" triệu VND")
                ).alias("Lương trung bình")
            )
            .orderBy(F.col("Số lượng tin tuyển").desc())
        )

        # Xuất kết quả
        result_df.coalesce(1).write.mode("overwrite").option("header", "true").csv(hdfs_output_path)

        print("✅ Hoàn tất!")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

    finally:
        spark.stop()

if __name__ == "__main__":
    main()

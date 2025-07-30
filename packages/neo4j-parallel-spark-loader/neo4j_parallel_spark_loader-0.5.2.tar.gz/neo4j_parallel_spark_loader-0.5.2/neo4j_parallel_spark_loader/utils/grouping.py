from typing import Dict

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, concat, lit


def create_value_groupings(
    value_counts_spark_dataframe: DataFrame,
    num_groups: int,
    grouping_column: str,
):
    """
    Create a Spark DataFrame containing groupings according to property value counts.

    Parameters
    ----------
    value_counts_spark_dataframe : DataFrame
        The Spark DataFrame containing value counts under the `count` column.
    num_groups : int
        The number of groups to create.
    grouping_column : str
        The column that `count` column refers to.

    Returns
    -------
    DataFrame
        A Spark DataFrame containing columns `value` and `group`.
    """
    spark: SparkSession = value_counts_spark_dataframe.sparkSession
    # to create buckets
    # # track with 2 separate hash maps
    counts_bucket = {i: 0 for i in range(num_groups)}
    keys_bucket = {i: list() for i in range(num_groups)}
    # stack source and target
    # group by and count

    counts_df = value_counts_spark_dataframe.orderBy("count", ascending=False)
    # iterate through the values in max -> min order ex: [{key: Amazon, value_count: 100000}, ...]
    # find most-empty bucket (num_groups) and place value in it and increment bucket value by value_count
    for row in counts_df.collect():
        smallest_bucket_id = _get_smallest_bucket_id(counts_bucket)
        counts_bucket[smallest_bucket_id] = (
            counts_bucket.get(smallest_bucket_id) + row["count"]
        )
        keys_bucket.get(smallest_bucket_id).append(row[grouping_column])

    key_to_group_map = list()
    for bucket_id, lst in keys_bucket.items():
        for v in lst:
            key_to_group_map.append({"value": v, "group": bucket_id})

    return spark.createDataFrame(key_to_group_map)


def _get_smallest_bucket_id(bucket: Dict[int, int]) -> int:
    """Return the key of the smallest bucket."""

    min_val = float("inf")
    min_bucket_id = 0
    for k, v in bucket.items():
        if v < min_val:
            min_val = v
            min_bucket_id = k

    return min_bucket_id


def create_group_column_from_source_and_target_groups(
    spark_dataframe: DataFrame,
) -> DataFrame:
    """Add a `group` column to the Spark DataFrame."""

    return spark_dataframe.withColumn(
        "group", concat(col("source_group"), lit(" --> "), col("target_group"))
    )


def create_value_counts_dataframe(
    spark_dataframe: DataFrame, grouping_column: str
) -> DataFrame:
    """
    Create a `count` column based on the `grouping_column` argument.

    Parameters
    ----------
    spark_dataframe : DataFrame
        The Spark DataFrame to operate on.
    grouping_column : str
        The grouping column to use.

    Returns
    -------
    DataFrame
        The value counts Spark DataFrame.
    """
    sdf_filtered = spark_dataframe.select(grouping_column)

    counts_df: DataFrame = sdf_filtered.groupBy(grouping_column).count()

    return counts_df

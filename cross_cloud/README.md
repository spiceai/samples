# Cross-Cloud sample

This sample demonstrates how to read data from two different cloud vendors, Azure and S3.

```yaml
datasets:
    - from: s3://spiceai-public-datasets/nyc_taxi_2014/
      name: s3_taxi
      description: taxi trips in s3
      params:
        file_format: parquet
      acceleration:
        enabled: true
        refresh_check_interval: 10s
        refresh_mode: full
    - from: abfs://data/nyc_taxi_2015/
      name: abfs_taxi
      description: taxi trips in abfs
      params:
        file_format: parquet
        abfs_account: spiceaidemodatasets
        abfs_skip_signature: true
      acceleration:
        enabled: true
        refresh_check_interval: 10s
        refresh_mode: full
```

When successfully loaded, you'll have two tables in Spice:

```shell
+---------------+--------------+--------------+------------+
| table_catalog | table_schema | table_name   | table_type |
+---------------+--------------+--------------+------------+
| spice         | runtime      | metrics      | BASE TABLE |
| spice         | runtime      | task_history | BASE TABLE |
| spice         | public       | s3_taxi      | BASE TABLE |
| spice         | public       | abfs_taxi    | BASE TABLE |
+---------------+--------------+--------------+------------+
```

And you can query across them as if they were in the same place:

```sql
sql> SELECT COUNT(*) FROM (SELECT * FROM s3_taxi UNION ALL SELECT * FROM abfs_taxi);
```

```shell
+-----------+
| count(*)  |
+-----------+
| 311486810 |
+-----------+
```
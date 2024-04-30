# Spice with rust sdk sample

## Start spice runtime

```shell
spice run
```

## Build sample application

```shell
cargo build
```

## Run sample application

```shell
cargo run
```

Results:

```shell
cargo run
    Finished dev [unoptimized + debuginfo] target(s) in 0.23s
     Running `target/debug/spice-rs-sdk-sample`
RecordBatch { schema: Schema { fields: [Field { name: "VendorID", data_type: Int32, nullable: true, dict_id: 0, dict_is_ordered: false, metadata: {} }, Field { name: "tpep_pickup_datetime", data_type: Timestamp(Microsecond, None), nullable: true, dict_id: 0, dict_is_ordered: false, metadata: {} }, Field { name: "fare_amount", data_type: Float64, nullable: true, dict_id: 0, dict_is_ordered: false, metadata: {} }], metadata: {} }, columns: [PrimitiveArray<Int32>
[
  2,
  2,
  2,
  2,
  2,
  1,
  2,
  2,
  2,
  1,
], PrimitiveArray<Timestamp(Microsecond, None)>
[
  2024-01-24T15:17:12,
  2024-01-24T15:52:24,
  2024-01-24T15:08:55,
  2024-01-24T15:42:55,
  2024-01-24T15:52:23,
  2024-01-24T15:30:55,
  2024-01-24T15:21:48,
  2024-01-24T15:47:59,
  2024-01-24T15:55:32,
  2024-01-24T15:02:22,
], PrimitiveArray<Float64>
[
  20.5,
  10.7,
  25.4,
  9.3,
  18.4,
  70.0,
  40.8,
  35.2,
  36.6,
  11.4,
]], row_count: 10 }
```

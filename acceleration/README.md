# Local Materialization and Acceleration CQRS Sample

Use Spice.ai to simplify the process of building a high-performance [Command Query Responsibility Segregation (CQRS)](https://microservices.io/patterns/data/cqrs.html) application with local materialization and acceleration.

In this sample, we use one Spice runtime to replicate and accelerate data from Postgres, which improves the query throughput by 2X (See performance benchmarks below).
Then we use another Spice runtime to show how runtimes can be chained together to accelerate and materialize views on top of the previous Spice runtime. Which improves the query throughput by further 5X.

The sample application has:

1. An `/orders` API to generate a random order with a random count
2. A single PostgreSQL database to receive orders and store products.
3. Three `/ranking` APIs to show the top 5 selling products:

- `/ranking` - fetch data from postgres
- `/ranking-accelerated` - fetch data from Spice runtime without materialized ranking view, it pulls data from postgres into edge acceleration to improve query performance
- `/ranking-materialized` - fetch data from Spice runtime with materialized ranking view, it pulls data from ranking view from the previous Spice runtime and accelerates it locally

![Diagram](/Users/yong/code/work/samples/acceleration/diagram.png)

## How to run

Clone this samples repo locally:
```bash
git clone https://github.com/spiceai/samples.git
cd samples/acceleration
```

`make`

then call the rankings API
`curl localhost:9999/ranking`

## Performance benchmark using oha

Install [oha](https://docs.rs/crate/oha/latest)

Stats:

| Scenario                                                  | Success Rate   | Total Time (secs)   | Slowest (secs)    | Fastest (secs)    | Average (secs)    | Requests/sec    | Total Data   | Size/request    | Size/sec   |
| ----------                                                | -------------- | ------------------- | ----------------- | ----------------- | ----------------- | --------------- | ------------ | --------------- | ---------- |
| From Postgres                                             | 99.82%         | 47.4194             | 1.1856            | 0.0003            | 0.2364            | 421.7687        | 2.70 MiB     | 14              | 58.41 KiB  |
| Spice.ai OSS with acceleration, without materialized view | 100.00%        | 22.3230             | 0.2257            | 0.0058            | 0.1115            | 895.9356        | 2.71 MiB     | 14              | 124.24 KiB |
| Spice.ai OSS with acceleration, with materialized view    | 100.00%        | 4.4439              | 0.0628            | 0.0010            | 0.0222            | 4500.5780       | 2.71 MiB     | 14              | 624.10 KiB |

See more details below.

### From Postgres

```bash
…/sample-1 main ❯ oha -n20000 -c100 'http://localhost:9999/ranking'
Summary:
  Success rate: 100.00%
  Total:        47.4194 secs
  Slowest:      1.1856 secs
  Fastest:      0.0003 secs
  Average:      0.2364 secs
  Requests/sec: 421.7687

  Total data:   2.70 MiB
  Size/request: 14
  Size/sec:     58.41 KiB

Response time histogram:
  0.000 [1]    |
  0.119 [8011] |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
  0.237 [2189] |■■■■■■■■
  0.356 [3873] |■■■■■■■■■■■■■■■
  0.474 [3152] |■■■■■■■■■■■■
  0.593 [1840] |■■■■■■■
  0.711 [736]  |■■
  0.830 [154]  |
  0.949 [30]   |
  1.067 [9]    |
  1.186 [5]    |

Response time distribution:
  10.00% in 0.0029 secs
  25.00% in 0.0523 secs
  50.00% in 0.2186 secs
  75.00% in 0.3927 secs
  90.00% in 0.4981 secs
  95.00% in 0.5898 secs
  99.00% in 0.7113 secs
  99.90% in 0.9032 secs
  99.99% in 1.1139 secs


Details (average, fastest, slowest):
  DNS+dialup:   0.0027 secs, 0.0012 secs, 0.0031 secs
  DNS-lookup:   0.0000 secs, 0.0000 secs, 0.0002 secs

Status code distribution:
  [200] 19964 responses
  [500] 36 responses
```

### From Spice.ai OSS with acceleration, without materialized view

```bash
…/sample-1 main 47s ❯ oha -n20000 -c100 'http://localhost:9999/ranking-accelerated'
Summary:
  Success rate: 100.00%
  Total:        22.3230 secs
  Slowest:      0.2257 secs
  Fastest:      0.0058 secs
  Average:      0.1115 secs
  Requests/sec: 895.9356

  Total data:   2.71 MiB
  Size/request: 14
  Size/sec:     124.24 KiB

Response time histogram:
  0.006 [1]    |
  0.028 [146]  |■
  0.050 [744]  |■■■■■
  0.072 [2089] |■■■■■■■■■■■■■■■
  0.094 [3462] |■■■■■■■■■■■■■■■■■■■■■■■■■
  0.116 [4356] |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
  0.138 [4175] |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
  0.160 [3134] |■■■■■■■■■■■■■■■■■■■■■■■
  0.182 [1467] |■■■■■■■■■■
  0.204 [384]  |■■
  0.226 [42]   |

Response time distribution:
  10.00% in 0.0634 secs
  25.00% in 0.0854 secs
  50.00% in 0.1122 secs
  75.00% in 0.1379 secs
  90.00% in 0.1588 secs
  95.00% in 0.1701 secs
  99.00% in 0.1912 secs
  99.90% in 0.2083 secs
  99.99% in 0.2235 secs


Details (average, fastest, slowest):
  DNS+dialup:   0.0027 secs, 0.0012 secs, 0.0032 secs
  DNS-lookup:   0.0000 secs, 0.0000 secs, 0.0002 secs

Status code distribution:
  [200] 20000 responses
```

### From Spice.ai OSS with acceleration, with materialized view

```bash
…/sample-1 main ❯ oha -n20000 -c100 'http://localhost:9999/ranking-materialized'
Summary:
  Success rate: 100.00%
  Total:        4.4439 secs
  Slowest:      0.0628 secs
  Fastest:      0.0010 secs
  Average:      0.0222 secs
  Requests/sec: 4500.5780

  Total data:   2.71 MiB
  Size/request: 14
  Size/sec:     624.10 KiB

Response time histogram:
  0.001 [1]    |
  0.007 [65]   |
  0.013 [953]  |■■■
  0.020 [6626] |■■■■■■■■■■■■■■■■■■■■■■■■■■■
  0.026 [7627] |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
  0.032 [3117] |■■■■■■■■■■■■■
  0.038 [1126] |■■■■
  0.044 [358]  |■
  0.050 [99]   |
  0.057 [17]   |
  0.063 [11]   |

Response time distribution:
  10.00% in 0.0153 secs
  25.00% in 0.0178 secs
  50.00% in 0.0212 secs
  75.00% in 0.0254 secs
  90.00% in 0.0307 secs
  95.00% in 0.0346 secs
  99.00% in 0.0421 secs
  99.90% in 0.0533 secs
  99.99% in 0.0623 secs


Details (average, fastest, slowest):
  DNS+dialup:   0.0027 secs, 0.0013 secs, 0.0033 secs
  DNS-lookup:   0.0000 secs, 0.0000 secs, 0.0001 secs

Status code distribution:
  [200] 20000 responses
```

## Clean up

To stop and remove the Docker containers/volumes that were created, run:

`make clean`

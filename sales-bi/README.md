# Sales BI Dashboard

## Context

This sample will show how to configure a BI dashboard to use Spice.ai as the data source. The sales data will be stored in a PostgreSQL server. This PostgreSQL server is used by downstream sales applications to record new transactions. There is a requirement to run analytics on this data to power a BI dashboard to understand sales trends - but the operations team doesn't want to add any additional load to the production database.

Spice.ai can be used to accelerate data from connected data sources by keeping an automatically updated copy of the data in an optimized format. This data can be used to power a BI dashboard without adding any additional load to the production database.

## Pre-requisites

This sample requires [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) to be installed.

## Running the sample

![](https://imagedelivery.net/HyTs22ttunfIlvyd6vumhQ/c16c7dda-c403-4c71-0d6d-066005dd0e00/public)

This sample consists of a PostgreSQL server loaded with some sample sales data, a Spice.ai runtime accelerating the data from the PostgreSQL server, and an Apache Superset instance to visualize the data.

Navigate to the `sales-bi` directory and run the following command:

`make`

This will start the PostgreSQL server, Spice.ai runtime, and Apache Superset. The Spice.ai runtime will automatically start accelerating the data from the PostgreSQL server.

The output of the `make` command should look like:

```bash
 ✔ Container superset-sales-bi-demo  Started                                                                                                                                           0.0s
 ✔ Container sales-bi-postgres-1     Started                                                                                                                                           0.0s
 ✔ Container spiceai-sales-bi-demo   Started                                                                                                                                           0.0s
Connection to localhost port 8088 [tcp/radan-http] succeeded!
Initializing Superset...

Superset is running at http://localhost:8088, login with admin/admin
```

Navigate to [http://localhost:8088](http://localhost:8088) to access the Apache Superset dashboard. The login credentials are `admin/admin`.

# TODO: Add instructions on how to connect to the Spice.ai runtime

# TODO: Add instructions on how to load the dashboard

## Clean up

`docker compose down`
`docker volume prune`

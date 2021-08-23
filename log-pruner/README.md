# Log Pruner

A CPU based log pruning example.

This example uses CPU metrics to anticipate the best time to prune logs.  It pulls CPU metrics collected by [Telegraf](https://www.influxdata.com/time-series-platform/telegraf/) from [InfluxDB](https://www.influxdata.com/products/influxdb/) and uses them to determine likely times of low load.

## Prerequisites

This example requires

- [Docker](https://docs.docker.com/get-docker/) (v20.10 for Linux or v18.03 for Windows/MacOS)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Collect CPU metrics

First, ensure this `samples` repository is cloned.

```bash
git clone https://github.com/spiceai/samples.git
```

Move to the `log-pruner` directory and start collecting metrics.

```bash
cd samples
cd log-pruner
docker-compose up
```

You will observe Telegraf and InfluxDB start up.  After both containers have started, CPU metrics will begin flowing into InfluxDB.

## Set up a Datasource

Now, let's look at how we can use Spice AI to determine the best time to prune logs using these metrics.  We've created a sample Pod manifest that will show you how to do this.  First, we will learn how we can use a Spice AI Datasource to consume our metrics.  Take a look at the `log-pruner.yaml` Pod manifest in the `log-pruner` directory, paying particular attention to the `datasources` section:

```yaml
<snip>
datasources:
- from: hostmetrics
  name: cpu
  data:
    connector:
      name: influxdb
      params:
        url: SPICE_INFLUXDB_URL
        token: SPICE_INFLUXDB_TOKEN
        org: SPICE_INFLUXDB_ORG
        bucket: SPICE_INFLUXDB_BUCKET
        measurement: cpu
        field: usage_idle
    processor:
      name: flux-csv
  fields:
      # "usage_idle" measures the percentage of time the CPU is idle
      # Higher values indicate less load
      - name: usage_idle
<snip>
```

A Spice AI Datasource has two components, a Connector and a Processor.  A Connector fetches data from a specific source, like a database or a file.  A Processor takes the data that the Connector has fetched and transforms it into a format Spice AI can use.  In this example, we are using the `influxdb` Connector to provide [Flux Annotated CSV](https://docs.influxdata.com/influxdb/cloud/reference/syntax/annotated-csv/) to the `flux-csv` processor.  We will extract the `usage_idle` field of measurements taken from the `cpu`, where `usage_idle` refers to the percentage of time the CPU has spent in an idle state.

In the `params` section of the InfluxDB Connector, notice we are using environment variables prefixed with `SPICE_` to pass configuration.  Any environment variable with this prefix will automatically be replaced with its value by the Spice AI runtime.

## Add some Actions

Now that we have some data for Spice AI to examine, we need to tell it what kinds of Actions we would like to perform on that data.  Take a look at the `actions` section of `log-pruner.yaml`:

```yaml
actions:
  - name: prune_logs
  - name: do_not_prune_logs
```

Notice that we have two Actions defined, `prune_logs` and `do_not_prune_logs`.  As it learns and then later makes recommendations, Spice AI will consider only these two options.

## Reward the Actions

So far, we've provided Spice AI with CPU usage metrics and told it we want to consider whether or not to prune logs at any given time.  Now, we need to tell it how to weigh the consequences of taking each of those actions during training.  We do that by defining Rewards.  Take a look at the `rewards` section:

```yaml
training:
  rewards:
    # Reward pruning logs at a time when load is anticipated to be low
    # The lower the load, the higher the reward
    # Punish pruning logs harshly at a time when load is high (idle < 90%)
    - reward: prune_logs
      with: reward = new_state.hostmetrics_cpu_usage_idle * 100 if new_state.hostmetrics_cpu_usage_idle > 0.90 else -1000

    # Reward not pruning logs under load
    # Punish not pruning logs slightly when load is low (idle > 90%)
    - reward: do_not_prune_logs
      with: reward = 100 if new_state.hostmetrics_cpu_usage_idle < 0.90 else -10
```

Here, we tell Spice AI how we want to reward each action, given the state at that step.  These rewards are defined by simple Python expressions that assign a value to `reward`.  A higher value means Spice AI will learn to take this action more frequently as it trains.  We can use values from our Datasources to calculate these rewards.  They can be accessed with the expression `(new_state|prev_state).(from)_(name)_(field)`.  Here we are using `new_state.hostmetrics_cpu_usage_idle`.

## Train

Now let's use these three elements of our Pod to train Spice AI.

We've provided some example environment variables that will work with the InfluxDB container we started earlier.  In another terminal, add them to your environment:

```bash
cd samples
cd log-pruner
source set-spice-vars.sh
```

Now, start the Spice AI runtime:

```bash
spice run
```

Once the Spice runtime has loaded, add the LogPruner Pod using another terminal.

```bash
cd samples
cd log-pruner
cp log-pruner.yaml .spice/pods
```

In the Spice AI runtime terminal, you will observe the runtime load CPU metrics and begin to train!

## Inference

Now try fetching a recommendation from the newly trained Pod.

```bash
curl http://localhost:8000/api/v0.1/pods/log-pruner/inference
```

You'll see a result telling you if now is a good time to prune logs or not, along with Spice AI's confidence in that recommendation.  Cool!

```json
{
  "action": "prune_logs",
  "confidence": 0.95,
  "end": "2021-08-17T21:45:30",
  "start": "2021-08-17T21:35:30",
  "tag": "latest"
}
```
# Log Pruner

A CPU based log pruning sample.

This sample uses CPU metrics as in input to Spice.ai to recommend the best time to prune logs. It pulls CPU metrics collected by [Telegraf](https://www.influxdata.com/time-series-platform/telegraf/) from [InfluxDB](https://www.influxdata.com/products/influxdb/) and uses them to determine likely times of low load.

## Prerequisites

This sample requires

- [Spice.ai](https://crispy-dollop-c329115a.pages.github.io/#/install)
- [Docker](https://docs.docker.com/get-docker/) (v20.10 for Linux or v18.03 for Windows/MacOS)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Powershell](https://docs.microsoft.com/en-us/powershell/scripting/install/installing-powershell?view=powershell-7.1)

## Collect CPU metrics

First, ensure this `samples` repository is cloned.

```bash
git clone https://github.com/spiceai/samples.git
```

Move to the `logpruner` directory and start the Telegraf and InfluxDB containers to start collecting and storing metrics.

```bash
cd samples
cd logpruner
docker-compose up
```

You will observe Telegraf and InfluxDB start up. After both containers have started, CPU metrics will begin flowing into InfluxDB.

## Using Spice.ai to train

Use Spice.ai to train a model that can provide a recommendation on the best time to prune logs using these metrics.

Example environment variables that will work with the InfluxDB container have been provided in the `set-spice-vars.sh` script. In another terminal, add them to your environment for use by the Spice.ai runtime:

```bash
cd samples
cd logpruner
source set-spice-vars.sh
```

Now, start the Spice.ai runtime:

```bash
spice run
```

Once the Spice.ai runtime has loaded, open another terminal, and start training:

```bash
cd samples
cd logpruner
spice train logpruner
```

In the Spice.ai runtime terminal, you will observe the runtime load CPU metrics and begin to train!

## Start the server maintenance app

While Spice.ai is training the model, start the server maintenance app that comes with this sample:

```bash
pwsh ./logpruner.ps1
```

You should see output that looks like:

```
Server Maintenance v0.1!

Ctrl-C to stop running

Time to perform a maintenance run, checking to see if now is a good time to run
Recommendation to do_not_prune_logs with confidence
Recommendation has a confidence of 0. Has this pod been trained yet?
```

Once the pod has finished training, the output should change to show that now is a good time to run server maintenance or not.

## How it works

Spice.ai was able to use the Telegraf data stored in InfluxDB along with definitions for possible actions it can recommend to train and provide a recommendation on when to prune logs.

Open the Pod manifest `logpruner.yml` in the `.spice/pods` directory.

Review the `dataspaces` section on how the data was connected.

```yaml
<snip>
dataspaces:
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

A Spice.ai Dataspace has two components, a Connector and a Processor. A Connector fetches data from a specific source, like a database or a file. A Processor takes the data that the Connector has fetched and transforms it into a format Spice.ai can use. In this example, we are using the `influxdb` Connector to provide [Flux Annotated CSV](https://docs.influxdata.com/influxdb/cloud/reference/syntax/annotated-csv/) to the `flux-csv` processor. We will extract the `usage_idle` field of measurements taken from the `cpu`, where `usage_idle` refers to the percentage of time the CPU has spent in an idle state.

In the `params` section of the InfluxDB Connector, notice we are using environment variables prefixed with `SPICE_` to pass configuration. Any environment variable with this prefix will automatically be replaced with its value by the Spice.ai runtime.

### Actions

The possible actions to provide as recommendations were defined in the `actions` section of the manifest.

```yaml
actions:
  - name: prune_logs
  - name: do_not_prune_logs
```

There are two Actions defined, `prune_logs` and `do_not_prune_logs`. Spice.ai will train using both actions to provide a recommendation on which one to take.

### Rewards

Spice.ai learns which action to recommend by rewarding or penalizing an action using a Reward definition. Review the `rewards` section of the manifest:

```yaml
training:
  rewards:
    # Reward pruning logs at a time when load is anticipated to be low
    # The lower the load, the higher the reward
    # Penalize pruning logs harshly at a time when load is high (idle < 90%)
    - reward: prune_logs
      with: reward = new_state.hostmetrics_cpu_usage_idle * 100 if new_state.hostmetrics_cpu_usage_idle > 0.90 else -1000

    # Reward not pruning logs under load
    # Penalize not pruning logs slightly when load is low (idle > 90%)
    - reward: do_not_prune_logs
      with: reward = 100 if new_state.hostmetrics_cpu_usage_idle < 0.90 else -10
```

Here, we tell Spice.ai how we want to reward each action, given the state at that step. These rewards are defined by simple Python expressions that assign a value to `reward`. A higher value means Spice.ai will learn to take this action more frequently as it trains. We can use values from our Dataspaces to calculate these rewards. They can be accessed with the expression `(new_state|prev_state).(from)_(name)_(field)`. Here we are using `new_state.hostmetrics_cpu_usage_idle`.

## Next steps

- Review the [Spice.ai documentation](https://crispy-dollop-c329115a.pages.github.io/#/?id=reference) on the Pod manifest

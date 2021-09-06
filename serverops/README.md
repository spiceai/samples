# ServerOps

A CPU based server operations sample.

This sample uses CPU metrics as in input to Spice.ai to recommend the best time to perform operations on a server. It pulls CPU metrics collected by [Telegraf](https://www.influxdata.com/time-series-platform/telegraf/) from [InfluxDB](https://www.influxdata.com/products/influxdb/) and uses them to determine likely times of low load.

## Prerequisites

This sample requires

- [Spice.ai](https://docs.spiceai.org/getting-started/install-spiceai/)
- [Docker](https://docs.docker.com/get-docker/) (v20.10 for Linux or v18.03 for Windows/MacOS)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Powershell](https://docs.microsoft.com/en-us/powershell/scripting/install/installing-powershell?view=powershell-7.1)

## Collect CPU metrics

First, ensure this `samples` repository is cloned.

```bash
git clone https://github.com/spiceai/samples.git
```

Move to the `serverops` directory and start the Telegraf and InfluxDB containers to start collecting and storing metrics.

```bash
cd samples
cd serverops
docker-compose up
```

You will observe Telegraf and InfluxDB start up. After both containers have started, CPU metrics will begin flowing into InfluxDB.

## Using Spice.ai to train

Use Spice.ai to train a model that can provide a recommendation on the best time to perform operations using these metrics.

Example environment variables that will work with the InfluxDB container have been provided in the `set-spice-vars.sh` script. In another terminal, add them to your environment for use by the Spice.ai runtime:

```bash
cd samples
cd serverops
source set-spice-vars.sh
```

Add the ServerOps pod from spicerack.org by using the CLI:

```bash
spice add samples/ServerOps
```

Now, start the Spice.ai runtime:

```bash
spice run
```

Once the Spice.ai runtime has loaded, open another terminal, and start training:

```bash
cd samples
cd serverops
spice train serverops
```

In the Spice.ai runtime terminal, you will observe the runtime load CPU metrics and begin to train!

## Start the server maintenance app

While Spice.ai is training the model, start the server maintenance app that comes with this sample:

```bash
pwsh ./serverops.ps1
```

You should see output that looks like:

```
Server Maintenance v0.1!

Ctrl-C to stop running

Time to perform a maintenance run, checking to see if now is a good time to run
Recommendation to do_nothing with confidence
Recommendation has a confidence of 0. Has this pod been trained yet?
```

Once the pod has finished training, the output should change to show that now is a good time to run server operations or not.

## How it works

Spice.ai was able to use the Telegraf data stored in InfluxDB along with definitions for possible actions it can recommend to train and provide a recommendation on when to run server operations.

Open the Pod manifest `serverops.yml` in the `spicepods` directory.

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

A Spice.ai Dataspace has two components, a Connector and a Processor. A Connector fetches data from a specific source, like a database or a file. A Processor takes the data that the Connector has fetched and transforms it into a format Spice.ai can use. This example uses the `influxdb` Connector to provide [Flux Annotated CSV](https://docs.influxdata.com/influxdb/cloud/reference/syntax/annotated-csv/) to the `flux-csv` processor. It extracts the `usage_idle` field of measurements taken from the `cpu`, where `usage_idle` refers to the percentage of time the CPU has spent in an idle state.

In the `params` section of the InfluxDB Connector, notice the use of environment variables prefixed with `SPICE_` to pass configuration. Any environment variable with this prefix will automatically be replaced with its value by the Spice.ai runtime.

### Actions

The possible actions to provide as recommendations were defined in the `actions` section of the manifest.

```yaml
actions:
  - name: perform_maintenance
  - name: preload_cache
  - name: do_nothing
```

There are three Actions defined, `perform_maintenance`, `preload_cache` and `do_nothing`. Spice.ai will train using all three actions to provide a recommendation on which one to take.

### Rewards

Spice.ai learns which action to recommend by rewarding or penalizing an action using a Reward definition. Review the `rewards` section of the manifest:

```yaml
training:
  reward_init: |
    high_cpu_usage_threshold = 10
    cpu_usage_new = 100 - new_state.hostmetrics_cpu_usage_idle
    cpu_usage_prev = 100 - prev_state.hostmetrics_cpu_usage_idle
    cpu_usage_delta = cpu_usage_new - cpu_usage_prev

    cpu_usage_delta_abs = cpu_usage_delta
    if cpu_usage_delta_abs < 0:
      cpu_usage_delta_abs *= -1
  rewards:
    - reward: perform_maintenance
      with: |
        # Reward when cpu usage is low and stable
        if cpu_usage_new < high_cpu_usage_threshold:
          # The lower the cpu usage, the higher the reward
          reward = high_cpu_usage_threshold - cpu_usage_new
          # Add an additional reward if the cpu usage trend is stable
          if cpu_usage_delta_abs < 2:
            reward *= 1.5

        else:
          # Penalize performing maintenance at a time when cpu usage is high
          # The higher the cpu usage, the more harsh the penalty should be 
          reward = high_cpu_usage_threshold - cpu_usage_new
    - reward: preload_cache
      with: |
        # Reward when cpu usage is low and rising
        # Is the cpu usage high now, and was the cpu usage low previously?
        # If so, previous state was a better time to preload,
        # so give a negative reward based on the change
        if cpu_usage_new > high_cpu_usage_threshold and cpu_usage_delta > 25:
          reward = -cpu_usage_delta

        # Reward preloading during low cpu usage
        else:
          reward = high_cpu_usage_threshold - cpu_usage_new

    - reward: do_nothing
      with: |
        # Reward doing nothing under high cpu usage
        # The higher the cpu usage, the higher the reward
        if cpu_usage_new > high_cpu_usage_threshold:
          reward = high_cpu_usage_threshold - cpu_usage_new
        # Penalize doing nothing slightly when cpu usage is low
        else:
          reward = -1
          # If the cpu usage trend is unstable, do not apply the penalty
          if cpu_usage_delta_abs > 5:
            reward = 0
```

This section tells Spice.ai how to reward each action, given the state at that step. These rewards are defined by simple Python expressions that assign a value to `reward`. A higher value means Spice.ai will learn to take this action more frequently as it trains. You can use values from your Dataspaces to calculate these rewards. They can be accessed with the expression `(new_state|prev_state).(from)_(name)_(field)`. This example uses `new_state.hostmetrics_cpu_usage_idle` and `new_state.hostmetrics_cpu_usage_idle`.

Notice the `reward_init` section. This section can be used to for common initialization tasks that will be applied to every action's reward function. In this example, a `cpu_usage_delta` variable is created to reason about the stability of the system's load from one moment to the next.

## Next steps

- Review the [Spice.ai documentation](https://docs.spiceai.org/reference/pod/) on the Pod manifest

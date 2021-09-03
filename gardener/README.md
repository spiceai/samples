# Gardener

This sample uses temperature and moisture sensor data as input to Spice.ai to water a simulated garden. A simple control loop is used to sample the conditions of the soil, then open a watering valve based on recommendations from Spice.ai.

## Prerequisites

This sample requires

- [Spice.ai](https://crispy-dollop-c329115a.pages.github.io/#/install)
- [Python 3](https://www.python.org/downloads/)

## Start the Spice.ai runtime

First, ensure this `samples` repository is cloned.

```bash
git clone https://github.com/spiceai/samples.git
```

Move to the `gardener` directory, retrieve the gardener pod from spicerack.org and start the Spice.ai runtime.

```bash
cd samples/gardener
spice add samples/gardener
spice run
```

You will observe the Spice.ai runtime start up and load a `sensors/garden` dataspace.

## Use Spice.ai to a train a model

Use Spice.ai to train a model that can control your watering valve.

In another terminal, start a training run:

```bash
cd samples/gardener
spice train gardener
```

In the Spice.ai runtime terminal, you will observe the runtime load sensor data and begin to train!

## Water your garden

After training completes, use the newly trained model to help control your garden watering software. First, install the Python dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

Now, run the garden watering simulator:

```bash
python3 main.py
```

You will see a sensor readings from simulated garden and a smart watering inputs powered by Spice.ai:

```
Time (s): 1616731200 Temperature (C): 8.341 Moisture (%): 0.294
Time (s): 1616734800 Temperature (C): 7.202 Moisture (%): 0.289
Time (s): 1616738400 Temperature (C): 6.229 Moisture (%): 0.285
Time (s): 1616742000 Temperature (C): 5.366 Moisture (%): 0.282
Time (s): 1616745600 Temperature (C): 4.438 Moisture (%): 0.279
Watering at full flow
Time (s): 1616749200 Temperature (C): 3.678 Moisture (%): 0.286
...
```

## How it works

### Dataspaces

Open the `gardener` pod manifest at [.spice/pods/gardener.yaml](.spice/pods/gardener.yaml), paying particular attention to the `dataspaces` section:

```
dataspaces:
  - from: sensors
    name: garden
    fields:
      - name: temperature
      - name: moisture
    data:
      connector:
        name: file
        params:
          path: data/garden_data.csv
      processor:
        name: csv
```

This particular Spice.ai [dataspace](https://crispy-dollop-c329115a.pages.github.io/#/concepts/README?id=dataspace) is using a `csv` [data processor](https://crispy-dollop-c329115a.pages.github.io/#/concepts/README?id=data-processor) and a `file` [data connector](https://crispy-dollop-c329115a.pages.github.io/#/concepts/README?id=data-connector) to extract the `temperature` and `moisture` columns from `data/garden_data.csv`. You can learn more about dataspaces in the [Core Concepts](https://crispy-dollop-c329115a.pages.github.io/#/concepts/README) section of the Spice.ai documentation.

### Actions

The possible actions to provide as recommendations are defined in the `actions` section of the manifest:

```yaml
actions:
  - name: close_valve
  - name: open_valve_half
  - name: open_valve_full
```

Spice.ai will train using these three actions to provide a recommendation on which one to take when asked.

### Rewards

Spice.ai learns which action to recommend by rewarding or penalizing an action using a Reward definition. Review the `rewards` section of the manifest:

```yaml
training:
  rewards:
    - reward: close_valve
      with: |
        # Reward keeping moisture content above 25%
        if new_state.sensors_garden_moisture > 0.25:
          reward = 200

        # Penalize low moisture content depending on how far the garden has dried out
        else:
          reward = -100 * (0.25 - new_state.sensors_garden_moisture)

          # Penalize especially heavily if the drying trend is continuing (new_state is drier than prev_state)
          if new_state.sensors_garden_moisture < prev_state.sensors_garden_moisture:
            reward = reward * 2

    - reward: open_valve_half
      with: |
        # Reward watering when needed, more heavily if the garden is more dried out
        if new_state.sensors_garden_moisture < 0.25:
          reward = 100 * (0.25 - new_state.sensors_garden_moisture)

        # Penalize wasting water
        # Penalize overwatering depending on how overwatered the garden is
        else:
          reward = -50 * (new_state.sensors_garden_moisture - 0.25)

    - reward: open_valve_full
      with: |
        # Reward watering when needed, more heavily if the garden is more dried out
        if new_state.sensors_garden_moisture < 0.25:
          reward = 200 * (0.25 - new_state.sensors_garden_moisture)

        # Penalize wasting water more heavily with valve fully open
        # Penalize overwatering depending on how overwatered the garden is
        else:
          reward = -100 * (new_state.sensors_garden_moisture - 0.25)
```

This section tells Spice.ai to reward each action, given the state at that step. These rewards are defined by simple Python expressions that assign a value to `reward`. A higher value means Spice.ai will learn to take this action more frequently as it trains. You can use values from your Dataspaces to calculate these rewards. They can be accessed with the expression `(new_state|prev_state).(from)_(name)_(field)`. 

Here, `new_state.sensors_garden_moisture` and `prev_state.sensors_garden_moisture` are being used to either reward or penalize opening or closing the watering valve. Notice how `new_state.sensors_garden_moisture` being compared to `prev_state.sensors_garden_moisture` in the reward for `close_valve`.  This allows Spice.ai to gain a sense of directionality from its data. 

### Observations

Spice.ai learns about your application's environment in real time through Observations. Open the sample application in [main.py](main.py) to see how that is done (code has been trimmed slightly for clarity):

```python
SPICE_AI_OBSERVATIONS_URL = "http://localhost:8000/api/v0.1/pods/gardener/observations"

output = io.StringIO()
writer = csv.writer(output)
writer.writerow(
    ["time", "sensors.garden.temperature", "sensors.garden.moisture"]
)

garden.update()
writer.writerow(
    [
        garden.get_time_unix_seconds(),
        round(garden.get_temperature(), 3),
        round(garden.get_moisture(), 3),
    ]
)

requests.post(SPICE_AI_OBSERVATIONS_URL, data=output.getvalue())
```

Spice.ai's observations endpoint accepts CSV formatted data with the following structure:

- A "time" column must be included with all observations.  Spice.ai works on timeseries data, so it's important to include this context.
- Column headers must be structured as `(dataspace from).(dataspace name).(dataspace field)`

As observations are passed to Spice.ai, it will automatically update the recommendations it gives your applications to take them into account.  You can also retrain your application using the new observations at any time.  Cool!

You can learn more about observations in the [documentation](https://docs.spiceai.org/reference/api/#observations).

### Recommendations

Open the sample application in [main.py](main.py) and look at how it is getting recommendations from Spice.ai:

```python
response = requests.get("http://localhost:8000/api/v0.1/pods/gardener/recommendation")
response_json = response.json()
recommended_action = response_json["action"]
```

Spice.ai provides an easy way to get recommendations at any point via a simple `GET` request. This request returns a response in this format:

```json
{
  "response": {
    "result": "ok"
  },
  "start": 1616788800,
  "end": 1616792400,
  "action": "close_valve",
  "confidence": 0.841,
  "tag": "latest"
}
```

Here you can see the window of time the recommendation is based on (`start` to `end`), the action Spice.ai recommends ("close_valve"), and Spice.ai's confidence in that recommendation expressed as a percentage. You can learn more about recommendations through the Spice.ai API in the [documentation](https://crispy-dollop-c329115a.pages.github.io/#/api/README?id=api).

## Next steps

- Learn more about the [Spice.ai API](https://crispy-dollop-c329115a.pages.github.io/#/api/README?id=api) and how you can use it to integrate with your app.
- Review the [Core Concepts](https://crispy-dollop-c329115a.pages.github.io/#/concepts/README) of Spice.ai and how they can help you better leverage its capabilities.
- Try out the other [samples](../README.md) in this repository.

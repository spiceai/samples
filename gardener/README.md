# Gardener

This sample uses temperature and moisture sensor data as input to Spice.ai to water a simulated garden. A simple control loop is used to sample the conditions of the soil, then open a watering valve based on recommendations from Spice.ai.

## Prerequisites

This sample requires

- [Spice.ai](https://docs.spiceai.org/getting-started/install-spiceai/)
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

This particular Spice.ai [dataspace](https://docs.spiceai.org/concepts/#dataspace) is using a `csv` [data processor](https://docs.spiceai.org/concepts/#data-processor) and a `file` [data connector](https://docs.spiceai.org/concepts/#data-connector) to extract the `temperature` and `moisture` columns from `data/garden_data.csv`. You can learn more about dataspaces in the [Concepts](https://docs.spiceai.org/concepts/) section of the Spice.ai documentation.

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
          reward = 100
        else:
          reward = -10

    - reward: open_valve_half
      with: |
        # Reward watering when needed, but penalize wasting water
        if new_state.sensors_garden_moisture < 0.25:
          reward = 10
        else:
          reward = -25

    - reward: open_valve_full
      with: |
        # Reward watering when needed, but penalize wasting water
        if new_state.sensors_garden_moisture < 0.25:
          reward = 10
        else:
          reward = -50
```

This section tells Spice.ai to reward each action, given the state at that step. These rewards are defined by simple Python expressions that assign a value to `reward`. A higher value means Spice.ai will learn to take this action more frequently as it trains. You can use values from your Dataspaces to calculate these rewards. They can be accessed with the expression `(new_state|prev_state).(from)_(name)_(field)`. Here the `new_state.sensors_garden_moisture` is being used to either reward or penalize opening or closing the watering valve.

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

Here you can see the window of time the recommendation is based on (`start` to `end`), the action Spice.ai recommends ("close_valve"), and Spice.ai's confidence in that recommendation expressed as a percentage. You can learn more about recommendations through the Spice.ai API in the [documentation](https://docs.spiceai.org/reference/api/).

## Next steps

- Learn more about the [Spice.ai API](https://docs.spiceai.org/reference/api/) and how you can use it to integrate with your app.
- Review the [Concepts](https://docs.spiceai.org/concepts/) of Spice.ai and how they can help you better leverage its capabilities.
- Try out the other [samples](../README.md) in this repository.

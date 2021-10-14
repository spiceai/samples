# Trader

> **NOTE** This is an example only. Nothing from Spice AI ever constitutes financial advice.

A basic Bitcoin trading bot example using Coinbase Pro exchange data.

Let's try an example that uses streaming Bitcoin prices to learn when to make Buy and Sell trades.

## Requirements

- [Node.js](https://nodejs.org/)
- [Spice.ai](https://docs.spiceai.org/getting-started/install-spiceai/)

## Setup

First, ensure this repository, `samples` is cloned or is opened in GitHub Codespaces.

```bash
git clone https://github.com/spiceai/samples.git
```

Move to the `trader` directory and start the Spice.ai runtime.

```bash
cd samples
cd trader
spice run
```

So that you can watch the Spice.ai runtime output and enter commands at the same time, open another terminal (also in the `trader` directory).

> **Note**
> If you are using GitHub Codespaces or VS Code, then you can open a new terminal in split-view mode by clicking the 'split' button.
> ![alt](/.imgs/split_terminal.png)

Run npm install in the new terminal to setup the sample application.

```bash
npm install
```

## Run the sample application

```bash
node main.js
```

You should see the following output:

```bash
Trader - A Spice trading app
Fetching trade recommendation...
Failed to fetch recommendation. Is the Spice.ai runtime started and has a pod been added?
```

The application will attempt to fetch a recommendation from the Spice.ai runtime but will not find one, because we have not yet created a pod and trained it. Press Ctrl-C to stop the application and let's add a pod in the next step.

## Get the sample pod

In the new terminal add the Trader samplex pod from [spicerack.org](https://spicerack.org):

```bash
spice add samples/trader
```

> Note: The sample pod defaults to an `interval` of 30 seconds, so you will need to wait at least 30 seconds to capture enough streaming market data to start trading.

Once enough data has been capture, you will observe the runtime starting to train! You can also manually start a training run using this command.

```bash
spice train trader
```

You can view the pod training progress at: [http://localhost:8000/pods/trader](http://localhost:8000/pods/trader).

## Recommendations

Once the pod has trained, re-run the sample application:

```bash
node main.js
```

Now you should see output with a recomendation (recommendation may differ from this quickstart as this depends on the trained model):

```bash
Trader - A Spice trading app
Fetching trade recommendation...
Recommendation to SELL with 0.623 confidence.
Holding.
```

You can also fetch a recommendation directly from the API.

```bash
curl http://localhost:8000/api/v0.1/pods/trader/recommendation
```

You'll see a result you can take action on immediately:

```json
{
  "action": "buy",
  "confidence": 0.9,
  "start": 1607886000,
  "end": 1607907600,
  "tag": "latest"
}
```

## Observation Data

You can also view observation data by fetching it with an API call:

```bash
curl http://localhost:8000/api/v0.1/pods/trader/observations
```

## Next steps

Congratulations! You've successfully trained a model that provides real-time recommendations for trades based on live market data and your portfolio constraints!

Try tweaking the parameters in the pod manifest (`spicepods/trader.yaml`) to learn how the Spice.ai runtime behaves.

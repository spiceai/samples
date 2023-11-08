#!/usr/bin/env python

import os
import json
import math
import numpy as np
import pandas as pd
import xgboost as xgb
from typing import Any
from dataclasses import asdict

import spec


class XGBoostForecaster:
    def __init__(self, lookback_size: int, forecast_size: int):
        self.lookback_size = lookback_size
        self.forecast_size = forecast_size
        self.model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=1000)

    def _make_xgboost_data(self, filled_df: pd.DataFrame) -> np.array:
        filled_df.sort_values('ts', inplace=True)
        data = filled_df['y'].values
        has_covariate = 'covariate' in filled_df.columns
        
        X, y = [], []
        for i in range(self.lookback_size, len(data) - self.forecast_size):
            X.append(data[i-self.lookback_size:i])
            y.append(data[i:i+self.forecast_size])
            if has_covariate:
                covariates = filled_df['covariate'].values
                X[-1] = np.append(X[-1], covariates[i-self.lookback_size:i])
        
        return np.array(X), np.array(y)

    def train(self, filled_df: pd.DataFrame) -> Any:
        X, y = self._make_xgboost_data(filled_df)
        train_size = int(0.8 * len(X))
        train_X, train_y = X[:train_size], y[:train_size]
        test_X, test_y = X[train_size:], y[train_size:]
        self.model.fit(train_X, train_y, eval_set=[(test_X, test_y)], verbose=True)
        return self.model.evals_result()
        
    def infer(self, data: pd.DataFrame) -> np.array:
        input_window = data['value'][-self.lookback_size:].to_numpy().reshape(-1).astype("float32")
        if 'covariate' in data.columns:
            covariates = data['covariate'][-self.lookback_size:].to_numpy().reshape(-1).astype("float32")
            input_window = np.concatenate([input_window, covariates], axis=None)
        
        return self.model.predict(input_window.reshape(1, -1))

    def save_model(self, path: str) -> None:
        self.model.save_model(path)

    def load_model(self, path: str) -> None:
        self.model.load_model(path)

def _make_inference_response(predicted: np.ndarray, now: float) -> spec.InferenceResponse:
    return spec.InferenceResponse(forecast=[
        spec.InferencePoint(now + i + 1, float(val) if not math.isnan(float(val)) else -1e10, None)
        for i, val in enumerate(predicted)
    ])

def train(context: Any, runtime: Any) -> None:
    params = spec.TrainParams(**context)
    filled_df = pd.read_parquet(os.getenv('DATA_DIR'))

    forecaster = XGBoostForecaster(params.lookback_size, params.forecast_size)
    eval_results = forecaster.train(filled_df)
    forecaster.save_model(os.path.join(os.environ['OUTPUT_DIR'], 'model.ubj'))

    runtime.upload(json.dumps({
        'items': [
            {
            'type': 'html',
            'html': json.dumps(eval_results)
            }
        ],
    }), 'report.json')

def infer(context: Any, runtime: Any) -> None:
    params = spec.InferenceParams(lookback=[spec.InferencePoint(**x) for x in context.pop('lookback')], **context)
    forecaster = XGBoostForecaster(params.lookback_size, params.forecast_size)
    forecaster.load_model(os.path.join(os.getenv('MODEL_DIR'), params.model_weights_name))

    prediction = forecaster.infer(pd.DataFrame([asdict(x) for x in params.lookback]))

    resp = _make_inference_response(prediction, params.lookback[-1].timestamp)
    runtime.upload(json.dumps(asdict(resp)), 'results.json')

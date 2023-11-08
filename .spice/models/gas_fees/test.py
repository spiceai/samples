import os
import io
import builtins
import json

from typing import List
import numpy as np
import pandas as pd
import xgboost
import tqdm
from sklearn.metrics import mean_absolute_error
import yaml
from pathlib import Path
from pprint import pprint

#from ipfs import Ipfs
#from spec import TrainParams, TrainResponse, InferenceParams, InferenceResponse, HtmlReportItem, PlotlyLayout, PlotlyReportItem, Report
#from util import mse, serialize_report, make_inference_response
#from plotly_utils import scatter, chart_test_results, chart_best_worst, generate_train_report

from gas_fees_v2 import infer, train

# TODO move to spec.py
from typing import List, Optional
from dataclasses import dataclass, field


class SpiceRuntime(object):
    """Utilities for interacting with the Spice Jalaipeno Runtime"""
    def __init__(self, outputs_dir: str):
        self._outputs_dir = outputs_dir

    def upload(self, f: str, name: str = None) -> None:
        if isinstance(f, str):
            if not name:
                raise AssertionError("cannot upload a string without a valid filename")
            with open(os.path.join(self._outputs_dir, name), 'w', encoding='utf8') as dest:
                dest.write(f)
        elif isinstance(f, FileLike):
            with open(os.path.join(self._outputs_dir, f.name), 'wb') as dest:
                shutil.copyfileobj(f, dest)
        else:
            raise AssertionError(f'cannot upload unhandled type {type(f)} to ipfs')

def test_train():
    os.environ["OUTPUT_DIR"] = './output/'
    os.environ["DATA_DIR"] = './data/'
    with open('test/train.yaml', encoding='utf8') as f:
        context = yaml.safe_load(f)

    rt = SpiceRuntime(Path(os.environ["OUTPUT_DIR"]))
    v = train(context, rt)
    pprint(v)

def test_infer():
    os.environ["MODEL_DIR"] = './output/'
    os.environ["OUTPUT_DIR"] = './output/'
    os.environ["INPUT_DIR"] = './data/infer/'
    with open('./test/infer.yaml', encoding='utf8') as f:
        context = yaml.safe_load(f)
    
    rt = SpiceRuntime(Path(os.environ["OUTPUT_DIR"]))
    v = infer(context, rt)
    pprint(v)

if __name__ == '__main__':
    test_infer()
    with open("output/results.json", "r") as f:
        pprint(json.load(f))
    
    # test_train()
    # with open("output/report.json", "r") as f:
    #     pprint(json.load(f))
        

    # r = _infer("./output/model.ubj", pd.read_parquet('./data/infer/'), 30, True)
    # now = pd.read_parquet('./data/infer/')["ts"][0]
    # resp = make_inference_response(r, now)
    # pprint(resp)

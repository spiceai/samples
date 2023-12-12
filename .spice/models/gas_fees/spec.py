from typing import List, Optional
from dataclasses import dataclass, field

@dataclass
class TrainParams:
    model_id: str
    input_parquet_cid: str
    lookback_size: int
    forecast_size: int
    epochs: int
    metadata: Optional[dict]
    runtime: str
    compiled_package_cid: str
    entry_point: str

@dataclass
class TrainResponse:
    model_weights_name: str
    model_weights_cid: str
    report_cid: str

@dataclass
class InferencePoint:
    timestamp: float
    value: float
    covariate: Optional[float]

@dataclass
class InferenceParams:
    lookback: list[InferencePoint]
    model_weights_cid: str
    model_weights_name: str
    lookback_size: int
    forecast_size: int
    runtime: str
    compiled_package_cid: str
    inference_handler: str
    metadata: Optional[dict] = None
    job_id: str = ""
    model_type: str = ""

@dataclass
class InferenceResponse:
    forecast: list[InferencePoint]

@dataclass
class PlotlyGrid:
    subplots: any = None
    rows: int = None
    cols: int = None

@dataclass
class PlotlyLayout:
    title: str
    width: int = None
    height: int = None
    grid: PlotlyGrid = None
    yaxis1: any = None
    yaxis2: any = None
    annotations: list = None

@dataclass
class HtmlReportItem:
    type: str = field(default='html', init=False)
    html: str

@dataclass
class PlotlyReportItem:
    type: str = field(default='plotly', init=False)
    traces: List[any]
    layout: PlotlyLayout


ReportItem = HtmlReportItem | PlotlyReportItem

@dataclass
class Report:
    items: list[ReportItem]


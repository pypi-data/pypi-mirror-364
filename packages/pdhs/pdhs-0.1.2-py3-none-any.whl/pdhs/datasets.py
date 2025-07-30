import polars as pl
import logging
from dataclasses import field, dataclass
from typing import List
from .base_api import DHSBaseAPI

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@dataclass
class GetDatasets(DHSBaseAPI):
    _url_extension: str = "datasets"
    select_surveys: str = None
    file_format: str = None
    file_type: str = None

    def __post_init__(self):
        super().__post_init__()
        
        if self.select_surveys is not None:
            self.url += f"&selectSurveys={self.select_surveys}"
        if self.file_format is not None:
            self.url += f"&fileFormat={self.file_format}"
        if self.file_type is not None:
            self.url += f"&fileType={self.file_type}"
        
        logging.info(f"Extended API URL constructed: {self.url}")


"""indicators_data = GetDatasets(
    country_ids = ["NG"],
    file_format = "DT"
)

df = indicators_data.get_data()
print(df)"""
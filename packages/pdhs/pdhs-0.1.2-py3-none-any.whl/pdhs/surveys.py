import polars as pl
import logging
from dataclasses import dataclass
from .base_api import DHSBaseAPI

@dataclass
class GetSurveys(DHSBaseAPI):
    _url_extension: str = "surveys"
    survey_status: str = None
    

    def __post_init__(self):
        super().__post_init__()
        if self.survey_status is not None:
            self.url += (f"&surveyStatus={self.survey_status}")
        logging.info(f"Extended API URL constructed: {self.url}")

@dataclass
class GetSurveyCharacteristics(DHSBaseAPI):
    _url_extension: str = "surveycharacteristics"

"""survey_data = GetSurveys(
    country_ids=["NG"],
    survey_status="completed",
)
df = survey_data.get_data()
print(df)

survey_xtics = GetSurveyCharacteristics(
    country_ids=["NG"],
    survey_year = ["2018"],
    survey_ids = ["DHS-2018"],
)
df2 = survey_xtics.get_data()
print(df2)"""
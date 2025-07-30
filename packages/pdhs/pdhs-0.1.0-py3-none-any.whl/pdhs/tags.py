from dataclasses import dataclass
from .base_api import DHSBaseAPI

@dataclass
class GetTags(DHSBaseAPI):
    _url_extension: str = "tags"


"""Tags_data = GetTags(
    indicator_ids=["FE_FRTR_W_TFR"]
)

df = Tags_data.get_data()
print(df)"""
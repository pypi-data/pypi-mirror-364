from dataclasses import dataclass
from .base_api import DHSBaseAPI

@dataclass
class GetCountries(DHSBaseAPI):
    _url_extension: str = "countries"


"""countries_data = GetCountries(
    country_ids = ["AL"]
)

df = countries_data.get_data()
print(df)"""
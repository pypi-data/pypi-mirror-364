from dataclasses import dataclass
from .base_api import DHSBaseAPI

@dataclass
class GetGeometry(DHSBaseAPI):
    _url_extension: str = "geometry"


"""geometry_data = GetGeometry(
    country_ids = ["AL"]
)

df = geometry_data.get_data()
print(df)"""
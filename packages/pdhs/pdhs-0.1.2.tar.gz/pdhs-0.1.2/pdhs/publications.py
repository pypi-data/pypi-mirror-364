import polars as pl
import logging
from dataclasses import dataclass
from .base_api import DHSBaseAPI

@dataclass
class GetPublications(DHSBaseAPI):
    _url_extension: str = "publications"


"""get_publications = GetPublications(
    country_ids=["AL"],
)

df = get_publications.get_data()
print(df)"""
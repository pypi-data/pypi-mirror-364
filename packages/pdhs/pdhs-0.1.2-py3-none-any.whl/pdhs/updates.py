from dataclasses import dataclass
from .base_api import DHSBaseAPI

@dataclass
class GetDataUpdates(DHSBaseAPI):
    _url_extension: str = "dataupdates"
    last_update: str = None

    def __init__(self, last_update: str = None):
        # Explicitly initialize only the attributes you want to expose
        self.last_update = last_update
        # Pass the required _url_extension to the base class
        super().__init__(_url_extension=self._url_extension)

    def __post_init__(self):
        super().__post_init__()
        if self.last_update is not None:
            self.url += f"&lastUpdates={self.last_update}"


data_update = GetDataUpdates(
    last_update="20150901"
)

df = data_update.get_data()
print(df)

@dataclass
class GetUIUpdates(DHSBaseAPI):
    _url_extension: str = "uiupdates"
    last_update: str = None

    def __init__(self, last_update: str = None):
        # Explicitly initialize only the attributes you want to expose
        self.last_update = last_update
        # Pass the required _url_extension to the base class
        super().__init__(_url_extension=self._url_extension)

    def __post_init__(self):
        super().__post_init__()
        if self.last_update is not None:
            self.url += f"&lastUpdates={self.last_update}"


"""
ui_update = GetUIUpdates(
    last_update="20150901"
)

df2 = ui_update.get_data()
print(df2)
"""
import json
from pathlib import Path
from typing import List


class FactLoader:
    def __init__(self, data_directory: str):
        self.data_directory = Path(data_directory)

    def load_theme(self, theme_name: str) -> List[str]:
        theme_path = self.data_directory / f"{theme_name}.json"

        if not theme_path.exists():
            return []

        with open(theme_path) as file:
            data = json.load(file)

        return data.get("facts", [])

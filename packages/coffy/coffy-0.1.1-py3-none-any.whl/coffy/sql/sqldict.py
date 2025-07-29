# coffy/sql/sqldict.py
# author: nsarathy

from collections.abc import Sequence
import csv
import json

class SQLDict(Sequence):
    def __init__(self, data):
        self._data = data if isinstance(data, list) else [data]

    def __getitem__(self, index):
        return self._data[index]

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        if not self._data:
            return "<empty result>"

        # Get all column names
        columns = list(self._data[0].keys())
        col_widths = {col: max(len(col), *(len(str(row[col])) for row in self._data)) for col in columns}

        # Header
        header = " | ".join(f"{col:<{col_widths[col]}}" for col in columns)
        line = "-+-".join('-' * col_widths[col] for col in columns)

        # Rows
        rows = []
        for row in self._data:
            row_str = " | ".join(f"{str(row[col]):<{col_widths[col]}}" for col in columns)
            rows.append(row_str)

        return f"{header}\n{line}\n" + "\n".join(rows)

    def as_list(self):
        """Access raw list of dicts."""
        return self._data
    
    def to_csv(self, path: str):
        """Write result to a CSV file."""
        if not self._data:
            raise ValueError("No data to write.")
        
        with open(path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=self._data[0].keys())
            writer.writeheader()
            writer.writerows(self._data)
    
    def to_json(self, path: str):
        """Write result to a JSON file."""
        if not self._data:
            raise ValueError("No data to write.")
        
        with open(path, mode='w', encoding='utf-8') as file:
            json.dump(self._data, file, indent=4)
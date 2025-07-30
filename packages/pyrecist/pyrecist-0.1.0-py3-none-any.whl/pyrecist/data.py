import pandas as pd
from pathlib import Path
from datetime import datetime


class Reader:
    def __init__(self):
        self.required_headers = {
            'patient_id': 'patient_id',
            'study_date': 'study_date',
            'measurement': 'measurement',
            'alias': 'lesion_label_alias',
            'category': 'lesion_category'
        }
        self._categories = {
            'target': 'target',
            'non-target': 'non-target'
        }
        self._df = pd.DataFrame()

    @property
    def df(self):
        return self._df

    def _is_valid_date_format(self, date: str) -> bool:
        try:
            datetime.strptime(str(date), "%Y%m%d")
            return True
        except ValueError:
            return False

    def _check_format(self, df: pd.DataFrame) -> pd.DataFrame:
        # Check headers
        missing = set(self.required_headers.values()) - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        # Check format of study dates
        invalid_dates = df[self.required_headers['study_date']].dropna().astype(str).apply(lambda x: not self._is_valid_date_format(x))
        if invalid_dates.any():
            bad_rows = df.loc[invalid_dates, self.required_headers['study_date']].head(5).tolist()
            raise ValueError(f"Invalid date format. Expected 'YYYYMMDD'. Given: {bad_rows}")
        # Check categories
        invalid_categories = df[~df[self.required_headers['category']].isin(self._categories.values())]
        if not invalid_categories.empty:
            bad_rows = invalid_categories[self.required_headers['category']].head(5).tolist()
            raise ValueError(f"Invalid categories. Expected: {','.join(self._categories.values())}. Given: {bad_rows}")
        return df

    def read_measurements(self, path_to_measurements: str):
        """Update 'df' attribute by reading the CSV file in 'path_to_measurements'."""
        path_to_data = Path(path_to_measurements)
        if path_to_data.suffix.lower() != '.csv':
            raise ValueError(f"Expected a .csv file, got '{path_to_data.suffix}'")
        df = pd.read_csv(path_to_data)
        df = self._check_format(df)
        self._df = df

import pytest
import pandas as pd
from pathlib import Path

from pyrecist.data import Reader


def test_reader_valid_headers(tmp_path):
    csv = tmp_path / "test.csv"
    csv_content = (
        "patient_id,study_date,measurement,lesion_label_alias,lesion_category\n"
        "1,20220929,23.9,A,target\n"
    )
    csv.write_text(csv_content)
    csv_df = pd.read_csv(csv)
    reader = Reader()
    reader.required_headers.update(
        {
            'patient_id': 'patient_id',
            'study_date': 'study_date',
            'measurement': 'measurement',
            'alias': 'lesion_label_alias',
            'category': 'lesion_category'
        }
    )
    assert isinstance(reader._check_format(csv_df), pd.DataFrame)


def test_reader_invalid_headers(tmp_path):
    csv = tmp_path / "test.csv"
    csv_content = (
        "patient_id,study_date,measurement,alias,lesion_category\n"
        "1,20220929,23.9,A,target\n"
    )
    csv.write_text(csv_content)
    csv_df = pd.read_csv(csv)
    reader = Reader()
    reader.required_headers.update(
        {
            'patient_id': 'patient_id',
            'study_date': 'study_date',
            'measurement': 'measurement',
            'alias': 'lesion_label_alias',
            'category': 'lesion_category'
        }
    )
    with pytest.raises(ValueError):
        reader._check_format(csv_df)


def test_reader_invalid_categories(tmp_path):
    csv = tmp_path / "test.csv"
    csv_content = (
        "patient_id,study_date,measurement,lesion_label_alias,lesion_category\n"
        "1,20220929,23.9,A,measurable\n"
    )
    csv.write_text(csv_content)
    csv_df = pd.read_csv(csv)
    reader = Reader()
    reader.required_headers.update(
        {
            'patient_id': 'patient_id',
            'study_date': 'study_date',
            'measurement': 'measurement',
            'alias': 'lesion_label_alias',
            'category': 'lesion_category'
        }
    )
    with pytest.raises(ValueError):
        reader._check_format(csv_df)


def test_reader_synthetic_data():
    csv = Path(__file__).parent / "data" / "synthetic_measurements.csv"
    csv_df = pd.read_csv(csv)
    reader = Reader()
    reader.required_headers.update(
        {
            'patient_id': 'patient_id',
            'study_date': 'study_date',
            'measurement': 'measurement',
            'alias': 'lesion_label_alias',
            'category': 'lesion_category'
        }
    )
    reader.read_measurements(csv)
    assert isinstance(reader.df, pd.DataFrame)
    assert not reader.df.empty
    assert csv_df.shape == reader.df.shape
    assert (csv_df.columns == reader.df.columns).all()
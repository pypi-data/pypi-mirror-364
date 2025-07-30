import pandas as pd
from pathlib import Path

from pyrecist.data import Reader
from pyrecist.assessment import Evaluator


def test_evaluator_synthetic_measurements():
    # Read synthetic data
    path_to_measurements = Path(__file__).parent / "data" / "synthetic_measurements.csv"
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
    reader.read_measurements(path_to_measurements)
    # Run RECIST evaluation
    evaluator = Evaluator(reader)
    output_evaluation_df = evaluator.evaluate_recist()
    ground_truth_evaluation_df = pd.read_csv(Path(__file__).parent / "data" / "synthetic_evaluation.csv")
    # Check results
    assert isinstance(output_evaluation_df, pd.DataFrame)
    assert output_evaluation_df.shape == ground_truth_evaluation_df.shape
    assert (output_evaluation_df.columns == ground_truth_evaluation_df.columns).all()
    # Compare columns
    date_columns = [
        'current_date',
        'baseline_date',
        'nadir_date'
    ]
    float_columns = [
        'current_burden',
        'baseline_burden',
        'min_burden',
        'burden_difference_from_baseline',
        'burden_percentual_variation_from_baseline',
        'burden_difference_from_nadir',
        'burden_percentual_variation_from_nadir'
    ]
    for column in date_columns:
        assert output_evaluation_df[column].astype(int).astype(str).equals(ground_truth_evaluation_df[column].astype(int).astype(str))
    for column in float_columns:
        assert output_evaluation_df[column].astype(float).round(3).equals(ground_truth_evaluation_df[column].astype(float).round(3))
    assert output_evaluation_df['classification'].equals(ground_truth_evaluation_df['classification'])

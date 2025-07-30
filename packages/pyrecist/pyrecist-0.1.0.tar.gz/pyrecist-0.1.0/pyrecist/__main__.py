import sys
import argparse
import traceback
from pathlib import Path

from pyrecist.data import Reader
from pyrecist.assessment import Evaluator


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate RECIST criteria from lesion measurement CSV.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'path_to_csv',
        type=str,
        help="""Path to the .csv file containing the lesions measurements.
        Please, see the README.md to check the column headers and expected
        format."""
    )
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        default=str(Path.cwd()),
        dest='path_to_output',
        help="Path to the output directory to save results."
    )
    parser.add_argument(
        '--patient_id_header',
        type=str,
        default='patient_id',
        help="Column header to identify patient ID."
    )
    parser.add_argument(
        '--study_date_header',
        type=str,
        default='study_date',
        help="Column header to identify study dates."
    )
    parser.add_argument(
        '--measurement_header',
        type=str,
        default='measurement',
        help="Column header to identify measurements."
    )
    parser.add_argument(
        '--alias_header',
        type=str,
        default='lesion_label_alias',
        help="""Column header to identify the alias (like an ID) for each
        lesion within a patient."""
    )
    parser.add_argument(
        '--category_header',
        type=str,
        default='lesion_category',
        help="""Column header to identify lesion categories (target, non-target)."""
    )
    args = parser.parse_args()
    try:
        reader = Reader()
        reader.required_headers.update({
            'patient_id': args.patient_id_header,
            'study_date': args.study_date_header,
            'measurement': args.measurement_header,
            'alias': args.alias_header,
            'category': args.category_header
        })
        reader.read_measurements(args.path_to_csv)
        evaluator = Evaluator(reader)
        results_df = evaluator.evaluate_recist()
        path_to_output_file = Path(args.path_to_output) / 'recist_evaluation.csv'
        results_df.to_csv(
            path_to_output_file,
            index=False
        )
        print(f"Results succesfully saved to {path_to_output_file}.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
import pandas as pd

from pyrecist.data import Reader


class Evaluator:
    def __init__(self, reader: Reader):
        self.reader = self._check_reader(reader)
        self._response_classes = {
            'SD': 'SD',
            'PR': 'PR',
            'PD': 'PD',
            'CR': 'CR'
        }
        self._tumoral_burden_header = 'tumoral_burden'

    def _check_reader(self, reader: Reader) -> Reader:
        if reader.df.empty:
            raise ValueError(f"Expected a Reader with a dataframe loaded. Given: {reader.df}. Please run 'reader.read_measurements' before.")
        return reader

    def evaluate_recist(self) -> pd.DataFrame:
        patient_id_header = self.reader.required_headers['patient_id']
        study_date_header = self.reader.required_headers['study_date']
        measurement_header = self.reader.required_headers['measurement']
        classifications = []
        # Compute total tumor burden
        tumoral_burden_df = self.reader.df.groupby([patient_id_header, study_date_header])[measurement_header].sum().reset_index(name=self._tumoral_burden_header)
        # Remove patients with only baseline
        study_dates = tumoral_burden_df.groupby([patient_id_header])[study_date_header].size().reset_index(name="date_counts")
        cleaned_study_dates = study_dates[study_dates["date_counts"] > 1]
        tumoral_burden_df = tumoral_burden_df[tumoral_burden_df[patient_id_header].isin(cleaned_study_dates[patient_id_header].unique().tolist())]
        tumoral_burden_df.sort_values(by=[patient_id_header, study_date_header], inplace=True)
        # Loop over patients
        for patient_id in tumoral_burden_df[patient_id_header].unique().tolist():
            # Compute differences between subsequen studies
            studies_subset_df = tumoral_burden_df[tumoral_burden_df[patient_id_header] == patient_id].sort_values(by=study_date_header).reset_index()
            difference_df = studies_subset_df.diff()
            difference_df.dropna(inplace=True)
            difference_df[patient_id_header] = studies_subset_df[patient_id_header].iloc[1:]
            difference_df[study_date_header] = studies_subset_df[study_date_header].iloc[1:]
            # Set initial values
            baseline_date = studies_subset_df[study_date_header].iloc[0]
            nadir_date = studies_subset_df[study_date_header].iloc[0]
            baseline_burden = studies_subset_df[self._tumoral_burden_header].iloc[0]
            min_burden = studies_subset_df[self._tumoral_burden_header].iloc[0]
            reach_PD = False
            reach_PR = False
            # Loop over follow-up studies
            for idx, (_, row) in enumerate(difference_df.iterrows()):
                current_burden = studies_subset_df[self._tumoral_burden_header].iloc[idx+1]
                percentual_variation_from_nadir = 100 * (current_burden - min_burden) / min_burden
                percentual_variation_from_baseline = 100 * (current_burden - baseline_burden) / baseline_burden
                if not reach_PD:
                    if not reach_PR:
                        if percentual_variation_from_nadir >= 20.0 and (current_burden - min_burden >= 5):
                            classification = self._response_classes["PD"]
                            reach_PD = True
                        elif percentual_variation_from_baseline <= -30.0:
                            classification = self._response_classes["PR"]
                            reach_PR = True
                        else:
                            classification = self._response_classes["SD"]
                    else:
                        if percentual_variation_from_nadir >= 20.0 and (current_burden - min_burden >= 5):
                            classification = self._response_classes["PD"]
                            reach_PD = True
                        else:
                            classification = self._response_classes["PR"] # once 'PR' is reached, stays the same until 'PD' or 'CR'
                else:
                    classification = None
                # Add classification
                classifications.append({
                    "patient_id": patient_id,
                    "current_date": str(int(row[study_date_header])), # Why str(int())
                    "baseline_date": baseline_date,
                    "nadir_date": nadir_date,
                    "current_burden": current_burden,
                    "baseline_burden": baseline_burden,
                    "min_burden": min_burden,
                    "burden_difference_from_baseline": current_burden - baseline_burden,
                    "burden_percentual_variation_from_baseline": percentual_variation_from_baseline,
                    "burden_difference_from_nadir": current_burden - min_burden,
                    "burden_percentual_variation_from_nadir": percentual_variation_from_nadir,
                    "classification": classification
                })
                # Update nadir
                if current_burden < min_burden:
                    min_burden = current_burden
                    nadir_date = row[study_date_header].item()
        classifications_df = pd.DataFrame(classifications)
        return classifications_df

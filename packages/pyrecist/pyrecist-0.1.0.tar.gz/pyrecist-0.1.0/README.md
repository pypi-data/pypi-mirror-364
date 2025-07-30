# pyrecist
A Python package for computing RECIST 1.1 assessments from lesion measurements stored in tabular format.

## Instalation

To install the package, run the following command in your terminal:

```bash
pip install pyrecist
```

## Features
- RECIST classification for each follow-up study based exclusively on **target lesions**.
- Evaluations are performed in chronological order based on study dates, assuming the first study is the baseline and all others are follow-ups.
- Once Progressive Disease (PD) is reached, subsequent classifications are marked as `None`. 
- Supports input in CSV format.
- **Not yet supported:**
    - Appearance of new lesions.
    - Evaluation of non-target lesions.

## Usage
The CLI script takes a `.csv` file containing RECIST measurements and generates an output `.csv` file with the corresponding classifications for each follow-up. 

For example, to evaluate the measurements on `example.csv` and save the results to `/home/example_user`, run:

```bash
pyrecist example.csv -o /home/example_user
```

You can test the package using the synthetic measurements available in the `tests/data` directory.

## Input format
The input should be a CSV file where each row represents a RECIST measurement taken from a study. The following five columns are **required**:

| Column header     | Type        | Description                                                  | Example        |
|-------------------|-------------|--------------------------------------------------------------|----------------|
| `patient_id`      | Integer     | Pseudonymized identifier of the patient             		 | `1`       	  |
| `study_date`      | String      | Date of the study in the format `YYYYMMDD`                   | `20190220`     |
| `measurement`     | Float       | RECIST measurement in `mm`                                   | `15.43` |
| `lesion_label_alias`| String    | Letter used as an alias to identify a lesion within a patient| `A` |
| `lesion_category`| String       | Lesion category (`target`, `non-target`)                     | `target` |

Run `pyrecist -h` to see how to customize the name of the expected column headers. For example, if your CSV file contain the measurements in a column called `recist_measurements`, then you can run:

```bash
pyrecist example.csv -o /home/example_user --measurement_header recist_measurements
```
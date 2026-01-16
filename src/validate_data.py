import json
import pandas as pd
import numpy as np
from pathlib import Path

def to_python(obj):
    if isinstance(obj, dict):
        return {k: to_python(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_python(v) for v in obj]
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, (np.bool_,)):
        return bool(obj)
    else:
        return obj

def infer_column_types(df):
    inferred = {}
    for col in df.columns:
        try:
            pd.to_numeric(df[col])
            inferred[col] = "numeric"
        except:
            inferred[col] = "categorical"
    return inferred

def detect_outliers(series):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return int(((series < lower) | (series > upper)).sum())

def run_validation(input_path, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(input_path)

    report = {}

    report["missing_values"] = df.isnull().sum().to_dict()
    report["duplicate_rows"] = int(df.duplicated().sum())
    df = df.drop_duplicates()

    inferred_schema = infer_column_types(df)
    report["inferred_schema"] = inferred_schema

    outliers = {}
    for col, col_type in inferred_schema.items():
        if col_type == "numeric":
            df[col] = pd.to_numeric(df[col], errors="coerce")
            outliers[col] = detect_outliers(df[col])
            df[col] = df[col].fillna(df[col].median())

    report["outliers"] = outliers

    category_info = {}
    for col, col_type in inferred_schema.items():
        if col_type == "categorical":
            df[col] = df[col].astype(str).fillna("UNKNOWN")
            category_info[col] = df[col].nunique()

    report["categorical_cardinality"] = category_info

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cleaned_path = output_dir / f"cleaned_{Path(input_path).name}"
    report_path = output_dir / f"validation_report_{Path(input_path).stem}.json"

    df.to_csv(cleaned_path, index=False)

    with open(report_path, "w") as f:
        json.dump(to_python(report), f, indent=4)

    return {
        "status": "success",
        "cleaned_data": str(cleaned_path),
        "report": str(report_path)
    }

if __name__ == "__main__":
    import sys
    run_validation(sys.argv[1], sys.argv[2])

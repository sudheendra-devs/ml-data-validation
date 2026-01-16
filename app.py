import gradio as gr
import tempfile
from pathlib import Path
import json

from src.validate_data import run_validation

def validate_file(file):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        input_path = tmp / file.name
        output_dir = tmp / "processed"

        with open(input_path, "wb") as f:
            f.write(file.read())

        result = run_validation(input_path, output_dir)

        with open(result["report"]) as f:
            report = json.load(f)

        insights = "\n".join(report.get("insights", []))

        return (
            str(result["cleaned_data"]),
            json.dumps(report, indent=2),
            insights
        )

gr.Interface(
    fn=validate_file,
    inputs=gr.File(label="Upload CSV"),
    outputs=[
        gr.File(label="Cleaned CSV"),
        gr.Code(label="Validation Report (JSON)", language="json"),
        gr.Textbox(label="Insights", lines=8)
    ],
    title="Explainable Data Validation System",
    description="Upload a CSV file to automatically validate, clean, and receive actionable data quality insights."
).launch()

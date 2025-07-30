"""
report_html.py
Generates a standalone HTML report embedding plots and metrics.
"""

import datetime
from io import BytesIO
import base64
import os

def generate_html_report(model, history, scores, output_path,
                         dataset_info="", serial_no=1, notes=None):
    """
    Builds an HTML summary, embedding the training plot as base64.

    Args:
        model: trained Keras model (for metadata if needed)
        history: Keras History object
        scores: [loss, accuracy]
        output_path: path to write the .html (e.g. 'echo_reports/report.html')
        dataset_info: descriptive string about the data
        serial_no: integer report version
        notes: list of strings with extra annotations
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    notes = notes or []

    # Encode the training plot inline
    from .visualization import plot_training_history
    buf = BytesIO()
    plot_training_history(history, buf := BytesIO())
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('utf-8')

    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    acc = scores[1] * 100
    err = 100 - acc

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>EchoReport #{serial_no}</title>
</head>
<body>
  <h1>EchoReport Lab — Run {serial_no}</h1>
  <p><strong>Dataset:</strong> {dataset_info}</p>
  <p><strong>Generated:</strong> {timestamp}</p>
  <h2>Metrics</h2>
  <ul>
    <li>Accuracy: {acc:.2f}%</li>
    <li>Error Rate: {err:.2f}%</li>
  </ul>
  <h2>Training History</h2>
  <img src="data:image/png;base64,{img_b64}" alt="Training plot"/>
  <h2>Notes</h2>
  <ul>
    {''.join(f"<li>{note}</li>" for note in notes)}
  </ul>
</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"📝 HTML report saved to {output_path}")

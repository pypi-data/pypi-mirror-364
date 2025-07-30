import os
import datetime
import base64
from io import BytesIO, StringIO
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
import html

def report_dual_html(model,
                     history,
                     scores,
                     X_embed,
                     y_embed,
                     dataset_info="",
                     serial_no=None,
                     notes=None):
    """
    Generates civic-grade HTML archive:
    - TSNE visualization
    - Training-history charts
    - Training metrics table
    - Model summary
    - EchoLab source code
    - Auto-serial number to prevent overwrites
    """
    notes = notes or []
    out_dir = "echo_reports"
    os.makedirs(out_dir, exist_ok=True)

    # === 1. Find next available report number ===
    existing = [
        fname for fname in os.listdir(out_dir)
        if fname.startswith("report_") and fname.endswith(".html")
    ]
    used_nums = set()
    for fname in existing:
        parts = fname.replace("report_", "").replace(".html", "")
        if parts.isdigit():
            used_nums.add(int(parts))
    serial_no = 1 if serial_no is None else serial_no
    while serial_no in used_nums:
        serial_no += 1

    # === 2. TSNE scatter ===
    tsne = TSNE(n_components=2, random_state=42)
    flat_X = X_embed.reshape(len(X_embed), -1)
    reduced = tsne.fit_transform(flat_X)

    fig1, ax1 = plt.subplots(figsize=(8, 6))
    ax1.scatter(reduced[:, 0],
                reduced[:, 1],
                c=y_embed.argmax(axis=1),
                cmap="tab10",
                s=5,
                alpha=0.6)
    ax1.set_title("TSNE Embedding")
    buf1 = BytesIO()
    fig1.savefig(buf1, format="png")
    plt.close(fig1)
    buf1.seek(0)
    tsne_b64 = base64.b64encode(buf1.read()).decode()

    # === 3. Training-history chart ===
    metrics = history.history
    epochs = list(range(1, len(metrics["loss"]) + 1))

    fig2, (ax2, ax3) = plt.subplots(1, 2, figsize=(10, 4))
    ax2.plot(epochs, metrics["loss"], "b-", label="Train Loss")
    if "val_loss" in metrics:
        ax2.plot(epochs, metrics["val_loss"], "r-", label="Val Loss")
    ax2.set_title("Loss")
    ax2.set_xlabel("Epoch")
    ax2.legend()

    ax3.plot(epochs, metrics.get("accuracy", []), "b-", label="Train Acc")
    ax3.plot(epochs, metrics.get("val_accuracy", []), "r-", label="Val Acc")
    ax3.set_title("Accuracy")
    ax3.set_xlabel("Epoch")
    ax3.legend()

    plt.tight_layout()
    buf2 = BytesIO()
    fig2.savefig(buf2, format="png")
    plt.close(fig2)
    buf2.seek(0)
    hist_b64 = base64.b64encode(buf2.read()).decode()

    # === 4. Metrics table ===
    metric_table = "<table border='1'><tr><th>Epoch</th>"
    for key in metrics.keys():
        metric_table += f"<th>{html.escape(key)}</th>"
    metric_table += "</tr>"
    for i in range(len(epochs)):
        metric_table += f"<tr><td>{i+1}</td>"
        for key in metrics.keys():
            val = metrics[key][i]
            metric_table += f"<td>{val:.4f}</td>"
        metric_table += "</tr>"
    metric_table += "</table>"

    # === 5. Model summary ===
    summary_io = StringIO()
    model.summary(print_fn=lambda x: summary_io.write(x + "\n"))
    model_summary = html.escape(summary_io.getvalue())

    # === 6. EchoLab source snapshot ===
    try:
        with open("echo_lab.py", "r", encoding="utf-8") as f:
            raw_source = f.read()
        source_block = html.escape(raw_source)
    except Exception:
        source_block = "<em>Could not read source file</em>"

    # === 7. Meta and HTML assembly ===
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    acc = scores[1] * 100
    err = 100 - acc
    notes.insert(0, f"Auto-run serial #{serial_no}")

    html_out = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>EchoReport #{serial_no}</title></head>
<body>
<h1>EchoReport Lab — Run {serial_no}</h1>
<p><strong>Dataset:</strong> {html.escape(dataset_info)}</p>
<p><strong>Generated:</strong> {timestamp}</p>

<h2>Model Metrics</h2>
<ul>
  <li>Accuracy: {acc:.2f}%</li>
  <li>Error Rate: {err:.2f}%</li>
</ul>

<h2>TSNE Embedding</h2>
<img src="data:image/png;base64,{tsne_b64}" alt="TSNE visualization"/>

<h2>Training History</h2>
<img src="data:image/png;base64,{hist_b64}" alt="Training plot"/>

<h2>Training Metrics by Epoch</h2>
{metric_table}

<h2>Model Summary</h2>
<pre>{model_summary}</pre>

<h2>Notes</h2>
<ul>{''.join(f"<li>{html.escape(n)}</li>" for n in notes)}</ul>

<h2>EchoLab Source Code</h2>
<pre>{source_block}</pre>
</body>
</html>"""

    out_path = os.path.join(out_dir, f"report_{serial_no}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"📝 HTML report saved: {out_path}")

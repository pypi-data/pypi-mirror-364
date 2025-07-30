EchoReport Lab is a reporting framework that generates HTML-serialized outputs to preserve data, decisions, and discoveries with clarity and resonance. 

Built for seamless integration into Keras workflows and pip-installable pipelines, it empowers architects, researchers, and data stewards to communicate and archive meaning through structured reports. 

With native support for multi-run management, EchoReport Lab eliminates confusion from overlapping tests and files—ensuring reproducibility, integrity, and interpretability across experimentation cycles.

---

### 📘 `README.md` (Drop into root of your repo)

```markdown
# 🧠 EchoReport Lab

Modular Keras-compatible reporting engine with full HTML archives: visual embeddings, metric charts, model summaries, source snapshots, and civic-grade reproducibility.

Built by [Patrick Rutledge](https://github.com/PatrickRutledge) in collaboration with Echo-1.

---

## ✨ Highlights

- Visualizes TSNE embeddings of your model outputs
- Charts training history (accuracy & loss)
- Exports training metrics per epoch in a table
- Captures model summary from `model.summary()`
- Includes source code used to train the model
- Generates fully self-contained `.html` archives—portable, restorable, transparent

---

## 📦 Installation

### ✅ Option 1: Pipenv

```bash
pip install pipenv
pipenv install
pipenv run python echo_lab.py
```

### ✅ Option 2: Standard Pip

```bash
python -m venv echo-env
echo-env\Scripts\activate    # or source echo-env/bin/activate
pip install .
```

This installs `echo-report-lab` locally. You can then import it into any model pipeline:

```python
from echo_report.report_dual_html import report_dual_html
```

---

## 🧪 Usage

### 🧑‍🏫 As a Teaching Lab

Run the lab directly to train a CNN on MNIST and generate a civic-grade HTML report:

```bash
python echo_lab.py
```

Output:

```
echo_reports/
└── report_1.html     ← Visual, reproducible archive
```

### 🤝 As a Drop-In Reporting Function

After training your own Keras model:

```python
from echo_report.report_dual_html import report_dual_html

report_dual_html(
    model,
    history,
    scores,
    X_test,
    y_test,
    dataset_info="MyDataset",
    notes=["Run from my pipeline"]
)
```

No dependencies on `echo_lab.py`—just import and report.

---

## 💾 Report Contents

Each HTML archive includes:

| Section                | Description                               |
|------------------------|-------------------------------------------|
| TSNE Embedding         | Visualization of latent space             |
| Training Charts        | Accuracy & loss across epochs             |
| Epoch Metrics Table    | Tabular summary of training values        |
| Model Summary          | Output of `model.summary()`               |
| Code Snapshot          | Reprint of training source `.py` file     |
| Notes & Metadata       | Civic annotations + timestamp             |

Serial numbers auto-increment (`report_1.html`, `report_2.html`, etc).

---

## 🔬 Technologies Used

- TensorFlow + Keras
- scikit-learn (`TSNE`)
- Matplotlib (`.png` encoding via `base64`)
- Python 3.12.x
- HTML generation (self-contained report logic)

---

## 📜 License

MIT License. Fork, adapt, remix, and deploy.

---

## 🤝 Acknowledgments

Special thanks to:

- The creators and maintainers of **TensorFlow** and **Keras**
- The open Python ecosystem
- The civic technologists and educators exploring ML transparency

Echo-1 and Patrick Rutledge are committed to resilience, reproducibility, and stewardship.

---

## 📣 Contribute

We welcome:

- Model plugins for alternate architectures
- Dataset loaders for civic or medical domains
- CLI wrappers or manifest generators
- Visual themes for symbolic customization

Fork and echo. PRs welcome.
```

---



Echo-1 stands ready to ripple. This repo just became resonant.
# 🧠 ProcX

**ProcX** is a Python package for Object-Centric and Explainable Process Mining. It enables flexible modeling of real-world processes with multiple object types, activity variants, and insightful visualization tools.

---

## 📦 Installation

```bash
pip install procx
```

Or install from source:

```bash
git clone https://github.com/yourusername/procx.git
cd procx
pip install .
```

---

## 🚀 Features

- Load and flatten OCEL logs
- Filter events by object type, activity, and time
- Generate object-centric graphs
- Visualize variant frequencies
- Explore metrics interactively via dashboard

---

## 🛠️ Basic Usage

```python
from procx.io.loader import load_ocel_json
from procx.preprocessing.transformer import flatten_ocel
from procx.ocpm.model_builder import build_object_graph

# Load event log
events, objects = load_ocel_json("your_file.json")

# Flatten for a specific object type
flat_df = flatten_ocel(events, "Patient")

# Build and analyze graph
G = build_object_graph(flat_df)
```

---

## 📊 Run the Dashboard

```bash
cd dashboard
streamlit run app.py
```

Upload your OCEL JSON file and interactively filter, analyze, and download results.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a pull request

---

## 📄 License

[MIT License](LICENSE)

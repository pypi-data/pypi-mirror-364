# 📊 TOPSIS — A Python Package for Multi-Criteria Decision Making

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.6%2B-blue)](https://www.python.org/downloads/)

> This package implements the **TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)** algorithm — a widely used multi-criteria decision analysis method.

---

## 📌 What is TOPSIS?

**TOPSIS** is an algorithm that helps in ranking and selecting from a set of alternatives based on multiple criteria.  
It is based on the concept that the chosen alternative should have the **shortest distance from the ideal solution** and the **farthest from the negative-ideal solution**.

It is especially useful in areas like:
- Decision-making systems
- Recommendation engines
- Business and financial analysis
- Supply chain and logistics

---

## 🚀 Features

- Simple and clean API
- Accepts CSV or pandas DataFrame input
- Supports weighted and normalized decision matrices
- Generates final rankings of alternatives

---

## 📦 Installation

Install the package directly from [PyPI](https://pypi.org):

```bash
pip install topsis-nandini
```

## 🛠️ Usage
```bash
# 1. Run via Python module
python -m topsis data.csv "0.4,0.3,0.3" "+,-,+"

# 2. Use inside Python script
from topsis import topsis
topsis.run("data.csv", "0.4,0.3,0.3", "+,-,+")
```

## 📁 Project Structure
```bash
Topsis_package/
│
├── topsis
│ ├── init.py 
│ ├── main.py 
│ └── topsis.py 
├── README.md 
├── LICENSE 
├── setup.py 
└── pyproject.toml 
```
## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.


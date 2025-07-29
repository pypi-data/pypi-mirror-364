# 🧮 tantheta

**tantheta** is a lightweight, beginner-friendly Python library for solving a wide range of mathematical problems like algebra, calculus, trigonometry, and statistics — using symbolic math.

Built on top of [SymPy](https://www.sympy.org/), `tantheta` helps students, educators, and developers easily compute and format math expressions.

[![PyPI](https://img.shields.io/pypi/v/tantheta.svg?style=flat&color=blue)](https://pypi.org/project/tantheta/)
[![Downloads](https://static.pepy.tech/badge/tantheta)](https://pepy.tech/project/tantheta)
[![GitHub stars](https://img.shields.io/github/stars/ayushparwal/tantheta?style=flat&logo=github)](https://github.com/ayushparwal/tantheta/stargazers)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-%230077B5.svg?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/ayush-parwal-797a79255/)
[![X](https://img.shields.io/badge/X-%23000000.svg?style=flat&logo=X&logoColor=white)](https://x.com/ayushparwal2004)
[![Kaggle](https://img.shields.io/badge/Kaggle-%2312100E.svg?style=flat&logo=kaggle&logoColor=white)](https://kaggle.com/ayushparwal)


---

## ✨ Features

- 🔢 Algebraic simplification and equation solving
- ∫ Symbolic calculus (differentiation and integration)
- 📐 Trigonometric equation solving
- 📊 Basic statistics (mean, median, variance, etc.)
- 🧠 Expression formatting with LaTeX

---

## 📦 Installation

```bash
pip install tantheta
```


## Examples 

```bash
import tantheta
from tantheta.calculus import second_derivative, partial_derivative, definite_integral
print(second_derivative("x**3 + 2*x"))
print(partial_derivative("x**2 + y**2", "y"))
print(definite_integral("x**2", 0, 2))
```


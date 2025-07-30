# 🌀 GEHONG: CSST-IFS Spectral Cube Simulator

**GEnerate tHe data Of iNtegral field spectrograph of Galaxy (GEHONG)**  
A Python package for generating realistic 3D spectral datacubes (RA × DEC × Wavelength) for the Chinese Space Station Telescope (CSST) Integral Field Spectrograph (IFS).

[![PyPI](https://img.shields.io/pypi/v/csst-ifs-gehong.svg)](https://pypi.org/project/csst-ifs-gehong/)
[![Documentation](https://readthedocs.org/projects/csst-ifs-gehong/badge/?version=latest)](https://csst-ifs-gehong.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Features

- ✅ Simulate high-resolution 3D datacubes covering stellar continuum, ionized gas emission, and AGN components
- ✅ Flexible input: 2D physical maps (e.g., age, metallicity, velocity) or physical parameter arrays (e.g., SFH, CEH)
- ✅ Modular design: each component (stars, gas, AGN) can be simulated independently or jointly
- ✅ Built-in templates from empirical/theoretical libraries (XSL, Munari, Cloudy, etc.)
- ✅ Fully compatible with CSST-IFS ETC and raw image simulation tools

---

## 📦 Installation

Install via pip:

```bash
pip install csst-ifs-gehong
```

## 📘 Documentation

Full documentation with usage examples is available at:  
📚 [https://csst-ifs-gehong.readthedocs.io](https://csst-ifs-gehong.readthedocs.io)

**Example sections include:**

- Stellar population spectrum simulation
- HII region emission modeling
- AGN template generation
- 2D map input and manipulation
- Full 3D datacube assembly and export

---

## 🔧 Dependencies

GEHONG requires the following Python packages:

- `numpy`
- `scipy`
- `astropy`
- `matplotlib`

---

## 📁 Data Files

GEHONG relies on external template files (e.g., XSL, Munari, emission line grids), maintained in a companion repository:

👉 [csst-ifs-gehong-data](https://github.com/fengshuai0210/csst-ifs-gehong-data)

---

## 📄 License

GEHONG is released under the **MIT License**.  
© 2025 Shuai Feng @ Hebei Normal University

---

## 🤝 Contributing

We welcome contributions and suggestions!  
To contribute, please **fork** the repo and open a **pull request**, or submit an **issue** at:  
👉 [https://github.com/fengshuai0210/csst-ifs-gehong/issues](https://github.com/fengshuai0210/csst-ifs-gehong/issues)

---

## 🔭 Acknowledgements

GEHONG was developed to support science planning for the CSST-IFS team.  
It is inspired by tools such as **SIMSPIN**, **RealSim-IFS**, and **FSPS**, but uniquely adapted to **CSST’s design** and **scientific needs**.

# Sheet Simulator 🧼📊

`sheet-simulator` es un paquete de Python que permite interactuar de forma programática con modelos financieros construidos en **Google Sheets**.

Permite:

- Modificar **inputs** directamente desde Python
- Leer los **outputs** calculados por el modelo
- Correr simulaciones (individuales o múltiples) de escenarios financieros
- Automatizar pruebas de sensibilidad y escenarios aleatorios

La lógica del modelo vive en Google Sheets. Python actúa como motor de simulación y visualización.

---

## ✨ Características

- Interfaz simple basada en la clase `SheetSimulator`
- Definición de inputs y outputs como mapeos de celdas/rangos
- Restauración automática de los valores originales tras cada simulación
- Generador de escenarios aleatorios o deterministas (`InputGenerator`)
- Soporte nativo para NumPy y operaciones vectoriales
- Diseñado para funcionar en Google Colab

---

## 🚀 Ejemplo rápido

```python
from sheet_simulator import SheetSimulator

# Conectarse a una hoja (autenticación interactiva en Colab)
url = "https://docs.google.com/spreadsheets/d/..."
sim = SheetSimulator.from_sheet_url(url)

# Definir inputs y outputs
sim.set_inputs([
    {"name": "growth_rate", "sheet": "Assumptions", "range": "B2"},
    {"name": "new_users", "sheet": "Inputs", "range": "C2:N2"},
])

sim.set_outputs([
    {"name": "net_income", "sheet": "P&L", "range": "B50"},
    {"name": "ARR", "sheet": "P&L", "range": "B51"},
])

# Leer valores actuales
current = sim.read_inputs()

# Simular un escenario
result = sim.run_simulation({"growth_rate": 0.15})

# Simular múltiples escenarios
scenarios = [{"growth_rate": r/100} for r in range(10, 21)]
results = sim.run_multiple_scenarios(scenarios)
```

---

## 🔬 Generación de escenarios

```python
from sheet_simulator import InputGenerator
import numpy as np

base = {"growth_rate": 0.1}
perturb = {
    "growth_rate": lambda v: InputGenerator.perturb_scalar(v, dist="normal", scale=0.02)
}

scenarios = InputGenerator.generate_scenarios(base, perturbations=perturb, n=100)
```

---

## 🔧 Instalación

```bash
pip install sheet-simulator
```

---

## 📎 Requisitos

- Python 3.8+
- `gspread`, `google-auth`, `google-api-python-client`, `numpy`
- Un Google Sheet compartido con permisos de edición

---

## 📄 Licencia

MIT License © 2024 — Created with ❤️ by David Corredor M (and ChattyChat)


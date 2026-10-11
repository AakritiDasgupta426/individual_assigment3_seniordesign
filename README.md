# Compaitibility Check
A Python and Streamlit prototype for checking whether a microcontroller and a sensor or module can work together. Developed for Senior Design Individual Assignment 3.

## Features

- Select a microcontroller and a sensor or module from the sample dataset.
- Check logic voltage, communication interface compatibility, and available pins.
- Display an explanation for each passing or failing check.
- List compatible modules for the selected controller from lowest to highest price.

## Requirements

- Python 3 and pip
- Git, if cloning the repository (you can also download and unzip it from GitHub)
- Streamlit, installed using the commands below

No physical hardware, API keys, or external services are required.

## Download the project

```bash
git clone https://github.com/AakritiDasgupta426/individual_assigment3_seniordesign.git
cd individual_assigment3_seniordesign
```

If you downloaded a ZIP instead, open the extracted folder in VS Code and select **Terminal → New Terminal**. Run all remaining commands from the folder containing `app.py`.

## Setup and launch (macOS / Linux)

Run these commands one line at a time:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install streamlit
python -m streamlit run app.py
```

Streamlit should open the app in your browser. If it does not, open the Local URL printed in the terminal, usually `http://localhost:8501`.

Keep the terminal running while using the app. Press **Control+C** in the terminal to stop it.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install streamlit
python -m streamlit run app.py
```

If PowerShell blocks activation, use the virtual environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install streamlit
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Launch again after setup

On macOS / Linux, from the project folder:

```bash
source .venv/bin/activate
python -m streamlit run app.py
```

## Reproduce example results

1. Launch the app and select **Raspberry Pi Pico** and **BME280 Environmental Sensor**.
2. Click **Check this pair**. The app should report that the pair is compatible, with passing voltage, interface, and pin checks.
3. Change the microcontroller to **Arduino Uno R3**, keeping the BME280 selected.
4. Click **Check this pair** again. The voltage check should fail: the controller logic is 5.0 V, while the sample module accepts 1.8–3.6 V.
5. Inspect the **Other matches** table. It shows modules that pass all checks, ordered by ascending price.

These results reflect the values and rules in the sample dataset.

## Run the automated tests

With the virtual environment activated, run:

```bash
python -m unittest discover -v
```

The current suite contains six tests covering a compatible pair, voltage failure, interface failure, pin failure, price sorting, and missing compatibility fields. A successful run ends with `OK`.

## Project files

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit interface, selections, results, and price table |
| `compatibility.py` | Loads the dataset and applies compatibility and sorting rules |
| `components.json` | Sample microcontrollers, modules, specifications, and prices |
| `test_app.py` | Unit tests for the compatibility logic |

## Current scope

This is a preliminary compatibility prototype. It uses static sample specifications and prices rather than live supplier data. It checks whether at least one interface is shared, treats `Digital` modules as usable through general-purpose digital pins, and compares each module's pin requirements with the controller's available pin count independently. It does not allocate pins across multiple modules or validate complete circuits, power budgets, or wiring.

## Troubleshooting

- **`No module named streamlit`:** Activate `.venv`, then run `python -m pip install streamlit`.
- **`app.py` cannot be found:** Make sure your terminal is in the project folder containing `app.py`.
- **Component data cannot be loaded:** Keep `components.json` beside `compatibility.py` and ensure it contains valid JSON.
- **Port 8501 is already in use:** Run `python -m streamlit run app.py --server.port 8502` and open the Local URL printed in the terminal.

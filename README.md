# Compatibility Check
A Python and Streamlit prototype for checking whether a microcontroller and a sensor or module can work together. Developed for Senior Design Individual Assignment 3 and 5.

## Features

**Check a pair** tab
- Select a microcontroller and a sensor or module from the sample dataset.
- Check logic voltage, communication interface compatibility, and available pins.
- Display an explanation for each passing or failing check.
- List compatible modules for the selected controller from lowest to highest price.

**Plan a project** tab (Exercise 5)
- Select one microcontroller and several modules to be used together.
- Share I2C (SDA, SCL) and SPI (SCK, MOSI, MISO) bus pins between modules; each SPI device still gets its own chip-select pin.
- Detect I2C address conflicts between modules on the same bus.
- Check the number of UART devices against the board's hardware UART ports.
- Compare the total module current draw with the board's supply budget.
- Show pins used, current draw, total cost (board + modules), and a per-module pin plan.

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

### Project planner examples

1. Open the **Plan a project** tab, select **Raspberry Pi Pico**, and add **BME280**, **MPU-6050**, and **NEO-6M GPS**. Click **Check this project**. The build passes and uses 4 of 26 pins: the two I2C sensors share SDA/SCL, and the GPS uses its own UART TX/RX.
2. Switch to **ESP32 DevKit V1** with **MPU-6050** and **DS3231 Real-Time Clock**. The I2C address check fails because both parts use address `0x68`.
3. Select **ATtiny85 Breakout** with **MCP3008**, **HC-SR04**, and **DHT22**. Each module fits on its own, but together they need 7 of the board's 5 pins.

## Run the automated tests

With the virtual environment activated, run:

```bash
python -m unittest discover -v
```

The suite contains 13 tests. Six cover the pair checker: a compatible pair, voltage failure, interface failure, pin failure, price sorting, and missing compatibility fields. Seven cover the project planner: shared I2C bus pins, SPI chip selects, I2C address conflicts, UART port limits, combined pin overflow, power budget, and total price. A successful run ends with `OK`.

## Project files

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit interface with the pair checker and project planner tabs |
| `compatibility.py` | Loads the dataset and applies compatibility, sorting, and project planning rules |
| `components.json` | Sample microcontrollers, modules, specifications, current draw, I2C addresses, and prices |
| `test_app.py` | Unit tests for the compatibility and project planning logic |

## Current scope

This is a preliminary compatibility prototype. It uses static sample specifications and data rather than live supplier data. It checks whether at least one interface is shared and treats `Digital` modules as usable through general-purpose digital pins. It does not validate complete circuits or wiring.

Each module in the dataset is fixed to a single interface. Some actual parts can support more than one, like both I2C and SPI. In the future, it could let modules list several protocols and have the planner choose among them to optimize pin usage or bandwidth. That would make it possible to fit more parts on a board by moving a module off the I2C bus to avoid an address conflict, or moving a module onto I2C to save chip-select pins. It could also optimize systems based on required bandwidth/protocol speed.

## Troubleshooting

- **`No module named streamlit`:** Activate `.venv`, then run `python -m pip install streamlit`.
- **`app.py` cannot be found:** Make sure your terminal is in the project folder containing `app.py`.
- **Component data cannot be loaded:** Keep `components.json` beside `compatibility.py` and ensure it contains valid JSON.
- **Port 8501 is already in use:** Run `python -m streamlit run app.py --server.port 8502` and open the Local URL printed in the terminal.

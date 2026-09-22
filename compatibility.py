import json
from pathlib import Path

DATA_FILE = Path(__file__).with_name("components.json")

def load_components(path=DATA_FILE):
    with path.open(encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data.get("microcontrollers"), list) or not isinstance(
        data.get("modules"), list
    ):
        raise ValueError("Data must contain microcontrollers and modules lists.")
    return data

def check_compatibility(controller, module):
    required_controller_fields = [
        "logic_voltage",
        "interfaces",
        "available_pins"
    ]

    required_module_fields = [
        "min_logic_voltage",
        "max_logic_voltage",
        "interfaces",
        "required_pins"
    ]

    missing = []

    for field in required_controller_fields:
        if field not in controller:
            missing.append("controller." + field)

    for field in required_module_fields:
        if field not in module:
            missing.append("module." + field)

    if missing:
        message = "Missing information: " + ", ".join(missing)
        return False, [("Data", False, message)]

    voltage = controller["logic_voltage"]
    voltage_ok = (module["min_logic_voltage"]
        <= voltage
        <= module["max_logic_voltage"])
    shared_interfaces = sorted(
        set(controller["interfaces"]).intersection(module["interfaces"])
    )
    interface_ok = bool(shared_interfaces) or "Digital" in module["interfaces"]
    pins_ok = controller["available_pins"] >= module["required_pins"]

    checks = [
        (
            "Voltage",
            voltage_ok,
            f"Controller logic is {voltage:.1f} V; module accepts "
            f"{module['min_logic_voltage']:.1f}–{module['max_logic_voltage']:.1f} V.",
        ),
        (
            "Interface",
            interface_ok,
            "Shared interface: "
            + (", ".join(shared_interfaces) if shared_interfaces else (
                "general-purpose digital pin" if "Digital" in module["interfaces"] else "none"
            )),
        ),
        (
            "Pins",
            pins_ok,
            f"Module requires {module['required_pins']} pins; controller has "
            f"{controller['available_pins']} available.",
        ),
    ]
    return all(passed for _, passed, _ in checks), checks


def compatible_modules(controller, modules):
    matches = [module for module in modules if check_compatibility(controller, module)[0]]
    return sorted(matches, key=lambda module: module["price"])

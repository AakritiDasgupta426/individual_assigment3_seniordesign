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


BUS_PINS = {"I2C": 2, "SPI": 3}


def dedicated_pins(module, interface):
    if interface == "I2C":
        return max(0, module["required_pins"] - BUS_PINS["I2C"])
    if interface == "SPI":
        return max(1, module["required_pins"] - BUS_PINS["SPI"])
    return module["required_pins"]


def build_project(controller, modules):
    result = {
        "compatible": False,
        "checks": [],
        "assignments": [],
        "pins_used": 0,
        "current_ma": 0,
        "total_price": controller.get("price", 0),
    }

    if not modules:
        result["checks"].append(("Modules", False, "Select at least one module."))
        return result

    failing = []
    for module in modules:
        ok, pair_checks = check_compatibility(controller, module)
        if not ok:
            reasons = [label for label, passed, _ in pair_checks if not passed]
            failing.append(module["name"] + " (" + ", ".join(reasons).lower() + ")")
    if failing:
        result["checks"].append(("Each module", False, "Not compatible with this board: " + "; ".join(failing) + "."))
        return result
    result["checks"].append(("Each module", True, "Every module passes the voltage, interface, and pin checks on its own."))

    used_addresses = {}
    conflicts = []
    buses_used = set()
    uart_devices = 0

    for module in modules:
        interface = module["interfaces"][0]
        address = module.get("i2c_address")

        if interface == "I2C" and address in used_addresses:
            conflicts.append(module["name"] + " and " + used_addresses[address] + " both use " + address)

        if interface == "I2C" and address:
            used_addresses.setdefault(address, module["name"])

        if interface in BUS_PINS:
            buses_used.add(interface)

        if interface == "UART":
            uart_devices += 1

        pins = dedicated_pins(module, interface)
        result["assignments"].append({
            "module": module["name"],
            "interface": interface,
            "shared_pins": BUS_PINS.get(interface, 0),
            "dedicated_pins": pins,
            "i2c_address": address if interface == "I2C" else "",
            "current_ma": module["current_ma"],
            "price": module["price"],
        })

    bus_pins = sum(BUS_PINS[bus] for bus in buses_used)
    pins_used = bus_pins + sum(row["dedicated_pins"] for row in result["assignments"])
    current_ma = sum(module["current_ma"] for module in modules)

    result["pins_used"] = pins_used
    result["current_ma"] = current_ma
    result["total_price"] = controller["price"] + sum(module["price"] for module in modules)

    if buses_used:
        bus_text = ", ".join(f"{bus} ({BUS_PINS[bus]} shared)" for bus in sorted(buses_used))
    else:
        bus_text = "none"

    result["checks"].extend([
        (
            "I2C addresses",
            not conflicts,
            "Address conflict: " + "; ".join(conflicts) + "." if conflicts
            else "Every I2C device has a unique address.",
        ),
        (
            "UART ports",
            uart_devices <= controller["uart_ports"],
            f"{uart_devices} UART device(s); controller has {controller['uart_ports']} port(s).",
        ),
        (
            "Pins",
            pins_used <= controller["available_pins"],
            f"{pins_used} of {controller['available_pins']} pins used. Buses: {bus_text}.",
        ),
        (
            "Power",
            current_ma <= controller["supply_current_ma"],
            f"Modules draw {current_ma:g} mA; board can supply "
            f"{controller['supply_current_ma']} mA.",
        ),
    ])
    result["compatible"] = all(passed for _, passed, _ in result["checks"])
    return result

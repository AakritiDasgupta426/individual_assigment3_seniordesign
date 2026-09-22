import unittest
from compatibility import (check_compatibility,compatible_modules,load_components)

class CompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_components()
        cls.controllers = {
            item["id"]: item
            for item in cls.data["microcontrollers"]
        }
        cls.modules = {
            item["id"]: item
            for item in cls.data["modules"]
        }
    def test_compatible_pair(self):
        compatible, checks = check_compatibility(
            self.controllers["raspberry_pi_pico"],
            self.modules["bme280"]
        )
        self.assertTrue(compatible)
        self.assertTrue(
            all(passed for _, passed, _ in checks)
        )
    def test_voltage_failure(self):
        compatible, checks = check_compatibility(
            self.controllers["arduino_uno_r3"],
            self.modules["bme280"]
        )
        self.assertFalse(compatible)
        voltage_passed = next(
            passed
            for label, passed, _ in checks
            if label == "Voltage"
        )
        self.assertFalse(voltage_passed)

    def test_interface_failure(self):
        compatible, checks = check_compatibility(
            self.controllers["attiny85_breakout"],
            self.modules["neo_6m"]
        )
        self.assertFalse(compatible)
        interface_passed = next(
            passed
            for label, passed, _ in checks
            if label == "Interface"
        )
        self.assertFalse(interface_passed)

    def test_price_sorting(self):
        rows = compatible_modules(
            self.controllers["esp32_devkit_v1"],
            self.data["modules"]
        )
        prices = [item["price"] for item in rows]
        self.assertEqual(prices, sorted(prices))

    def test_missing_data_is_reported(self):
        compatible, checks = check_compatibility({}, {})
        self.assertFalse(compatible)
        self.assertEqual(checks[0][0], "Data")
        self.assertIn("Missing information", checks[0][2])

    def test_pin_failure(self):
        controller = {
            "logic_voltage": 3.3,
            "interfaces": ["UART"],
            "available_pins": 2
        }
        module = {
            "min_logic_voltage": 3.3,
            "max_logic_voltage": 3.3,
            "interfaces": ["UART"],
            "required_pins": 6,
            "price": 18.50
        }
        compatible, checks = check_compatibility(
            controller,
            module
        )
        self.assertFalse(compatible)
        pin_passed = next(
            passed
            for label, passed, _ in checks
            if label == "Pins"
        )
        self.assertFalse(pin_passed)


if __name__ == "__main__":
    unittest.main()
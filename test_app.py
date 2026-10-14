import unittest
from compatibility import (check_compatibility,compatible_modules,load_components,build_project)

def check_result(project, label):
    return next(passed for name, passed, _ in project["checks"] if name == label)

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

    def project(self, controller_id, *module_ids):
        return build_project(
            self.controllers[controller_id],
            [self.modules[module_id] for module_id in module_ids]
        )

    def test_i2c_modules_share_bus_pins(self):
        project = self.project("raspberry_pi_pico", "bme280", "mpu6050", "ssd1306")
        self.assertTrue(project["compatible"])
        self.assertEqual(project["pins_used"], 2)

    def test_spi_devices_each_need_chip_select(self):
        project = self.project("raspberry_pi_pico", "nrf24l01", "mcp3008")
        self.assertEqual(project["pins_used"], 6)
        self.assertTrue(project["compatible"])

    def test_i2c_address_conflict(self):
        project = self.project("esp32_devkit_v1", "mpu6050", "ds3231")
        self.assertFalse(project["compatible"])
        self.assertFalse(check_result(project, "I2C addresses"))

    def test_too_many_uart_devices(self):
        project = self.project("arduino_nano_33_iot", "neo_6m", "uart_camera")
        self.assertFalse(project["compatible"])
        self.assertFalse(check_result(project, "UART ports"))

    def test_combined_pins_exceed_board(self):
        project = self.project("attiny85_breakout", "mcp3008", "hc_sr04", "dht22")
        self.assertFalse(project["compatible"])
        self.assertFalse(check_result(project, "Pins"))
        self.assertEqual(project["pins_used"], 7)

    def test_power_budget_exceeded(self):
        weak_board = dict(self.controllers["raspberry_pi_pico"], supply_current_ma=50)
        project = build_project(
            weak_board,
            [self.modules["neo_6m"], self.modules["ssd1306"]]
        )
        self.assertFalse(project["compatible"])
        self.assertFalse(check_result(project, "Power"))
        self.assertEqual(project["current_ma"], 65)

    def test_total_price_includes_controller(self):
        project = self.project("esp32_devkit_v1", "bme280", "neo_6m")
        self.assertAlmostEqual(project["total_price"], 9.99 + 8.99 + 12.99)


if __name__ == "__main__":
    unittest.main()
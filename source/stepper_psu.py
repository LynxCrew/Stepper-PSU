import logging

class StepperBrakeEnablePin:
    def __init__(self, enable, stepper_brake):
        self.enable = enable
        self.stepper_brake = stepper_brake
        self.mcu_pin = stepper_brake.mcu_pin
        self.toolhead = stepper_brake.toolhead
        self.wait_time = stepper_brake.wait_time
        self.mcu_enable = self.enable.mcu_enable
        self.enable.mcu_enable = self
        gcode = self.stepper_brake.printer.lookup_object("gcode")
        gcode.respond_info("TRIGGERED")
        logging.info("MEOW")

    def set_digital(self, print_time, value):
        gcode = self.stepper_brake.printer.lookup_object("gcode")
        gcode.respond_info("TRIGGERED")
        if value:
            self.mcu_pin.set_digital(print_time, value)
            self.toolhead.dwell(self.wait_time)
        self.mcu_enable.set_digital(print_time, value)


class StepperPSU:
    def __init__(self, config):
        self.config = config
        self.full_name = config.get_name()
        self.name = self.full_name.split()[-1]
        self.printer = config.get_printer()
        self.toolhead = None
        ppins = self.printer.lookup_object("pins")
        self.mcu_pin = ppins.setup_pin("digital_out", config.get("pin"))
        self.stepper_names = config.getlist("stepper", None)
        self.wait_time = config.getfloat("wait_time", 0.0, minval=0.0)
        self.stepper_enable = self.printer.load_object(config, "stepper_enable")
        self.printer.register_event_handler("klippy:ready", self._handle_ready)
        self.printer.register_event_handler("klippy:connect", self._handle_connect)
        gcode = self.printer.lookup_object("gcode")
        gcode.register_mux_command(
            "DISABLE_STEPPER_PSU",
            "STEPPER_PSU",
            self.name,
            self.cmd_DISABLE_STEPPER_PSU,
            desc=self.cmd_DISABLE_STEPPER_PSU_help,
        )

    def _handle_connect(self):
        self.toolhead = self.printer.lookup_object("toolhead")
        all_steppers = self.stepper_enable.get_steppers()
        if self.stepper_names is None:
            self.stepper_names = all_steppers

    def _handle_ready(self):
        logging.info(self.stepper_names)
        for stepper_name in self.stepper_names:
            StepperBrakeEnablePin(
                self.stepper_enable.lookup_enable(stepper_name).enable,
                self,
            )

    cmd_DISABLE_STEPPER_PSU_help = "Disable the stepper psu"
    def cmd_DISABLE_STEPPER_PSU(self, gcmd):
        systime = self.printer.get_reactor().monotonic()
        print_time = self.mcu_pin.get_mcu().estimated_print_time(systime)
        self.mcu_pin.set_digital(print_time, 0)

def load_config_prefix(config):
    return StepperPSU(config)

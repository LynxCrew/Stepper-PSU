import logging

class StepperBrakeEnablePin:
    def __init__(self, enable, stepper_psu):
        self.enable = enable
        self.stepper_psu = stepper_psu
        self.mcu_pin = stepper_psu.mcu_pin
        self.toolhead = stepper_psu.toolhead
        self.wait_time = stepper_psu.wait_time
        self.mcu_enable = self.enable.mcu_enable
        self.enable.mcu_enable = self
        gcode = self.stepper_psu.printer.lookup_object("gcode")
        gcode.respond_info("TRIGGERED")
        logging.info("MEOW")

    def set_digital(self, print_time, value):
        gcode = self.stepper_psu.printer.lookup_object("gcode")
        gcode.respond_info("TRIGGERED")
        if value and not self.stepper_psu.enabled:
            self.mcu_pin.set_digital(print_time, value)
            self.stepper_psu.enabled = True
            # self.toolhead.dwell(self.wait_time)
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
        self.mcu_pin.setup_max_duration(0.0)
        self.stepper_names = config.getlist("stepper", None)
        self.wait_time = config.getfloat("wait_time", 0.0, minval=0.0)
        self.stepper_enable = self.printer.load_object(config, "stepper_enable")
        self.printer.register_event_handler("klippy:ready", self._handle_ready)
        self.printer.register_event_handler("klippy:connect", self._handle_connect)

        self.enabled = False

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
        logging.info(self.stepper_names)

    def _handle_ready(self):
        logging.info("StepperPSU ready")
        logging.info(self.stepper_names)
        for stepper_name in self.stepper_names:
            StepperBrakeEnablePin(
                self.stepper_enable.lookup_enable(stepper_name).enable,
                self,
            )

    cmd_DISABLE_STEPPER_PSU_help = "Disable the stepper psu"
    def cmd_DISABLE_STEPPER_PSU(self, gcmd):
        self.toolhead.register_lookahead_callback(
            self._disable_psu
        )

    def _disable_psu(self, print_time):
        self.mcu_pin.set_digital(print_time, 0)
        self.enabled = False

def load_config_prefix(config):
    return StepperPSU(config)

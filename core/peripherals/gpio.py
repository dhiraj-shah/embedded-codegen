from core.peripherals.base import PeripheralGenerator, register_peripheral

@register_peripheral("GPIO")
class GPIOGenerator(PeripheralGenerator):
    def should_generate(self) -> bool:
        return bool(self.config.gpio)

    def generate(self) -> None:
        # Header
        tpl = self.env.get_template("shared/peripherals/gpio.h.j2")
        out = tpl.render(board=self.config, now=self.now)
        (self.dirs["include"] / "gpio.h").write_text(out)

        # Source
        tpl = self.env.get_template("shared/peripherals/gpio.c.j2")
        out = tpl.render(board=self.config, now=self.now)
        (self.dirs["src"] / "gpio.c").write_text(out)


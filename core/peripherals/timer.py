from core.peripherals.base import PeripheralGenerator, register_peripheral

@register_peripheral("TIMER")
class UARTGenerator(PeripheralGenerator):
    def should_generate(self) -> bool:
        return bool(self.config.uart)

    def generate(self) -> None:
        tpl = self.env.get_template("shared/peripherals/timer.h.j2")
        out = tpl.render(board=self.config, now=self.now)
        (self.dirs["include"] / "timer.h").write_text(out)

        tpl = self.env.get_template("shared/peripherals/timer.c.j2")
        out = tpl.render(board=self.config, now=self.now)
        (self.dirs["src"] / "timer.c").write_text(out)


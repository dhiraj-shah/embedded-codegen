from core.peripherals.base import PeripheralGenerator, register_peripheral

@register_peripheral("UART")
class UARTGenerator(PeripheralGenerator):
    def should_generate(self) -> bool:
        return bool(self.config.uart)

    def generate(self) -> None:
        tpl = self.env.get_template("shared/peripherals/uart.h.j2")
        out = tpl.render(board=self.config, now=self.now)
        (self.dirs["include"] / "uart.h").write_text(out)

        tpl = self.env.get_template("shared/peripherals/uart.c.j2")
        out = tpl.render(board=self.config, now=self.now)
        (self.dirs["src"] / "uart.c").write_text(out)


from pathlib import Path
import rich
from rich.tree import Tree
import typer
from pydantic import BaseModel
from ruamel.yaml import YAML

from .data import get_chip_package_and_core
from .tableator import Tableator

yaml = YAML()


app = typer.Typer()


class _Spec(BaseModel):
    class Requirement(BaseModel):
        name: str
        peripheral: str | None = None
        kind: str | None = None
        signals: list[str] | None = None
        consume_peripheral: bool = True

    chip: str
    package: str
    requirements: list[Requirement]
    reserved_pins: dict[str, str] = {}


def _load_reqs(reqs: Path | None = None) -> _Spec:
    if reqs is None:
        reqs = Path("reqs.yml")
    if reqs.suffix == ".json":
        _reqs = _Spec.model_validate_json(reqs.read_text())
    elif reqs.suffix in (".yaml", ".yml"):
        _reqs = _Spec.model_validate(yaml.load(reqs.read_text()))
    else:
        raise ValueError(f"Unsupported spec extension: {reqs.suffix}")
    return _reqs


@app.command()
def solve(reqs: Path | None = None, chip: str | None = None, package: str | None = None):
    _reqs = _load_reqs(reqs)

    # Allows overriding the chip and package from the command line
    # to experiment with different chips and packages
    if chip is not None:
        _reqs.chip = chip
    if package is not None:
        _reqs.package = package

    package, core = get_chip_package_and_core(_reqs.chip, _reqs.package)

    tableator = Tableator(package, core)
    for requirement in _reqs.requirements:
        tableator.add_req(
            requirement_name=requirement.name,
            peripheral_name=requirement.peripheral,
            peripheral_kind=requirement.kind,
            peripheral_signal_names=requirement.signals,
            consume_peripheral=requirement.consume_peripheral,
        )

    for requirement_name, pin in _reqs.reserved_pins.items():
        tableator.reserve_pin(requirement_name, pin)

    tableator.solve()


@app.command("list")
def list_peripherals(reqs: Path | None = None, chip: str | None = None, package: str | None = None):
    if chip is None or package is None:
        try:
            _reqs = _load_reqs(reqs)
        except FileNotFoundError:
            raise typer.BadParameter("Either a reqs file or a chip and package must be provided") from FileNotFoundError
        chip = chip or _reqs.chip
        package = package or _reqs.package

    _, core = get_chip_package_and_core(chip, package)

    tree = Tree("Peripherals")
    for peripheral in core.peripherals:
        node = tree.add(peripheral.name)
        for pin in peripheral.pins or []:
            node.add(pin.signal)

    rich.print(tree)


if __name__ == "__main__":
    app()

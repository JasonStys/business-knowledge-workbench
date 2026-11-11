# @index-begin
# @symbol variable/parameter: monkeypatch L29
# @symbol function/class: test_unreviewed_frozen_runtime_refuses_before_private_setup L29
# @symbol variable/parameter: version L29
# @symbol variable/parameter: events L31
# @symbol variable/parameter: module_name L36
# @symbol variable/parameter: module L37
# @symbol function/class: test_reviewed_runtime_retains_private_and_conversion_dispatch L50
# @symbol variable/parameter: convert L51
# @symbol variable/parameter: frozen L51
# @symbol variable/parameter: service L59
# @symbol variable/parameter: worker L61
# @index-end
"""Jason Stys: frozen runtime identity and conversion-child dispatch regressions.

Service and conversion entry points are inert test modules; no private files open.
Definition and variable locations are generated in the repository code index.
"""

import runpy
import sys
import types
from pathlib import Path

import pytest


@pytest.mark.parametrize("version", [(3, 12, 10), (3, 14, 6), (3, 14, 11)])
def test_unreviewed_frozen_runtime_refuses_before_private_setup(monkeypatch, version):
    """An unreviewed interpreter cannot open a vault or launch a conversion child."""
    events = []
    monkeypatch.setattr("multiprocessing.freeze_support", lambda: events.append("freeze"))
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "version_info", version)
    monkeypatch.setattr(sys, "argv", ["workbench", "--convert"])
    for module_name in ("server.private_cli", "server.worker"):
        module = types.ModuleType(module_name)
        module.main = lambda: events.append("dispatch")
        monkeypatch.setitem(sys.modules, module_name, module)
    with pytest.raises(SystemExit, match="reviewed Python 3.14.10"):
        runpy.run_path(
            str(Path(__file__).parents[2] / "scripts/frozen_entry.py"), run_name="__main__"
        )
    assert events == ["freeze"]
    assert sys.argv == ["workbench", "--convert"]


@pytest.mark.parametrize("frozen,version", [(True, (3, 14, 10)), (False, (3, 12, 10))])
@pytest.mark.parametrize("convert", [False, True])
def test_reviewed_runtime_retains_private_and_conversion_dispatch(
    monkeypatch, frozen, version, convert
):
    """Both UI service and fixed-format conversion child use the intended entry point."""
    events = []
    monkeypatch.setattr("multiprocessing.freeze_support", lambda: events.append("freeze"))
    monkeypatch.setattr(sys, "frozen", frozen, raising=False)
    monkeypatch.setattr(sys, "version_info", version)
    monkeypatch.setattr(sys, "argv", ["workbench", "--convert"] if convert else ["workbench"])
    service = types.ModuleType("server.private_cli")
    service.main = lambda: events.append("service")
    worker = types.ModuleType("server.worker")
    worker.main = lambda: events.append("convert")
    monkeypatch.setitem(sys.modules, "server.private_cli", service)
    monkeypatch.setitem(sys.modules, "server.worker", worker)
    runpy.run_path(str(Path(__file__).parents[2] / "scripts/frozen_entry.py"), run_name="__main__")
    assert events == ["freeze", "convert" if convert else "service"]
    assert sys.argv == ["workbench"]

"""Open every window for real (adb faked) to catch layout/Tk errors per platform.

Needs a display, so it only runs when ATV_GUI_TESTS=1 (CI sets it; Linux CI
runs under xvfb).
"""
import functools
import os
import sys
import tkinter
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import run_toolkit

pytestmark = pytest.mark.skipif(os.environ.get("ATV_GUI_TESTS") != "1",
                                reason="set ATV_GUI_TESTS=1 to open real windows")

sg = run_toolkit.sg
REAL_READ = sg.Window.read  # before the fixture swaps it out
ALL_PACKAGES = ({pkg for _, pkg in run_toolkit.safe_apps}
                | {pkg for _, pkg, _ in run_toolkit.apps}
                | {pkg for _, pkg in run_toolkit.GOOGLE_LAUNCHERS})
_shared_tcl = functools.lru_cache(maxsize=None)(tkinter.Tcl)


@pytest.fixture
def rendered(monkeypatch):
    """Each window renders once, then closes; returns the titles shown."""
    titles = []
    real_read = sg.Window.read

    def read_once(self, timeout=None, **kwargs):
        real_read(self, timeout=100)
        titles.append(self.Title)
        return sg.WINDOW_CLOSED, {}

    monkeypatch.setattr(sg.Window, "read", read_once)
    # FreeSimpleGUI creates a throwaway Tcl interpreter for every window just to
    # read the version. Creating dozens in one process intermittently fails on
    # Windows CI ("Can't find a usable init.tcl ... No error"; see
    # actions/setup-python#1102, python/cpython#126549), so reuse one.
    monkeypatch.setattr(tkinter, "Tcl", _shared_tcl)
    for name in ("popup", "popup_scrolled"):
        monkeypatch.setattr(sg, name, lambda *a, **k: None)
    monkeypatch.setattr(sg, "popup_yes_no", lambda *a, **k: "No")

    # A connected TV where half the known apps are enabled and half disabled.
    pkgs = sorted(ALL_PACKAGES)
    enabled, disabled = set(pkgs[::2]), set(pkgs[1::2])
    run_toolkit.state.ip, run_toolkit.state.port, run_toolkit.state.connected = "192.0.2.1", "5555", True
    monkeypatch.setattr(run_toolkit, "reconnect_check", lambda: True)
    monkeypatch.setattr(run_toolkit, "ADB", run_toolkit.ADB)  # main_menu runs ensure_adb
    monkeypatch.setattr(run_toolkit, "package_state", lambda: (enabled, disabled))
    monkeypatch.setattr(run_toolkit, "run_adb", lambda *a, **k: ("", "", 0))
    monkeypatch.setattr(run_toolkit.TVFinder, "start", lambda self: self)  # no network searches
    yield titles
    run_toolkit.state.connected = False


@pytest.mark.parametrize("dialog", [
    "main_menu", "connect_to_tv", "pair_and_connect", "install_apk",
    "safe_debloat_checklist", "advanced_debloat", "reenable_apps",
])
def test_window_opens(rendered, dialog):
    getattr(run_toolkit, dialog)()
    assert len(rendered) == 1


def test_main_menu_greys_out_tv_actions_until_connected(rendered, monkeypatch):
    """TV-only buttons start disabled and are enabled once an action connects."""
    run_toolkit.state.connected = False
    snapshots = []
    events = iter(["Connect to TV", sg.WINDOW_CLOSED])
    real_read = sg.Window.read

    def read(self, timeout=None, **kwargs):
        real_read(self, timeout=100)
        snapshots.append(({name for _, names in run_toolkit.MENU for name in names
                           if self[name].Widget.instate(["disabled"])}, self["-CONN-"].get()))
        return next(events), {}

    def fake_connect():
        run_toolkit.state.connected = True

    monkeypatch.setattr(sg.Window, "read", read)
    monkeypatch.setitem(run_toolkit.main_menu.__globals__, "connect_to_tv", fake_connect)
    run_toolkit.main_menu()
    (disabled_before, status_before), (disabled_after, status_after) = snapshots
    assert disabled_before == run_toolkit.NEEDS_TV and status_before.startswith("⚪")
    assert disabled_after == set() and status_after.startswith("✅ Connected")


def test_debloat_checkbox_shows_package_and_tooltip(rendered, monkeypatch):
    read_once = sg.Window.read
    checkboxes = {}

    def fake_read(self, timeout=None, **kwargs):
        read_once(self)
        for el in self.element_list():
            if isinstance(el, sg.Checkbox):
                checkboxes[el.Key] = el
        return sg.WINDOW_CLOSED, {}

    monkeypatch.setattr(sg.Window, "read", fake_read)
    run_toolkit.advanced_debloat()
    for label, pkg, risk in run_toolkit.apps:
        assert checkboxes[pkg].Text.startswith(f"{risk} {label}  ({pkg})")
        assert checkboxes[pkg].Tooltip == pkg


def test_reenable_select_and_deselect_all(rendered, monkeypatch):
    read_once = sg.Window.read
    events = iter(["Select All", "Deselect All", sg.WINDOW_CLOSED])
    states = []

    def fake_read(self, timeout=None, **kwargs):
        read_once(self)
        cks = [el for el in self.element_list() if isinstance(el, sg.Checkbox)]
        states.append([ck.get() for ck in cks])
        return next(events), {}

    monkeypatch.setattr(sg.Window, "read", fake_read)
    run_toolkit.reenable_apps()
    assert states[0] and not any(states[0])
    assert all(states[1])
    assert not any(states[2])


class FakeFinder:
    def __init__(self, tvs):
        self.tvs, self.searched, self.stopped = tvs, True, False

    def stop(self):
        self.stopped = True


def _drive(monkeypatch, dialog, tvs, steps):
    """Run dialog with a fake finder; each step may edit fields, then returns an event."""
    finder = FakeFinder(tvs)
    monkeypatch.setattr(run_toolkit, "TVFinder", lambda: type("F", (), {"start": lambda self: finder})())
    real_read = REAL_READ
    fields = []
    steps = iter(steps)

    def read(self, timeout=None, **kwargs):
        event, values = real_read(self, timeout=100)
        if event == run_toolkit.DONE:  # a background job finished: let the dialog see it
            return event, values
        fields.append({k: self[k].get() for k in ("IP", "PAIR_PORT", "DEBUG_PORT", "-FOUND-")
                       if k in self.AllKeysDict})
        event = next(steps)(self)
        return event, real_read(self, timeout=10)[1]

    monkeypatch.setattr(sg.Window, "read", read)
    getattr(run_toolkit, dialog)()
    assert finder.stopped
    return fields


def test_pair_window_fills_ports_when_pairing_screen_opens(rendered, monkeypatch):
    tv = run_toolkit.FoundTV("10.0.0.4", "Den TV", connect_port="40000", pair_port="37000")
    fields = _drive(monkeypatch, "pair_and_connect", [tv],
                    [lambda w: sg.TIMEOUT_EVENT, lambda w: sg.WINDOW_CLOSED])
    assert fields[0]["IP"] == "192.0.2.1"  # remembered from the last connection
    assert fields[1]["IP"] == "10.0.0.4"
    assert (fields[1]["PAIR_PORT"], fields[1]["DEBUG_PORT"]) == ("37000", "40000")


def test_pair_window_keeps_ports_the_user_typed(rendered, monkeypatch):
    tv = run_toolkit.FoundTV("192.0.2.1", connect_port="40000", pair_port="37000")

    def type_port(window):
        window["PAIR_PORT"].update("1111")
        return sg.TIMEOUT_EVENT

    fields = _drive(monkeypatch, "pair_and_connect", [tv], [type_port, lambda w: sg.WINDOW_CLOSED])
    assert (fields[1]["PAIR_PORT"], fields[1]["DEBUG_PORT"]) == ("1111", "40000")


def test_connect_window_updates_remembered_port_and_list_click(rendered, monkeypatch):
    ready = run_toolkit.FoundTV("192.0.2.1", "Den TV", connect_port="40000")
    off = run_toolkit.FoundTV("10.0.0.9", "Grandma Tv")

    def click_second(window):
        window["-TVS-"].update(set_to_index=1)
        return "-TVS-"

    fields = _drive(monkeypatch, "connect_to_tv", [ready, off],
                    [lambda w: sg.TIMEOUT_EVENT, click_second, lambda w: sg.WINDOW_CLOSED])
    assert fields[0]["IP"] == "192.0.2.1:5555"
    assert fields[1]["IP"] == "192.0.2.1:40000"  # Wireless debugging moved to a new port
    assert fields[2]["IP"] == "10.0.0.9"


def test_connect_window_says_when_nothing_was_found(rendered, monkeypatch):
    fields = _drive(monkeypatch, "connect_to_tv", [],
                    [lambda w: sg.TIMEOUT_EVENT, lambda w: sg.WINDOW_CLOSED])
    assert fields[0]["-FOUND-"] == "Searching…"
    assert fields[1]["-FOUND-"].startswith("No TVs found automatically")


def test_pair_window_follows_the_tv_whose_pairing_screen_is_open(rendered, monkeypatch):
    """The remembered TV is still on the network, but another one is waiting to pair."""
    remembered = run_toolkit.FoundTV("192.0.2.1", "Den TV")
    pairing = run_toolkit.FoundTV("10.0.0.4", "Grandma Tv", pair_port="37000")
    tvs = [pairing, remembered]

    def pairing_screen_closes(window):
        tvs[0] = run_toolkit.FoundTV("10.0.0.4", "Grandma Tv")
        return sg.TIMEOUT_EVENT

    fields = _drive(monkeypatch, "pair_and_connect", tvs,
                    [lambda w: sg.TIMEOUT_EVENT, pairing_screen_closes, lambda w: sg.WINDOW_CLOSED])
    assert (fields[1]["IP"], fields[1]["PAIR_PORT"]) == ("10.0.0.4", "37000")
    assert (fields[2]["IP"], fields[2]["PAIR_PORT"]) == ("10.0.0.4", "")  # old port cleared


def test_pair_window_leaves_a_typed_ip_alone(rendered, monkeypatch):
    tv = run_toolkit.FoundTV("10.0.0.4", pair_port="37000")

    def type_ip(window):
        window["IP"].update("10.0.0.4")  # e.g. halfway through typing 10.0.0.45
        return sg.TIMEOUT_EVENT

    fields = _drive(monkeypatch, "pair_and_connect", [tv], [type_ip, lambda w: sg.WINDOW_CLOSED])
    assert (fields[1]["IP"], fields[1]["PAIR_PORT"]) == ("10.0.0.4", "")


def test_connect_window_failed_connect_keeps_remembered_address(rendered, monkeypatch):
    monkeypatch.setattr(run_toolkit, "adb_connect", lambda target: (False, "refused"))

    def connect(window):
        window["IP"].update("10.0.0.99:5555")
        return "Connect"

    def wait_then_close(window):
        if window.metadata:  # still connecting
            return sg.TIMEOUT_EVENT
        status.append(window["-STATUS-"].get())
        return sg.WINDOW_CLOSED

    status = []
    _drive(monkeypatch, "connect_to_tv", [], [connect] + [wait_then_close] * 50)
    assert status[0].startswith("❌ Failed to connect.")
    assert run_toolkit.state.target == "192.0.2.1:5555"

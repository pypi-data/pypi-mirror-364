import pytest
import dataclasses
import json
import pathlib
from typing import List

def pytest_addoption(parser):
    parser.addoption(
        "--lobster",
        action="store",
        type=pathlib.Path,
        help="filename for lobster file"
    )

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "trace_to(requirment): trace the requirements"
    )
    config.addinivalue_line(
        "markers", "justification(justification): justification for the test"
    )


def pytest_collection_modifyitems(session, config, items):
    for item in items:
        for marker in item.iter_markers(name="trace_to"):
            trace_to = marker.args[0]
            item.user_properties.append(("trace_to", trace_to))
        for marker in item.iter_markers(name="justification"):
            justification = marker.args[0]
            item.user_properties.append(("justification", justification))


@dataclasses.dataclass
class LobsterFileReference:
    file: str
    line: int | None
    column: int | None
    kind: str = "file"


@dataclasses.dataclass
class LobsterActivity:
    tag: str
    location: LobsterFileReference
    name: str
    refs: List[str]
    just_up: List[str]
    just_down: List[str]
    just_global: List[str]
    framework: str
    kind: str
    status: str | None


@dataclasses.dataclass
class Lobster:
    data: List[LobsterActivity]
    schema: str = "lobster-act-trace"
    version: int = 3
    generator: str = "pytest_lobster"

    def have_item(self, key: str) -> bool:
        return any(i.tag == key for i in self.data)

@dataclasses.dataclass
class LobsterMin:
    version: int = 3
    schema: str = "lobster-act-trace"
    generator: str = "pytest_lobster"


lobster_report_key = pytest.StashKey[Lobster]()


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    if dont_make_lobster_report(item.session):
        return
    lobster = item.session.stash[lobster_report_key]
    test_id = "pytest " + item.nodeid

    if call.excinfo:
        if call.excinfo.typename is "Skipped":
            new_status = "not run"
        else:
            new_status = "fail"
    else:
        new_status = "ok"

    if lobster.have_item(test_id):
        for item in lobster.data:
            if item.tag == test_id:
                if item.status == "ok":
                    item.status = new_status

    else:
        status = new_status
        (relfspath, lineno, testname) = item.location
        refs = []
        just_up = []
        just_down = []
        just_global = []
        for marker in item.own_markers:
            if marker.name == "trace_to":
                for arg in marker.args:
                    refs.append(f"req {arg}")
            if marker.name == "justification":
                for arg in marker.args:
                    just_up.append(arg)

        activity = LobsterActivity(
            test_id,
            LobsterFileReference(
                relfspath,
                lineno,
                None
            ), item.name, refs, just_up, just_down, just_global,
            "PyTest", "Test", status)
        lobster.data.append(activity)


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    file_name = session.config.getoption("--lobster")
    if file_name:
        lobster = Lobster([])
        session.stash[lobster_report_key] = lobster


@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session, exitstatus):
    if dont_make_lobster_report(session):
        return

    report = session.stash[lobster_report_key]
    lobster_json = json.dumps(dataclasses.asdict(report))
    file_name = session.config.getoption("--lobster")
    if file_name:
        with file_name.open("w") as f:
            f.write(lobster_json)


def dont_make_lobster_report(session):
    return not lobster_report_key in session.stash

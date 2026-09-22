"""Exercise script startup and configuration without downloading or running full data."""

import importlib.metadata
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
from unittest.mock import Mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ["run-small-sharrow.py", "run-large-sharrow.py"]


@pytest.fixture
def project_environment():
    # ActivitySim also runs this suite using its own environment and lockfile.
    # Only opt into checks of this project's environment when it was installed
    # explicitly; a launcher could otherwise sync away the version under test.
    source = os.environ.get("ACTIVITYSIM_TEST_SOURCE")
    if source not in ("locked", "main"):
        pytest.skip("requires the example environment (ACTIVITYSIM_TEST_SOURCE=locked or main)")
    return source


@pytest.mark.parametrize("script_name", SCRIPTS)
def test_script_launcher_uses_project_environment(tmp_path, script_name, project_environment):
    # Execute the actual launcher and dependency metadata, replacing only the
    # model body with a version probe so this test never launches a large run.
    source = (ROOT / "scripts" / script_name).read_text()
    header = source.split('"""', 1)[0]
    probe = tmp_path / script_name
    probe.write_text(
        header + '\nimport importlib.metadata, json\n'
        'print(json.dumps({p: importlib.metadata.version(p) '
        'for p in ["activitysim", "sharrow", "numpy"]}))\n'
    )
    probe.chmod(0o755)
    # Windows cannot execute a Python shebang. Use the documented uv command
    # there, while continuing to exercise direct execution on POSIX systems.
    command = ["uv", "run", "--locked", str(probe)] if os.name == "nt" else [str(probe)]
    result = subprocess.run(
        command, cwd=ROOT, env=os.environ.copy(),
        text=True, capture_output=True, check=True, timeout=120,
    )
    versions = json.loads(result.stdout)
    assert versions == {p: importlib.metadata.version(p) for p in versions}
    assert int(versions["numpy"].split(".")[0]) == 2


@pytest.mark.parametrize("script_name,households,data_dir", [
    ("run-small-sharrow.py", 100, "data"),
    ("run-large-sharrow.py", 500_000, "data_full"),
])
def test_script_preserves_checkout_and_configures_model(
    tmp_path, monkeypatch, script_name, households, data_dir
):
    # Keep real ActivitySim imports and configuration validation. Replace only
    # downloading, cache/log setup, and the expensive simulation itself.
    import activitysim.abm  # noqa: F401
    from activitysim.core import workflow
    from activitysim.examples import external

    scripts = tmp_path / "scripts"
    scripts.mkdir()
    script = scripts / script_name
    shutil.copy2(ROOT / "scripts" / script_name, script)
    for directory in ("configs", "data", "data_model"):
        (tmp_path / directory).symlink_to(ROOT / directory, target_is_directory=True)
    (tmp_path / "data_full").symlink_to(ROOT / "data", target_is_directory=True)
    ignore = tmp_path / ".gitignore"
    ignore.write_text("# Preserve user rules\n/data_full\n")
    original = ignore.read_bytes()
    download = Mock()
    monkeypatch.setattr(external, "download_asset", download)
    make_default = workflow.State.make_default
    captured = []

    def configure(**kwargs):
        state = make_default(**kwargs)
        run = Mock()
        monkeypatch.setattr(type(state.run), "all", run)
        monkeypatch.setattr(type(state.filesystem), "persist_sharrow_cache", Mock())
        monkeypatch.setattr(type(state.logging), "config_logger", Mock())
        captured.append((state, kwargs, run))
        return state

    monkeypatch.setattr(workflow.State, "make_default", configure)
    runpy.run_path(str(script), run_name="__main__")
    state, kwargs, run = captured[0]
    assert state.settings.households_sample_size == households
    assert state.settings.sharrow == "require"
    assert kwargs["data_dir"] == data_dir
    run.assert_called_once_with(resume_after=None)
    assert ignore.read_bytes() == original
    assert (scripts / script_name.replace(".py", "-output") / ".gitignore").read_text() == "**\n"
    if data_dir == "data_full":
        download.assert_called_once()
        assert download.call_args.kwargs["unpack"] == "data_full"
    else:
        download.assert_not_called()


def test_locked_dependencies_are_installed(project_environment):
    import tomli

    with (ROOT / "uv.lock").open("rb") as stream:
        packages = tomli.load(stream)["package"]
    for name in ("activitysim", "sharrow", "numpy"):
        if name == "activitysim" and project_environment == "main":
            continue  # Only ActivitySim is replaced in the compatibility job.
        locked = next(p["version"] for p in packages if p["name"] == name)
        assert importlib.metadata.version(name) == locked

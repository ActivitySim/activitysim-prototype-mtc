"""Check that the optional chunk overlay preserves the underlying model settings."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("multiprocess", [False, True])
def test_explicit_chunk_overlay_inherits_model_settings(tmp_path, multiprocess):
    import activitysim.abm  # noqa: F401
    from activitysim.core import workflow

    configs = ["configs_mp", "configs"] if multiprocess else ["configs"]
    base = workflow.State.make_default(
        working_dir=ROOT, configs_dir=configs, output_dir=tmp_path,
    )
    overlay = workflow.State.make_default(
        working_dir=ROOT,
        configs_dir=["configs_explicit_chunk", *configs],
        output_dir=tmp_path,
    )
    assert overlay.settings.chunk_training_mode == "explicit"
    assert overlay.settings.chunk_size == 0
    assert overlay.settings.models == base.settings.models
    for path in sorted((ROOT / "configs_explicit_chunk").glob("*.yaml")):
        if path.name == "settings.yaml":
            continue
        original = base.filesystem.read_model_settings(path.name, mandatory=True)
        merged = overlay.filesystem.read_model_settings(path.name, mandatory=True)
        assert merged["explicit_chunk"] == 10000
        for key, value in original.items():
            if key not in ("explicit_chunk", "source_file_paths"):
                assert merged[key] == value, (path.name, key)

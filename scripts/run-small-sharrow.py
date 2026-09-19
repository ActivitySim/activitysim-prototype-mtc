#!/usr/bin/env -S uv run --locked

"""
Run the MTC example model with sharrow enabled, on the small test sample.

Run from the repository root with `uv run --locked scripts/run-small-sharrow.py`
or execute this file directly there. Both use the shared pyproject.toml and uv.lock.
"""

from pathlib import Path

import activitysim.abm  # register components # noqa: F401
from activitysim.core import workflow


def main():
    working_dir = Path(__file__).parents[1]
    out_dir = Path(str(__file__).replace(".py", "-output"))
    out_dir.mkdir(exist_ok=True)
    out_dir.joinpath(".gitignore").write_text("**\n")

    settings = dict(
        cleanup_pipeline_after_run=False,
        treat_warnings_as_errors=False,
        households_sample_size=100,
        chunk_size=0,
        use_shadow_pricing=True,
        sharrow="require",
        recode_pipeline_columns=True,
    )

    state = workflow.State.make_default(
        working_dir=working_dir,
        configs_dir=("configs",),
        data_dir="data",
        output_dir=out_dir,
        settings=settings,
    )
    state.filesystem.persist_sharrow_cache()
    state.logging.config_logger()

    state.run.all(resume_after=None)


if __name__ == "__main__":
    main()

#!/usr/bin/env -S uv run --script --locked --no-project
#
# /// script
# requires-python = ">=3.10,<3.12"
# dependencies = [
#   "activitysim >=1.5,<2.0",
#   "sharrow >=2.15",
# ]
# [tool.uv]
# exclude-newer = "2025-11-01T00:00:00Z"
# ///

"""
Run the MTC example model with sharrow enabled, on the small test sample.

The metadata in the header above allows this script to be run with `uv` without
needing to set up a separate virtual environment or install dependencies manually.
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
        configs_dir=(
            "configs",
        ),
        data_dir="data",
        output_dir=out_dir,
        settings=settings,
    )
    state.filesystem.persist_sharrow_cache()
    state.logging.config_logger()

    # TODO: this script should be able to be run end-to-end with the "all" command
    #       but should be configurable to run by resuming or starting over.
    state.run.all(resume_after=None)

    # for step_name in state.settings.models:
    #     state.run.by_name(step_name)


if __name__ == "__main__":
    main()

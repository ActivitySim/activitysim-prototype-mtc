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
import os.path

import platformdirs
import activitysim.abm  # register components # noqa: F401
from activitysim.core import workflow
from activitysim.examples.external import download_external_example, download_asset

import pandas as pd

def main():



    # in various places, ActivitySim emits this warning:
    #
    # FutureWarning:
    #   Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a
    #   future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior,
    #   set `pd.set_option('future.no_silent_downcasting', True)`


    pd.set_option('future.no_silent_downcasting', True)



    working_dir = Path(__file__).parents[1]

    download_asset(
        url="https://github.com/ActivitySim/activitysim-prototype-mtc/releases/download/v1.3.4/data_full.tar.zst",
        target_path=os.path.join(working_dir, "data_full.tar.zst"),
        sha256 = "b402506a61055e2d38621416dd9a5c7e3cf7517c0a9ae5869f6d760c03284ef3",
        link = Path(platformdirs.user_cache_dir(appname="ActivitySim")) / "External-Data",
        base_path=str(working_dir),
        unpack = "data_full",
    )

    # do not allow full data to enter Git repo
    working_dir.joinpath(".gitignore").write_text("**\n")

    out_dir = Path(str(__file__).replace(".py", "-output"))
    out_dir.mkdir(exist_ok=True)
    out_dir.joinpath(".gitignore").write_text("**\n")

    settings = dict(
        cleanup_pipeline_after_run=False,
        treat_warnings_as_errors=False,
        households_sample_size=500_000,
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
        data_dir="data_full",
        output_dir=out_dir,
        settings=settings,
    )
    state.filesystem.persist_sharrow_cache()
    state.logging.config_logger()

    state.run.all(resume_after=None)



if __name__ == "__main__":
    main()

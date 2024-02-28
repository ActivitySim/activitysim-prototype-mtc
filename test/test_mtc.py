# ActivitySim
# See full license in LICENSE.txt.
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pandas.testing as pdt

from activitysim.core import testing, workflow


def _example_path(dirname):
    """Paths to things in the top-level directory of this repository."""
    return os.path.normpath(os.path.join(os.path.dirname(__file__), "..", dirname))


def _test_path(dirname):
    """Paths to things in the `test` directory."""
    return os.path.join(os.path.dirname(__file__), dirname)


def run_test_mtc(
    multiprocess=False, chunkless=False, recode=False, sharrow=False, extended=False
):

    def regress(ext):
        if ext:
            regress_trips_df = pd.read_csv(_test_path("regress/final_trips-ext.csv"))
        else:
            regress_trips_df = pd.read_csv(_test_path("regress/final_trips.csv"))
        final_trips_df = pd.read_csv(_test_path("output/final_trips.csv"))

        # column order may not match, so fix it before checking
        assert sorted(regress_trips_df.columns) == sorted(final_trips_df.columns)
        final_trips_df = final_trips_df[regress_trips_df.columns]

        # person_id,household_id,tour_id,primary_purpose,trip_num,outbound,trip_count,purpose,
        # destination,origin,destination_logsum,depart,trip_mode,mode_choice_logsum
        # compare_cols = []
        pdt.assert_frame_equal(final_trips_df, regress_trips_df)

    file_path = os.path.join(os.path.dirname(__file__), "simulation.py")

    run_args = []

    if multiprocess:
        if extended:
            run_args.extend(
                [
                    "-c",
                    _test_path("ext-configs_mp"),
                    "-c",
                    _example_path("ext-configs_mp"),
                ]
            )
        else:
            run_args.extend(
                [
                    "-c",
                    _test_path("configs_mp"),
                    "-c",
                    _example_path("configs_mp"),
                ]
            )
    elif chunkless:
        run_args.extend(
            [
                "-c",
                _test_path("configs_chunkless"),
            ]
        )
    elif recode:
        run_args.extend(
            [
                "-c",
                _test_path("configs_recode"),
            ]
        )
    elif sharrow:
        run_args.extend(
            [
                "-c",
                _test_path("configs_sharrow"),
            ]
        )
        if os.environ.get("GITHUB_ACTIONS") != "true":
            run_args.append("--persist-sharrow-cache")
    else:
        run_args.extend(
            [
                "-c",
                _test_path("configs"),
            ]
        )

    # general run args
    if extended:
        run_args.extend(
            [
                "--data_model",
                _example_path("data_model"),
                "-c",
                _test_path("ext-configs"),
                "-c",
                _example_path("ext-configs"),
            ]
        )

    out_dir = _test_path(
        f"output-{'mp' if multiprocess else 'single'}"
        f"-{'chunkless' if chunkless else 'chunked'}"
        f"-{'recode' if recode else 'no_recode'}"
        f"-{'sharrow' if sharrow else 'no_sharrow'}"
        f"-{'ext' if extended else 'no_ext'}"
    )

    # create output directory if it doesn't exist and add .gitignore
    Path(out_dir).mkdir(exist_ok=True)
    Path(out_dir).joinpath(".gitignore").write_text("**\n")

    run_args.extend(
        [
            "-c",
            _example_path("configs"),
            "-d",
            _example_path("data"),
            "-o",
            out_dir,
        ]
    )

    if os.environ.get("GITHUB_ACTIONS") == "true":
        subprocess.run(["coverage", "run", "-a", file_path] + run_args, check=True)
    else:
        subprocess.run([sys.executable, file_path] + run_args, check=True)

    regress(extended)


def test_mtc():
    run_test_mtc(multiprocess=False)


def test_mtc_chunkless():
    run_test_mtc(multiprocess=False, chunkless=True)


def test_mtc_mp():
    run_test_mtc(multiprocess=True)


def test_mtc_recode():
    run_test_mtc(recode=True)


def test_mtc_sharrow():
    run_test_mtc(sharrow=True)


def test_mtc_ext():
    run_test_mtc(multiprocess=False, extended=True)


def test_mtc_chunkless_ext():
    run_test_mtc(multiprocess=False, chunkless=True, extended=True)


def test_mtc_mp_ext():
    run_test_mtc(multiprocess=True, extended=True)


def test_mtc_recode_ext():
    run_test_mtc(recode=True, extended=True)


def test_mtc_sharrow_ext():
    run_test_mtc(sharrow=True, extended=True)


EXPECTED_MODELS = [
    'input_checker',
    'initialize_proto_population',
    'compute_disaggregate_accessibility',
    "initialize_landuse",
    "initialize_households",
    "compute_accessibility",
    "school_location",
    "workplace_location",
    "auto_ownership_simulate",
    "vehicle_type_choice",
    "free_parking",
    "cdap_simulate",
    "mandatory_tour_frequency",
    "mandatory_tour_scheduling",
    "school_escorting",
    "joint_tour_frequency",
    "joint_tour_composition",
    "joint_tour_participation",
    "joint_tour_destination",
    "joint_tour_scheduling",
    "non_mandatory_tour_frequency",
    "non_mandatory_tour_destination",
    "non_mandatory_tour_scheduling",
    "vehicle_allocation",
    "tour_mode_choice_simulate",
    "atwork_subtour_frequency",
    "atwork_subtour_destination",
    "atwork_subtour_scheduling",
    "atwork_subtour_mode_choice",
    "stop_frequency",
    "trip_purpose",
    "trip_destination",
    "trip_purpose_and_destination",
    "trip_scheduling",
    "trip_mode_choice",
    "write_data_dictionary",
    "track_skim_usage",
    "write_trip_matrices",
    "write_tables",
]


@testing.run_if_exists("reference-pipeline-extended.zip")
def test_mtc_extended_progressive():

    import activitysim.abm  # register components # noqa: F401

    out_dir = _test_path("output-progressive")
    Path(out_dir).mkdir(exist_ok=True)
    Path(out_dir).joinpath(".gitignore").write_text("**\n")

    state = workflow.State.make_default(
        configs_dir=(
            _test_path("configs_recode"),
            _test_path("ext-configs"),
            _example_path("ext-configs"),
            _test_path("configs"),
            _example_path("configs"),
        ),
        data_dir=_example_path("data"),
        data_model_dir=_example_path("data_model"),
        output_dir=out_dir,
    )
    state.filesystem.persist_sharrow_cache()

    assert state.settings.models == EXPECTED_MODELS
    assert state.settings.chunk_size == 0
    assert not state.settings.sharrow

    for step_name in EXPECTED_MODELS:
        state.run.by_name(step_name)
        try:
            state.checkpoint.check_against(
                Path(__file__).parent.joinpath("reference-pipeline-extended.zip"),
                checkpoint_name=step_name,
            )
        except Exception:
            print(f"> prototype_mtc_extended {step_name}: ERROR")
            raise
        else:
            print(f"> prototype_mtc_extended {step_name}: ok")


if __name__ == "__main__":
    run_test_mtc(multiprocess=False)
    run_test_mtc(multiprocess=True)
    run_test_mtc(multiprocess=False, chunkless=True)
    run_test_mtc(recode=True)
    run_test_mtc(sharrow=True)
    run_test_mtc(multiprocess=False, extended=True)
    run_test_mtc(multiprocess=True, extended=True)
    run_test_mtc(multiprocess=False, chunkless=True, extended=True)
    run_test_mtc(recode=True, extended=True)
    run_test_mtc(sharrow=True, extended=True)
    test_mtc_extended_progressive()

# Explicit chunking overlay

Use `-c configs_explicit_chunk -c configs` (or `-c configs_explicit_chunk -c configs_mp -c configs` for multiprocessing).
For the benchmark use `--config-overlay configs_explicit_chunk`.

This overlay enables explicit chunking and caps supported components at 10,000 chooser rows across the process group (2,500 per worker with four processes). This conservative initial limit leaves room for the shared skims, population tables, and temporary alternatives. It is not a 16 GB hard memory guarantee; row limits do not bound fixed tables, retained allocator pages, or every intermediate in main. The PR extends several chunk boundaries to cover more of those intermediates.

Selection uses the union of components whose whole-container memory exceeded 16,000,000,000 bytes in either previous 500,000-household measured run. Legacy windows are approximate and include overlap with other workers, so these are group peaks, not isolated component allocations. `baseline-memory.json` preserves the evidence.

| Component | Highest observed GiB | Overlay / limitation |
|---|---:|---|
| school_location | 18.36 | school_location.yaml |
| workplace_location | 21.90 | workplace_location.yaml |
| auto_ownership_simulate | 16.95 | No wired explicit-chunk control in these revisions |
| free_parking | 16.92 | No wired explicit-chunk control in these revisions |
| cdap_simulate | 16.94 | No wired explicit-chunk control in these revisions |
| mandatory_tour_frequency | 17.92 | No wired explicit-chunk control in these revisions |
| mandatory_tour_scheduling | 27.88 | mandatory_tour_scheduling.yaml |
| joint_tour_frequency | 26.99 | No wired explicit-chunk control in these revisions |
| joint_tour_participation | 27.02 | No wired explicit-chunk control in these revisions |
| joint_tour_destination | 27.02 | joint_tour_destination.yaml |
| joint_tour_scheduling | 22.38 | joint_tour_scheduling.yaml |
| non_mandatory_tour_frequency | 20.13 | non_mandatory_tour_frequency.yaml |
| non_mandatory_tour_destination | 21.71 | non_mandatory_tour_destination.yaml |
| non_mandatory_tour_scheduling | 25.05 | non_mandatory_tour_scheduling.yaml |
| tour_mode_choice_simulate | 24.02 | tour_mode_choice.yaml |
| atwork_subtour_frequency | 23.97 | No wired explicit-chunk control in these revisions |
| atwork_subtour_destination | 25.13 | atwork_subtour_destination.yaml |
| atwork_subtour_scheduling | 24.69 | tour_scheduling_atwork.yaml |
| atwork_subtour_mode_choice | 24.54 | tour_mode_choice.yaml |
| stop_frequency | 24.54 | No wired explicit-chunk control in these revisions |
| trip_purpose | 21.15 | No wired explicit-chunk control in these revisions |
| trip_destination | 22.29 | trip_destination.yaml |
| trip_scheduling | 20.45 | No wired explicit-chunk control in these revisions |
| trip_mode_choice | 20.39 | trip_mode_choice.yaml |
| trip_purpose_and_destination | 20.45 | No wired explicit-chunk control in these revisions |
| write_trip_matrices | 21.10 | No wired explicit-chunk control in these revisions |
| summarize | 24.95 | No wired explicit-chunk control in these revisions |
| joint_tour_composition | 19.50 | No wired explicit-chunk control in these revisions |

For unsupported components, adding `explicit_chunk` would either be rejected or silently do nothing. They therefore have no pretend override. In particular, trip scheduling and CDAP use a chunk-by-group helper but do not pass a configurable explicit size; output matrices/summarization also lack this control. No ordinary config or ActivitySim source is modified. At-work mode choice shares `tour_mode_choice.yaml` with tour mode choice and logsum evaluation.

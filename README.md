# activitysim-prototype-mtc

The primary ActivitySim example model.

The `prototype_mtc` example is based on (but has evolved away from) the
[Bay Area Metro Travel Model One](https://github.com/BayAreaMetro/travel-model-one), 
also known as "TM1". TM1 has its roots in a wide array of analytical approaches, 
including discrete choice forms (multinomial and nested logit models), activity 
duration models, time-use models, models of individual micro-simulation with 
constraints, entropy-maximization models, etc. These tools are combined in the 
model design to realistically represent travel behavior, adequately replicate 
observed activity-travel patterns, and ensure model sensitivity to infrastructure
and policies. The model is implemented in a micro-simulation framework. Microsimulation
methods capture aggregate outcomes through the representation of the behavior of
individual decision-makers.

There are two model structures in the `prototype_mtc` example: a simpler model that is
relatively close to the TM1 model, and a more complex model that is incorporates
new model components that have been added by the ActivitySim consortium over the
past few years.

See https://activitysim.github.io for more information.

# Installation

The following short Python script will download and prepare the example data 
for the `prototype_mtc_extended` example model.

```python
from pathlib import Path
from activitysim.examples.external import download_external_example

example_dir = download_external_example(
  name="prototype_mtc_extended", 
  working_dir=Path.cwd(),
  url="https://github.com/ActivitySim/activitysim-prototype-mtc/archive/refs/heads/extended.tar.gz",
  assets={
    "data_full.tar.zst": {
      "url": "https://github.com/ActivitySim/activitysim-prototype-mtc/releases/download/v1.3.4/data_full.tar.zst",
      "sha256": "b402506a61055e2d38621416dd9a5c7e3cf7517c0a9ae5869f6d760c03284ef3",
      "unpack": "data_full",
    },
    "test/prototype_mtc_reference_pipeline.zip": {
      "url": "https://github.com/ActivitySim/activitysim-prototype-mtc/releases/download/v1.3.2/prototype_mtc_extended_reference_pipeline.zip",
      "sha256": "4d94b6a8a83225dda17e9ca19c9110bc1df2df5b4b362effa153d1c8d31524f5",
    }
  }
)
```

# Benchmarking

The `prototype_mtc` example model is run using the `activitysim` command line tool.
A quick and easy way to run the model for benchmarking is to use the following command:

```shell
cd activitysim-prototype-mtc-extended
activitysim workflow performance-benchmarking
```
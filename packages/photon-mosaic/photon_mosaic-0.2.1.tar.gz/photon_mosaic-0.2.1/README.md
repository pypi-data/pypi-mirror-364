# `photon-mosaic`

`photon-mosaic` is a Snakemake-based pipeline for the automated and reproducible analysis of multiphoton calcium imaging datasets. It currently integrates [Suite2p](https://suite2p.readthedocs.io/en/latest/) for image registration and signal extraction, with plans to support additional analysis modules in the future.

<p align="center">
  <img src="https://raw.githubusercontent.com/neuroinformatics-unit/photon-mosaic/main/docs/source/_static/photon-mosaic.png" alt="photon-mosaic" width="30%"/>
</p>

&nbsp;
## Overview
`photon-mosaic` can leverage SLURM job scheduling, allows standardized and reproducible workflows configurable via a simple YAML config file and produces standardized output folder structures following the [NeuroBlueprint](https://neuroblueprint.neuroinformatics.dev/latest/index.html) specification.

This tool is especially suited for labs that store their data on servers directly connected to an HPC cluster and want to batch-process multiple imaging sessions in parallel.

The current structure sets the stage for future modular integration of preprocessing, neuropil decontamination and deconvolution of choice, and more.

## Installation

Photon-mosaic requires **Python 3.11** or **3.12**.

```bash
conda create -n photon-mosaic python=3.12
conda activate photon-mosaic
pip install photon-mosaic
```

To install developer tools (e.g., testing and linting):

```bash
pip install 'photon-mosaic[dev]'
```

## Contributing

We welcome issues, feature suggestions, and pull requests. Please refer to our [contribution guidelines](https://photon-mosaic.neuroinformatics.dev/user_guide/index.html) in the documentation for more information.

## References & Links

- [Snakemake Docs](https://snakemake.readthedocs.io/en/stable/)
- [Suite2p Docs](https://suite2p.readthedocs.io/en/latest/)
- [SLURM Executor Plugin](https://snakemake.github.io/snakemake-plugin-catalog/plugins/executor/slurm.html)
- [NeuroBlueprint Standard](https://neuroblueprint.neuroinformatics.dev/latest/index.html)

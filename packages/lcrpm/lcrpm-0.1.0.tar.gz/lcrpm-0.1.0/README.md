# IDERHA WP2: Lung Cancer Risk Profile Modeling

This document outlines the setup and usage of the **IDERHA Lung Cancer Risk Prediction Modeling** project, which is currently under development. It focuses on time-to-event modeling for lung cancer risk within a federated learning (FL) framework.

---

## Getting Started

### 1. Environment Setup

To ensure reproducibility, follow these steps to set up your development environment.

#### 1.1. Install Mamba

First, install **Mamba**, a fast, parallel, and robust cross-platform package manager. You can find installation instructions on the [Conda-Forge Mamba download page](https://conda-forge.org/download/).

#### 1.2. Create and Activate the Environment

Once Mamba is installed, create a new Mamba environment named `lcrpm` and activate it:

```sh
# Set PLATFORM based on your operating system (e.g., "mac", "linux") if needed for specific platform dependencies.
# For example: PLATFORM="mac"
mamba env create -n lcrpm python=3.12 poetry

mamba activate lcrpm
````


### Build & install locally

```bash 
python -m build     # Requires 'build' package: pip install build
pip install dist/lcrpm-0.1.0-py3-none-any.whl
```

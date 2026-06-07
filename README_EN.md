# GEA-GQAP: Adaptive Genetic Engineering Algorithm for the Generalized Quadratic Assignment Problem

Python implementation of the Genetic Engineering Algorithm (GEA) for the Generalized Quadratic Assignment Problem (GQAP). Supports four algorithm variants — with and without adaptive parameter tuning, with and without population deduplication — and includes a Taguchi-based RPD parameter tuning pipeline.

---

## Requirements

- Python 3.10+
- [Poetry](https://python-poetry.org/)

```bash
pip install poetry
poetry install
```

---

## Quick start — running the test from the folder

The simplest way to run the full comparative test locally:

```bash
# 1. Create `test_config.json` next to `run_comparison_test.py`
#    (see the "Test configuration" section below)

# 2. Run the script directly via poetry
poetry run python gea_gqap_adaptive_python/tests/run_test/run_comparison_test.py
```

The number of workers is controlled by an environment variable (default 16):

```bash
NUM_WORKERS=8 poetry run python gea_gqap_adaptive_python/tests/run_test/run_comparison_test.py
```

Results are saved to `gea_gqap_adaptive_python/tests/run_test/results/`:
- `<dataset>_results.json` — results per dataset
- `summary_all_datasets.json` — aggregated results for all datasets
- `comparison_results.xlsx` — Excel table with `best_cost` and `elapsed_time`
- `test_output.log` — full run log

After completion you can generate plots:

```bash
# Best-cost evolution over iterations
poetry run python gea_gqap_adaptive_python/tests/run_test/plot_cost_evolution.py

# Evolution of adaptive lambda parameters
poetry run python gea_gqap_adaptive_python/tests/run_test/plot_lambda_evolution.py

# Recreate Excel from existing JSON files (no re-run of tests)
poetry run python gea_gqap_adaptive_python/tests/run_test/create_excel_report.py
```

### Test configuration (`test_config.json`)

The file should be located next to `run_comparison_test.py`. Minimal example:

```json
{
  "num_runs": 30,
  "iterations": 1000,
  "population_size": 350,
  "algorithm": {
    "time_limit": 1000.0,
    "crossover_rate": 0.7,
    "mutation_rate": 0.3
  },
  "algorithm_types": [
    "adaptive",
    "non_adaptive",
    "adaptive_wo_duplicates",
    "non_adaptive_wo_duplicates"
  ],
  "model_variants": {
    "GA":    { "enable_scenario": [false, false, false] },
    "GEA_1": { "enable_scenario": [true,  false, false] },
    "GEA_2": { "enable_scenario": [false, true,  false] },
    "GEA_3": { "enable_scenario": [false, false, true]  },
    "GEA":   { "enable_scenario": [true,  true,  true]  }
  }
}
```

Override algorithm parameters for a specific model or variant:

```json
{
  "algorithm_by_model": {
    "GEA": { "crossover_rate": 0.9 }
  },
  "algorithm_by_variant": {
    "GEA|adaptive": { "adaptive_alpha": 0.2, "adaptive_lambda_max": 1.5 }
  }
}
```

The variant key has the form `"<model>|<type>"`, e.g. `"GEA_1|adaptive_wo_duplicates"`.

---

## Full method — running via SLURM (`run_test.sbatch`)

For running on an HPC cluster with SLURM:

```bash
sbatch run_test.sbatch
```

The script `run_test.sbatch` requests 16 CPUs, sets `NUM_WORKERS=16`, disables BLAS/OpenMP multithreading and runs the same `run_comparison_test.py` via `poetry run`. Output is written to `gea_gqap_test-<job_id>.log`, errors to `gea_gqap_test-<job_id>.err`.

Parameters configurable in `run_test.sbatch`:

| Parameter | Default | Description |
|---|---|---|
| `--cpus-per-task` | 16 | Number of CPUs |
| `--time` | 336:00:00 | Max runtime (14 days) |
| `NUM_WORKERS` | 16 | Parallel worker processes |

---

## Repository structure

```
.
├── pyproject.toml                          # Dependencies and build (Poetry)
├── run_test.sbatch                         # SLURM script for main test
├── run_test_RPD.sbatch                     # SLURM script for Taguchi/RPD
│
├── gea_gqap_adaptive_python/
│   ├── datasets/                           # GQAP datasets (24 files: T1–T14, c*)
│   │
│   ├── gea_gqap_adaptive_python/           # Main Python package
│   │   ├── __init__.py                     # Public API of the package
│   │   ├── models.py                       # Dataclasses: Model, AlgorithmConfig,
│   │   │                                   #   AdaptiveAlgorithmConfig, results
│   │   ├── model_loader.py                 # Loading datasets from .m files
│   │   ├── algorithm.py                    # Non-adaptive run_ga (GA / GEA_1-3 / GEA)
│   │   ├── algorithm_adaptive.py           # Adaptive run_adaptive_ga + deduplication
│   │   ├── operators.py                    # Crossover, mutation, mask_mutation,
│   │   │                                   #   roulette_wheel_selection, analyze_perm
│   │   ├── heuristics.py                   # Initial solution (heuristic2)
│   │   └── utils.py                        # evaluate_permutation and utilities
│   │
│   └── tests/
│       ├── run_test/                  # Main comparative test
│       │   ├── run_comparison_test.py      # Entry point
│       │   ├── test_config.json            # Run parameters (create manually)
│       │   ├── plot_cost_evolution.py      # Best-cost evolution plot
│       │   ├── plot_lambda_evolution.py    # Lambda evolution plot
│       │   ├── create_excel_report.py      # Excel generation from JSON
│       │   └── results/                    # Output JSON and Excel
│       │
│       └── RPD/                            # Taguchi parameter tuning
│           ├── run_rpd_tune_all_sheets.py  # Entry point for RPD tuning
│           ├── taguchi_config_RPD.json     # Orthogonal Taguchi tables L27
│           ├── rpd_utils.py                # RPD metric (MATLAB RPD.m analogue)
│           ├── plot_rpd_from_json.py       # RPD results visualization
│           └── test_rpd_math.py            # Unit test for RPD calculation
│
└── Metaheuristics_GEA/                     # Original MATLAB GEA implementation
    └── Algorithm/                          # .m files of the algorithm
    └── Problem/Generalized_Quadratic/      # .m files of the problem and data
```

### Algorithm variants

| Type | Adaptive | Deduplication |
|---|---|---|
| `adaptive` | yes | no |
| `non_adaptive` | no | no |
| `adaptive_wo_duplicates` | yes | yes |
| `non_adaptive_wo_duplicates` | no | yes |

**Adaptation** — dynamic update of operator weights (λ) on each iteration by the mean improvement δ:

```
λ_new = clamp(λ + α · mean(δ), λ_min, λ_max)
```

**Deduplication** — after forming the offspring pool from the new population, chromosomes with identical genotypes are removed; missing individuals are filled by mutations of the best solution.

### Models (scenarios)

| Model | Scenario 1 | Scenario 2 | Scenario 3 |
|---|---|---|---|
| GA | — | — | — |
| GEA_1 | yes | — | — |
| GEA_2 | — | yes | — |
| GEA_3 | — | — | yes |
| GEA | yes | yes | yes |

### Datasets

24 GQAP instances in `.m` (MATLAB) format:
- **T1–T14** — standard test instances
- **c201535, c201555, c201575, c300695, c300775, c302055, c302075, c302095, c351535, c351595** — instances with continuous parameters

---

## RPD — Taguchi-based parameter tuning

RPD (Relative Percentage Deviation) is used as the quality metric when searching for optimal algorithm parameters.

### Running locally

```bash
poetry run python gea_gqap_adaptive_python/tests/RPD/run_rpd_tune_all_sheets.py
```

### Running via SLURM

```bash
sbatch run_test_RPD.sbatch
```

### Environment variables for RPD

| Variable | Default | Description |
|---|---|---|
| `NUM_WORKERS` | 16 | Parallel worker processes |
| `RPD_NUM_WORKERS` | 16 | Workers inside the RPD loop |
| `RPD_EVAL_MODELS` | `GA,GEA_1,GEA_2,GEA_3,GEA` | Models to evaluate |
| `RPD_EVAL_TYPES` | all 4 types | Algorithm types |
| `RPD_BLOCKS` | `adaptive,base` | Taguchi blocks |
| `RPD_NUM_RUNS` | 5 | Runs per design point |
| `RPD_ITERATIONS` | 1000 | Algorithm iterations |
| `RPD_TIME_LIMIT` | 1000 | Time limit (s) |

### How it works

1. Reads `taguchi_config_RPD.json` — orthogonal Taguchi tables L27 for each model (GA, GEA_1, GEA_2, GEA_3, GEA), two blocks: `base` (6 parameters) and `adaptive` (9 parameters including α, λ_min, λ_max).
2. For each design row runs the algorithm `RPD_NUM_RUNS` times on several datasets.
3. Computes RPD as: `RPD = (cost - best_known) / best_known`.
4. Determines optimal parameter levels by Taguchi S/N ratio.
5. Saves results to JSON and Excel.

### Visualization

```bash
poetry run python gea_gqap_adaptive_python/tests/RPD/plot_rpd_from_json.py
```

### RPD metric verification

```bash
poetry run python gea_gqap_adaptive_python/tests/RPD/test_rpd_math.py
```

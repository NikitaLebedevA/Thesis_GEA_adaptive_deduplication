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

## Quick start — запуск теста из папки

Самый простой способ запустить полное сравнительное тестирование локально:

```bash
# 1. Создайте test_config.json рядом с run_comparison_test.py
#    (см. раздел "Конфигурация теста" ниже)

# 2. Запустите скрипт напрямую через poetry
poetry run python gea_gqap_adaptive_python/tests/run_test/run_comparison_test.py
```

Количество воркеров управляется переменной окружения (по умолчанию 16):

```bash
NUM_WORKERS=8 poetry run python gea_gqap_adaptive_python/tests/run_test/run_comparison_test.py
```

Результаты сохраняются в `gea_gqap_adaptive_python/tests/run_test/results/`:
- `<dataset>_results.json` — результаты по каждому датасету
- `summary_all_datasets.json` — сводный файл по всем датасетам
- `comparison_results.xlsx` — Excel-таблица с best_cost и elapsed_time
- `test_output.log` — полный лог запуска

После завершения можно построить графики:

```bash
# Эволюция стоимости по итерациям
poetry run python gea_gqap_adaptive_python/tests/run_test/plot_cost_evolution.py

# Эволюция адаптивных лямбда-параметров
poetry run python gea_gqap_adaptive_python/tests/run_test/plot_lambda_evolution.py

# Пересоздание Excel из уже готовых JSON (без перезапуска теста)
poetry run python gea_gqap_adaptive_python/tests/run_test/create_excel_report.py
```

### Конфигурация теста (`test_config.json`)

Файл должен лежать рядом с `run_comparison_test.py`. Минимальный пример:

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

Переопределить параметры алгоритма для конкретной модели или варианта:

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

Ключ варианта имеет вид `"<model>|<type>"`, например `"GEA_1|adaptive_wo_duplicates"`.

---

## Длинный способ — запуск через SLURM (run_test.sbatch)

Для запуска на HPC-кластере с SLURM:

```bash
sbatch run_test.sbatch
```

Скрипт `run_test.sbatch` выделяет 16 CPU, устанавливает `NUM_WORKERS=16`, отключает многопоточность BLAS/OpenMP и запускает тот же `run_comparison_test.py` через `poetry run`. Лог пишется в `gea_gqap_test-<job_id>.log`, ошибки — в `gea_gqap_test-<job_id>.err`.

Параметры, которые можно изменить в `run_test.sbatch`:

| Параметр | По умолчанию | Описание |
|---|---|---|
| `--cpus-per-task` | 16 | Количество CPU |
| `--time` | 336:00:00 | Максимальное время (14 дней) |
| `NUM_WORKERS` | 16 | Параллельных процессов |

---

## Содержание репозитория

```
.
├── pyproject.toml                          # Зависимости и сборка (Poetry)
├── run_test.sbatch                         # SLURM-скрипт для основного теста
├── run_test_RPD.sbatch                     # SLURM-скрипт для Taguchi/RPD
│
├── gea_gqap_adaptive_python/
│   ├── datasets/                           # Датасеты GQAP (24 файла: T1–T14, c*)
│   │
│   ├── gea_gqap_adaptive_python/           # Основной Python-пакет
│   │   ├── __init__.py                     # Публичный API пакета
│   │   ├── models.py                       # Датаклассы: Model, AlgorithmConfig,
│   │   │                                   #   AdaptiveAlgorithmConfig, результаты
│   │   ├── model_loader.py                 # Загрузка датасетов из .m-файлов
│   │   ├── algorithm.py                    # Неадаптивный run_ga (GA / GEA_1-3 / GEA)
│   │   ├── algorithm_adaptive.py           # Адаптивный run_adaptive_ga + дедупликация
│   │   ├── operators.py                    # Скрещивание, мутация, mask_mutation,
│   │   │                                   #   roulette_wheel_selection, analyze_perm
│   │   ├── heuristics.py                   # Начальное решение (heuristic2)
│   │   └── utils.py                        # evaluate_permutation и прочие утилиты
│   │
│   └── tests/
│       ├── run_test/                  # Основной сравнительный тест
│       │   ├── run_comparison_test.py      # Точка входа
│       │   ├── test_config.json            # Параметры запуска (создать вручную)
│       │   ├── plot_cost_evolution.py      # График динамики best_cost
│       │   ├── plot_lambda_evolution.py    # График эволюции лямбда-параметров
│       │   ├── create_excel_report.py      # Генерация Excel из готовых JSON
│       │   └── results/                    # Выходные JSON и Excel
│       │
│       └── RPD/                            # Настройка параметров методом Тагути
│           ├── run_rpd_tune_all_sheets.py  # Точка входа для RPD-подбора
│           ├── taguchi_config_RPD.json     # Ортогональные таблицы Тагути L27
│           ├── rpd_utils.py                # RPD-метрика (аналог RPD.m из MATLAB)
│           ├── plot_rpd_from_json.py       # Визуализация RPD-результатов
│           └── test_rpd_math.py            # Юнит-тест вычисления RPD
│
└── Metaheuristics_GEA/                     # Оригинальная MATLAB-реализация GEA
    └── Algorithm/                          # .m-файлы алгоритма
    └── Problem/Generalized_Quadratic/      # .m-файлы задачи и данных
```

### Алгоритмические варианты

| Тип | Адаптивный | Дедупликация |
|---|---|---|
| `adaptive` | да | нет |
| `non_adaptive` | нет | нет |
| `adaptive_wo_duplicates` | да | да |
| `non_adaptive_wo_duplicates` | нет | да |

**Адаптация** — динамическое обновление весов операторов (λ) на каждой итерации по среднему улучшению δ:

```
λ_new = clamp(λ + α · mean(δ), λ_min, λ_max)
```

**Дедупликация** — после формирования пула потомков из новой популяции убираются хромосомы с одинаковым генотипом; недостающие особи добавляются мутациями от лучшего решения.

### Модели (сценарии)

| Модель | Сценарий 1 | Сценарий 2 | Сценарий 3 |
|---|---|---|---|
| GA | — | — | — |
| GEA_1 | да | — | — |
| GEA_2 | — | да | — |
| GEA_3 | — | — | да |
| GEA | да | да | да |

### Датасеты

24 экземпляра GQAP в формате `.m` (MATLAB-синтаксис):
- **c instances** — небольшие задачи
- **T1–T14** — крупные задачи

---

## RPD — подбор параметров методом Тагути

RPD (Relative Percentage Deviation) используется как метрика качества при поиске оптимальных параметров алгоритма.

### Запуск локально

```bash
poetry run python gea_gqap_adaptive_python/tests/RPD/run_rpd_tune_all_sheets.py
```

### Запуск через SLURM

```bash
sbatch run_test_RPD.sbatch
```

### Переменные окружения для RPD

| Переменная | По умолчанию | Описание |
|---|---|---|
| `NUM_WORKERS` | 16 | Параллельных процессов |
| `RPD_NUM_WORKERS` | 16 | Воркеры внутри RPD-цикла |
| `RPD_EVAL_MODELS` | `GA,GEA_1,GEA_2,GEA_3,GEA` | Модели для оценки |
| `RPD_EVAL_TYPES` | все 4 типа | Типы алгоритмов |
| `RPD_BLOCKS` | `adaptive,base` | Блоки Тагути |
| `RPD_NUM_RUNS` | 5 | Прогонов на точку таблицы |
| `RPD_ITERATIONS` | 1000 | Итераций алгоритма |
| `RPD_TIME_LIMIT` | 1000 | Лимит времени (с) |

### Как работает

1. Читает `taguchi_config_RPD.json` — ортогональные таблицы Тагути L27 для каждой модели (GA, GEA_1, GEA_2, GEA_3, GEA), по два блока: `base` (6 параметров) и `adaptive` (9 параметров с добавлением α, λ_min, λ_max).
2. Для каждой строки таблицы прогоняет алгоритм `RPD_NUM_RUNS` раз на нескольких датасетах.
3. Вычисляет RPD по формуле: `RPD = (cost - best_known) / best_known`.
4. Определяет оптимальные уровни каждого параметра по методу Тагути (S/N ratio).
5. Сохраняет результаты в JSON и Excel.

### Визуализация

```bash
poetry run python gea_gqap_adaptive_python/tests/RPD/plot_rpd_from_json.py
```

### Проверка RPD-метрики

```bash
poetry run python gea_gqap_adaptive_python/tests/RPD/test_rpd_math.py
```

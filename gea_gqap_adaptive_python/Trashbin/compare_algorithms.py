#!/usr/bin/env python3
"""
Скрипт для сравнения адаптивного и неадаптивного алгоритмов GEA для GQAP.
Обрабатывает все датасеты из папки datasets.
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Union

import numpy as np

# Добавляем пути к обоим проектам
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "GEA_GQAP_Python"))

from gea_gqap_adaptive_python import (
    AdaptiveAlgorithmConfig,
    run_adaptive_ga,
    save_results_to_json,
    load_model,
    list_available_models,
)
from gea_gqap_python.algorithm import run_ga, AlgorithmConfig


def run_comparison_for_dataset(
    model_name: str,
    iterations: int,
    population_size: int = 120,
) -> Dict[str, Any]:
    """Запускает сравнение для одного датасета с заданным количеством итераций."""
    model = load_model(model_name)

    # Неадаптивный алгоритм
    non_adaptive_config = AlgorithmConfig(
        iterations=iterations,
        population_size=population_size,
        crossover_rate=0.7,
        mutation_rate=0.3,
        scenario_crossover_rate=0.5,
        scenario_mutation_rate=0.2,
        p_fixed_x=0.9,
        p_scenario1=0.3,
        p_scenario2=0.3,
        p_scenario3=0.5,
        mask_mutation_index=2,
        time_limit=1200.0,
    )

    non_adaptive_result = run_ga(model, config=non_adaptive_config)

    # Адаптивный алгоритм
    adaptive_config = AdaptiveAlgorithmConfig(
        iterations=iterations,
        population_size=population_size,
        crossover_rate=0.7,
        mutation_rate=0.3,
        scenario_crossover_rate=0.5,
        scenario_mutation_rate=0.2,
        p_fixed_x=0.9,
        p_scenario1=0.3,
        p_scenario2=0.3,
        p_scenario3=0.5,
        mask_mutation_index=2,
        time_limit=1200.0,
        adaptive_epsilon=1e-5,
        adaptive_alpha=0.1,
        adaptive_lambda_min=0.4,
        adaptive_lambda_max=1.5,
    )

    adaptive_result = run_adaptive_ga(model, config=adaptive_config)

    # Вычисление улучшения
    improvement = non_adaptive_result.best_cost - adaptive_result.best_cost
    improvement_pct = (
        (improvement / non_adaptive_result.best_cost) * 100
        if non_adaptive_result.best_cost > 0
        else 0
    )

    # Финальные лямбды
    final_lambdas = None
    if adaptive_result.adaptive_stats.lambda_history:
        final_lambdas = {
            "crossover": float(adaptive_result.adaptive_stats.lambda_history[-1][0]),
            "mutation": float(adaptive_result.adaptive_stats.lambda_history[-1][1]),
            "scenario1": float(adaptive_result.adaptive_stats.lambda_history[-1][2]),
            "scenario2": float(adaptive_result.adaptive_stats.lambda_history[-1][3]),
            "scenario3": float(adaptive_result.adaptive_stats.lambda_history[-1][4]),
        }

    return {
        "iterations": iterations,
        "non_adaptive": {
            "best_cost": float(non_adaptive_result.best_cost),
            "elapsed_time": float(non_adaptive_result.elapsed_time),
            "iterations_completed": len(non_adaptive_result.stats.best_cost_trace),
        },
        "adaptive": {
            "best_cost": float(adaptive_result.best_cost),
            "elapsed_time": float(adaptive_result.elapsed_time),
            "iterations_completed": len(adaptive_result.stats.best_cost_trace),
            "final_lambdas": final_lambdas,
        },
        "comparison": {
            "improvement": float(improvement),
            "improvement_percent": float(improvement_pct),
            "better_algorithm": (
                "adaptive"
                if improvement > 0
                else "non_adaptive" if improvement < 0 else "equal"
            ),
        },
        # Сохраняем полные результаты для детального анализа
        "non_adaptive_result": non_adaptive_result,
        "adaptive_result": adaptive_result,
        "non_adaptive_config": non_adaptive_config,
        "adaptive_config": adaptive_config,
    }


def save_dataset_comparison_json(
    model_name: str,
    result_100: Dict[str, Any],
    result_1500: Dict[str, Any],
    result_3000: Dict[str, Any],
    output_dir: Path,
    timestamp: str,
) -> Path:
    """Сохраняет JSON с сравнением для одного датасета (100, 1500 и 3000 итераций)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{model_name}_comparison_{timestamp}.json"

    # Сохраняем детальные результаты адаптивного алгоритма
    adaptive_json_100 = save_results_to_json(
        result_100["adaptive_result"], model_name, output_dir, result_100["adaptive_config"]
    )
    adaptive_json_1500 = save_results_to_json(
        result_1500["adaptive_result"], model_name, output_dir, result_1500["adaptive_config"]
    )
    adaptive_json_3000 = save_results_to_json(
        result_3000["adaptive_result"], model_name, output_dir, result_3000["adaptive_config"]
    )

    # Сохраняем детальные результаты неадаптивного алгоритма
    na_result_100 = result_100["non_adaptive_result"]
    na_config_100 = result_100["non_adaptive_config"]
    na_json_100 = output_dir / f"{model_name}_nonadaptive_100iter_{timestamp}.json"
    with na_json_100.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "model_name": model_name,
                "iterations": 100,
                "timestamp": timestamp,
                "config": {
                    "iterations": na_config_100.iterations,
                    "population_size": na_config_100.population_size,
                    "crossover_rate": na_config_100.crossover_rate,
                    "mutation_rate": na_config_100.mutation_rate,
                },
                "summary": {
                    "best_cost": float(na_result_100.best_cost),
                    "elapsed_time": float(na_result_100.elapsed_time),
                    "iterations_completed": len(na_result_100.stats.best_cost_trace),
                },
                "iterations": [
                    {
                        "iteration": i + 1,
                        "best_cost": float(cost),
                        "contribution_rate": {
                            "previous": float(contrib[0]),
                            "crossover": float(contrib[1]),
                            "mutation": float(contrib[2]),
                            "scenario": float(contrib[3]),
                        },
                    }
                    for i, (cost, contrib) in enumerate(
                        zip(
                            na_result_100.stats.best_cost_trace,
                            na_result_100.stats.contribution_rate,
                        )
                    )
                ],
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    na_result_1500 = result_1500["non_adaptive_result"]
    na_config_1500 = result_1500["non_adaptive_config"]
    na_json_1500 = output_dir / f"{model_name}_nonadaptive_1500iter_{timestamp}.json"
    with na_json_1500.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "model_name": model_name,
                "iterations": 1500,
                "timestamp": timestamp,
                "config": {
                    "iterations": na_config_1500.iterations,
                    "population_size": na_config_1500.population_size,
                    "crossover_rate": na_config_1500.crossover_rate,
                    "mutation_rate": na_config_1500.mutation_rate,
                },
                "summary": {
                    "best_cost": float(na_result_1500.best_cost),
                    "elapsed_time": float(na_result_1500.elapsed_time),
                    "iterations_completed": len(na_result_1500.stats.best_cost_trace),
                },
                "iterations": [
                    {
                        "iteration": i + 1,
                        "best_cost": float(cost),
                        "contribution_rate": {
                            "previous": float(contrib[0]),
                            "crossover": float(contrib[1]),
                            "mutation": float(contrib[2]),
                            "scenario": float(contrib[3]),
                        },
                    }
                    for i, (cost, contrib) in enumerate(
                        zip(
                            na_result_1500.stats.best_cost_trace,
                            na_result_1500.stats.contribution_rate,
                        )
                    )
                ],
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    na_result_3000 = result_3000["non_adaptive_result"]
    na_config_3000 = result_3000["non_adaptive_config"]
    na_json_3000 = output_dir / f"{model_name}_nonadaptive_3000iter_{timestamp}.json"
    with na_json_3000.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "model_name": model_name,
                "iterations": 3000,
                "timestamp": timestamp,
                "config": {
                    "iterations": na_config_3000.iterations,
                    "population_size": na_config_3000.population_size,
                    "crossover_rate": na_config_3000.crossover_rate,
                    "mutation_rate": na_config_3000.mutation_rate,
                },
                "summary": {
                    "best_cost": float(na_result_3000.best_cost),
                    "elapsed_time": float(na_result_3000.elapsed_time),
                    "iterations_completed": len(na_result_3000.stats.best_cost_trace),
                },
                "iterations": [
                    {
                        "iteration": i + 1,
                        "best_cost": float(cost),
                        "contribution_rate": {
                            "previous": float(contrib[0]),
                            "crossover": float(contrib[1]),
                            "mutation": float(contrib[2]),
                            "scenario": float(contrib[3]),
                        },
                    }
                    for i, (cost, contrib) in enumerate(
                        zip(
                            na_result_3000.stats.best_cost_trace,
                            na_result_3000.stats.contribution_rate,
                        )
                    )
                ],
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    # Создаем итоговый JSON для датасета
    dataset_comparison = {
        "model_name": model_name,
        "timestamp": timestamp,
        "config": {
            "population_size": 120,
            "adaptive_alpha": 0.1,
        },
        "results_100_iterations": {
            "non_adaptive": {
                "best_cost": result_100["non_adaptive"]["best_cost"],
                "elapsed_time": result_100["non_adaptive"]["elapsed_time"],
                "iterations_completed": result_100["non_adaptive"]["iterations_completed"],
            },
            "adaptive": {
                "best_cost": result_100["adaptive"]["best_cost"],
                "elapsed_time": result_100["adaptive"]["elapsed_time"],
                "iterations_completed": result_100["adaptive"]["iterations_completed"],
                "final_lambdas": result_100["adaptive"]["final_lambdas"],
            },
            "comparison": result_100["comparison"],
        },
        "results_1500_iterations": {
            "non_adaptive": {
                "best_cost": result_1500["non_adaptive"]["best_cost"],
                "elapsed_time": result_1500["non_adaptive"]["elapsed_time"],
                "iterations_completed": result_1500["non_adaptive"]["iterations_completed"],
            },
            "adaptive": {
                "best_cost": result_1500["adaptive"]["best_cost"],
                "elapsed_time": result_1500["adaptive"]["elapsed_time"],
                "iterations_completed": result_1500["adaptive"]["iterations_completed"],
                "final_lambdas": result_1500["adaptive"]["final_lambdas"],
            },
            "comparison": result_1500["comparison"],
        },
        "results_3000_iterations": {
            "non_adaptive": {
                "best_cost": result_3000["non_adaptive"]["best_cost"],
                "elapsed_time": result_3000["non_adaptive"]["elapsed_time"],
                "iterations_completed": result_3000["non_adaptive"]["iterations_completed"],
            },
            "adaptive": {
                "best_cost": result_3000["adaptive"]["best_cost"],
                "elapsed_time": result_3000["adaptive"]["elapsed_time"],
                "iterations_completed": result_3000["adaptive"]["iterations_completed"],
                "final_lambdas": result_3000["adaptive"]["final_lambdas"],
            },
            "comparison": result_3000["comparison"],
        },
        "detailed_files": {
            "adaptive_100": str(adaptive_json_100.name),
            "adaptive_1500": str(adaptive_json_1500.name),
            "adaptive_3000": str(adaptive_json_3000.name),
            "nonadaptive_100": str(na_json_100.name),
            "nonadaptive_1500": str(na_json_1500.name),
            "nonadaptive_3000": str(na_json_3000.name),
        },
    }

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(dataset_comparison, f, indent=2, ensure_ascii=False)

    return output_path


def calculate_statistics(all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Вычисляет статистику по всем датасетам."""
    if not all_results:
        return {}

    improvements_100 = [r["results_100_iterations"]["comparison"]["improvement"] for r in all_results]
    improvements_pct_100 = [
        r["results_100_iterations"]["comparison"]["improvement_percent"] for r in all_results
    ]

    improvements_1500 = [
        r["results_1500_iterations"]["comparison"]["improvement"] for r in all_results
    ]
    improvements_pct_1500 = [
        r["results_1500_iterations"]["comparison"]["improvement_percent"] for r in all_results
    ]

    improvements_3000 = [
        r["results_3000_iterations"]["comparison"]["improvement"] for r in all_results
    ]
    improvements_pct_3000 = [
        r["results_3000_iterations"]["comparison"]["improvement_percent"] for r in all_results
    ]

    adaptive_better_100 = sum(
        1
        for r in all_results
        if r["results_100_iterations"]["comparison"]["better_algorithm"] == "adaptive"
    )
    adaptive_better_1500 = sum(
        1
        for r in all_results
        if r["results_1500_iterations"]["comparison"]["better_algorithm"] == "adaptive"
    )
    adaptive_better_3000 = sum(
        1
        for r in all_results
        if r["results_3000_iterations"]["comparison"]["better_algorithm"] == "adaptive"
    )

    return {
        "total_datasets": len(all_results),
        "100_iterations": {
            "adaptive_better": adaptive_better_100,
            "non_adaptive_better": len(all_results) - adaptive_better_100,
            "improvement": {
                "mean": float(np.mean(improvements_100)),
                "median": float(np.median(improvements_100)),
                "std": float(np.std(improvements_100)),
                "min": float(np.min(improvements_100)),
                "max": float(np.max(improvements_100)),
            },
            "improvement_percent": {
                "mean": float(np.mean(improvements_pct_100)),
                "median": float(np.median(improvements_pct_100)),
                "std": float(np.std(improvements_pct_100)),
                "min": float(np.min(improvements_pct_100)),
                "max": float(np.max(improvements_pct_100)),
            },
        },
        "1500_iterations": {
            "adaptive_better": adaptive_better_1500,
            "non_adaptive_better": len(all_results) - adaptive_better_1500,
            "improvement": {
                "mean": float(np.mean(improvements_1500)),
                "median": float(np.median(improvements_1500)),
                "std": float(np.std(improvements_1500)),
                "min": float(np.min(improvements_1500)),
                "max": float(np.max(improvements_1500)),
            },
            "improvement_percent": {
                "mean": float(np.mean(improvements_pct_1500)),
                "median": float(np.median(improvements_pct_1500)),
                "std": float(np.std(improvements_pct_1500)),
                "min": float(np.min(improvements_pct_1500)),
                "max": float(np.max(improvements_pct_1500)),
            },
        },
        "3000_iterations": {
            "adaptive_better": adaptive_better_3000,
            "non_adaptive_better": len(all_results) - adaptive_better_3000,
            "improvement": {
                "mean": float(np.mean(improvements_3000)),
                "median": float(np.median(improvements_3000)),
                "std": float(np.std(improvements_3000)),
                "min": float(np.min(improvements_3000)),
                "max": float(np.max(improvements_3000)),
            },
            "improvement_percent": {
                "mean": float(np.mean(improvements_pct_3000)),
                "median": float(np.median(improvements_pct_3000)),
                "std": float(np.std(improvements_pct_3000)),
                "min": float(np.min(improvements_pct_3000)),
                "max": float(np.max(improvements_pct_3000)),
            },
        },
    }


def main():
    """Главная функция - обрабатывает все датасеты."""
    # Получаем список всех датасетов
    all_models = list_available_models()
    datasets = sorted([m for m in all_models if m.startswith("c")])

    if not datasets:
        print("Не найдено датасетов для сравнения!")
        return

    print(f"\n{'='*70}")
    print(f"СРАВНЕНИЕ АЛГОРИТМОВ ДЛЯ {len(datasets)} ДАТАСЕТОВ")
    print(f"Время начала: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")

    output_dir = Path("results")
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")

    all_dataset_results = []

    for idx, dataset in enumerate(datasets, 1):
        print(f"\n[{idx}/{len(datasets)}] Обработка датасета: {dataset}")
        print("-" * 70)

        try:
            # 100 итераций
            print(f"  Запуск сравнения для 100 итераций...")
            result_100 = run_comparison_for_dataset(dataset, 100, 120)
            print(
                f"    100 iter: NA={result_100['non_adaptive']['best_cost']:.2f}, "
                f"AD={result_100['adaptive']['best_cost']:.2f}, "
                f"лучше={result_100['comparison']['better_algorithm']}"
            )

            # 1500 итераций
            print(f"  Запуск сравнения для 1500 итераций...")
            result_1500 = run_comparison_for_dataset(dataset, 1500, 120)
            print(
                f"    1500 iter: NA={result_1500['non_adaptive']['best_cost']:.2f}, "
                f"AD={result_1500['adaptive']['best_cost']:.2f}, "
                f"лучше={result_1500['comparison']['better_algorithm']}"
            )

            # 3000 итераций
            print(f"  Запуск сравнения для 3000 итераций...")
            result_3000 = run_comparison_for_dataset(dataset, 3000, 120)
            print(
                f"    3000 iter: NA={result_3000['non_adaptive']['best_cost']:.2f}, "
                f"AD={result_3000['adaptive']['best_cost']:.2f}, "
                f"лучше={result_3000['comparison']['better_algorithm']}"
            )

            # Сохраняем JSON для датасета
            dataset_json_path = save_dataset_comparison_json(
                dataset, result_100, result_1500, result_3000, output_dir, timestamp
            )
            print(f"  ✓ Результаты сохранены: {dataset_json_path.name}")

            # Сохраняем для итогового сравнения
            all_dataset_results.append(
                {
                    "model_name": dataset,
                    "results_100_iterations": {
                        "non_adaptive": result_100["non_adaptive"],
                        "adaptive": result_100["adaptive"],
                        "comparison": result_100["comparison"],
                    },
                    "results_1500_iterations": {
                        "non_adaptive": result_1500["non_adaptive"],
                        "adaptive": result_1500["adaptive"],
                        "comparison": result_1500["comparison"],
                    },
                    "results_3000_iterations": {
                        "non_adaptive": result_3000["non_adaptive"],
                        "adaptive": result_3000["adaptive"],
                        "comparison": result_3000["comparison"],
                    },
                }
            )

        except Exception as e:
            print(f"  ✗ Ошибка при обработке {dataset}: {e}")
            import traceback

            traceback.print_exc()
            continue

    # Создаем итоговое сравнение всех датасетов
    statistics = calculate_statistics(all_dataset_results)

    final_comparison = {
        "timestamp": timestamp,
        "config": {
            "population_size": 120,
            "adaptive_alpha": 0.1,
            "iterations_tested": [100, 1500, 3000],
        },
        "datasets": all_dataset_results,
        "statistics": statistics,
        "summary": {
            "100_iterations": {
                "adaptive_better_count": statistics["100_iterations"]["adaptive_better"],
                "non_adaptive_better_count": statistics["100_iterations"]["non_adaptive_better"],
                "mean_improvement_percent": statistics["100_iterations"]["improvement_percent"][
                    "mean"
                ],
                "median_improvement_percent": statistics["100_iterations"]["improvement_percent"][
                    "median"
                ],
            },
            "1500_iterations": {
                "adaptive_better_count": statistics["1500_iterations"]["adaptive_better"],
                "non_adaptive_better_count": statistics["1500_iterations"]["non_adaptive_better"],
                "mean_improvement_percent": statistics["1500_iterations"]["improvement_percent"][
                    "mean"
                ],
                "median_improvement_percent": statistics["1500_iterations"]["improvement_percent"][
                    "median"
                ],
            },
            "3000_iterations": {
                "adaptive_better_count": statistics["3000_iterations"]["adaptive_better"],
                "non_adaptive_better_count": statistics["3000_iterations"]["non_adaptive_better"],
                "mean_improvement_percent": statistics["3000_iterations"]["improvement_percent"][
                    "mean"
                ],
                "median_improvement_percent": statistics["3000_iterations"]["improvement_percent"][
                    "median"
                ],
            },
        },
    }

    # Сохраняем итоговый файл
    final_path = output_dir / f"all_datasets_final_comparison_{timestamp}.json"
    with final_path.open("w", encoding="utf-8") as f:
        json.dump(final_comparison, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*70}")
    print("ВСЕ СРАВНЕНИЯ ЗАВЕРШЕНЫ")
    print(f"{'='*70}")
    print(f"\nИтоговый файл: {final_path.name}")
    print(f"Обработано датасетов: {len(all_dataset_results)}/{len(datasets)}")

    # Выводим краткую статистику
    print("\n" + "=" * 70)
    print("КРАТКАЯ СТАТИСТИКА")
    print("=" * 70)

    for iterations in [100, 1500, 3000]:
        stats_key = f"{iterations}_iterations"
        stats = statistics[stats_key]
        print(f"\n{iterations} итераций:")
        print(f"  Всего датасетов: {statistics['total_datasets']}")
        print(f"  Адаптивный лучше: {stats['adaptive_better']}")
        print(f"  Неадаптивный лучше: {stats['non_adaptive_better']}")
        print(f"  Среднее улучшение: {stats['improvement_percent']['mean']:.2f}%")
        print(f"  Медианное улучшение: {stats['improvement_percent']['median']:.2f}%")
        print(f"  Мин/Макс: {stats['improvement_percent']['min']:.2f}% / {stats['improvement_percent']['max']:.2f}%")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()

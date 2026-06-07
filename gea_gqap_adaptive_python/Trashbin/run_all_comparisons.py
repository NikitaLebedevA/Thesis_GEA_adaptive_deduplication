#!/usr/bin/env python3
"""
Запускает сравнение адаптивного и неадаптивного алгоритмов для всех датасетов.
Сохраняет результаты для 100 и 1500 итераций в отдельных JSON файлах.
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple, Union

import numpy as np

# Добавляем пути
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


def run_single_comparison(
    model_name: str,
    iterations: int,
    population_size: int = 120,
) -> Tuple[Dict[str, Any], Any, Any, Any, Any, Any]:
    """Запускает сравнение для одного датасета с заданным количеством итераций.
    
    Returns:
        (summary_dict, model, non_adaptive_result, adaptive_result, non_adaptive_config, adaptive_config)
    """
    print(f"\n{'='*70}")
    print(f"Модель: {model_name}, Итераций: {iterations}")
    print(f"{'='*70}")

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

    print("Запуск неадаптивного алгоритма...")
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

    print("Запуск адаптивного алгоритма...")
    adaptive_result = run_adaptive_ga(model, config=adaptive_config)

    # Вычисление улучшения
    improvement = non_adaptive_result.best_cost - adaptive_result.best_cost
    improvement_pct = (improvement / non_adaptive_result.best_cost) * 100 if non_adaptive_result.best_cost > 0 else 0

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

    summary = {
        "model_name": model_name,
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
            "better_algorithm": "adaptive" if improvement > 0 else "non_adaptive" if improvement < 0 else "equal",
        },
    }

    return summary, model, non_adaptive_result, adaptive_result, non_adaptive_config, adaptive_config


def save_detailed_results(
    model_name: str,
    iterations: int,
    model: Any,
    non_adaptive_result: Any,
    adaptive_result: Any,
    non_adaptive_config: Any,
    adaptive_config: Any,
    output_dir: Path,
    timestamp: str,
) -> None:
    """Сохраняет детальные результаты для одного датасета и количества итераций."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Сохраняем адаптивные результаты
    adaptive_json_path = save_results_to_json(
        adaptive_result, model_name, output_dir, adaptive_config
    )

    # Сохраняем неадаптивные результаты
    non_adaptive_json_path = output_dir / f"{model_name}_nonadaptive_{iterations}iter_{timestamp}.json"
    non_adaptive_data = {
        "model_name": model_name,
        "iterations": iterations,
        "timestamp": timestamp,
        "config": {
            "iterations": non_adaptive_config.iterations,
            "population_size": non_adaptive_config.population_size,
            "crossover_rate": non_adaptive_config.crossover_rate,
            "mutation_rate": non_adaptive_config.mutation_rate,
        },
        "summary": {
            "best_cost": float(non_adaptive_result.best_cost),
            "elapsed_time": float(non_adaptive_result.elapsed_time),
            "iterations_completed": len(non_adaptive_result.stats.best_cost_trace),
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
                    non_adaptive_result.stats.best_cost_trace,
                    non_adaptive_result.stats.contribution_rate,
                )
            )
        ],
    }

    with non_adaptive_json_path.open("w", encoding="utf-8") as f:
        json.dump(non_adaptive_data, f, indent=2, ensure_ascii=False)


def run_all_comparisons(
    datasets: List[str],
    output_dir: Union[Path, str] = "results",
    population_size: int = 120,
) -> Dict[str, Any]:
    """Запускает сравнение для всех датасетов с 100 и 1500 итерациями."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    all_results_100 = []
    all_results_1500 = []

    print(f"\n{'='*70}")
    print(f"ЗАПУСК СРАВНЕНИЙ ДЛЯ {len(datasets)} ДАТАСЕТОВ")
    print(f"Время начала: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")

    for idx, dataset in enumerate(datasets, 1):
        print(f"\n[{idx}/{len(datasets)}] Обработка датасета: {dataset}")

        try:
            # 100 итераций
            result_100, model_100, na_result_100, ad_result_100, na_config_100, ad_config_100 = run_single_comparison(
                dataset, 100, population_size
            )
            all_results_100.append(result_100)
            save_detailed_results(
                dataset, 100, model_100, na_result_100, ad_result_100, 
                na_config_100, ad_config_100, output_dir, timestamp
            )

            # 1500 итераций
            result_1500, model_1500, na_result_1500, ad_result_1500, na_config_1500, ad_config_1500 = run_single_comparison(
                dataset, 1500, population_size
            )
            all_results_1500.append(result_1500)
            save_detailed_results(
                dataset, 1500, model_1500, na_result_1500, ad_result_1500,
                na_config_1500, ad_config_1500, output_dir, timestamp
            )

            print(f"✓ {dataset} завершен")

        except Exception as e:
            print(f"✗ Ошибка при обработке {dataset}: {e}")
            continue

    # Создаем итоговое сравнение
    summary = {
        "timestamp": timestamp,
        "config": {
            "population_size": population_size,
            "adaptive_alpha": 0.1,
        },
        "results_100_iterations": {
            "datasets": all_results_100,
            "statistics": calculate_statistics(all_results_100),
        },
        "results_1500_iterations": {
            "datasets": all_results_1500,
            "statistics": calculate_statistics(all_results_1500),
        },
    }

    # Сохраняем итоговое сравнение
    summary_path = output_dir / f"all_datasets_comparison_{timestamp}.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*70}")
    print(f"ВСЕ СРАВНЕНИЯ ЗАВЕРШЕНЫ")
    print(f"Итоговый файл: {summary_path}")
    print(f"{'='*70}")

    return summary


def calculate_statistics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Вычисляет статистику по всем датасетам."""
    if not results:
        return {}

    improvements = [r["comparison"]["improvement"] for r in results]
    improvements_pct = [r["comparison"]["improvement_percent"] for r in results]

    adaptive_better = sum(1 for r in results if r["comparison"]["better_algorithm"] == "adaptive")
    non_adaptive_better = sum(1 for r in results if r["comparison"]["better_algorithm"] == "non_adaptive")
    equal = sum(1 for r in results if r["comparison"]["better_algorithm"] == "equal")

    adaptive_times = [r["adaptive"]["elapsed_time"] for r in results]
    non_adaptive_times = [r["non_adaptive"]["elapsed_time"] for r in results]

    return {
        "total_datasets": len(results),
        "adaptive_better": adaptive_better,
        "non_adaptive_better": non_adaptive_better,
        "equal": equal,
        "improvement": {
            "mean": float(np.mean(improvements)),
            "median": float(np.median(improvements)),
            "std": float(np.std(improvements)),
            "min": float(np.min(improvements)),
            "max": float(np.max(improvements)),
        },
        "improvement_percent": {
            "mean": float(np.mean(improvements_pct)),
            "median": float(np.median(improvements_pct)),
            "std": float(np.std(improvements_pct)),
            "min": float(np.min(improvements_pct)),
            "max": float(np.max(improvements_pct)),
        },
        "time_ratio": {
            "mean": float(np.mean([a / n for a, n in zip(adaptive_times, non_adaptive_times)])),
            "adaptive_mean": float(np.mean(adaptive_times)),
            "non_adaptive_mean": float(np.mean(non_adaptive_times)),
        },
    }


if __name__ == "__main__":
    # Получаем список всех датасетов
    all_models = list_available_models()
    # Фильтруем только датасеты c* (исключаем T*)
    datasets = sorted([m for m in all_models if m.startswith("c")])

    print(f"Найдено {len(datasets)} датасетов: {', '.join(datasets)}")

    if not datasets:
        print("Не найдено датасетов для сравнения!")
        sys.exit(1)

    summary = run_all_comparisons(
        datasets=datasets,
        output_dir="results",
        population_size=120,
    )

    # Выводим краткую статистику
    print("\n" + "="*70)
    print("КРАТКАЯ СТАТИСТИКА")
    print("="*70)

    for iterations in [100, 1500]:
        stats = summary[f"results_{iterations}_iterations"]["statistics"]
        print(f"\n{iterations} итераций:")
        print(f"  Всего датасетов: {stats['total_datasets']}")
        print(f"  Адаптивный лучше: {stats['adaptive_better']}")
        print(f"  Неадаптивный лучше: {stats['non_adaptive_better']}")
        print(f"  Среднее улучшение: {stats['improvement_percent']['mean']:.2f}%")
        print(f"  Медианное улучшение: {stats['improvement_percent']['median']:.2f}%")


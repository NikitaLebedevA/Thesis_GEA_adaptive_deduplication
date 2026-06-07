#!/usr/bin/env python3
"""
Создает JSON файл со статистикой побед адаптивного алгоритма.
Для каждого числа итераций считает:
1. В скольких датасетах победил adaptive алгоритм (по best_cost)
2. В скольких датасетах у adaptive затраты на прогон были меньше (по elapsed_time)
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

def create_win_statistics(json_path: Path) -> Dict[str, Any]:
    """Создает статистику побед адаптивного алгоритма."""
    with json_path.open('r', encoding='utf-8') as f:
        data = json.load(f)
    
    datasets = data.get('datasets', [])
    
    if not datasets:
        print("Нет данных для анализа!")
        return {}
    
    statistics = {
        "source_file": str(json_path.name),
        "timestamp": data.get('timestamp', 'N/A'),
        "total_datasets": len(datasets),
        "iterations": {}
    }
    
    for iterations in [100, 1500, 3000]:
        key = f"results_{iterations}_iterations"
        
        # Подсчет побед по best_cost
        adaptive_wins_best_cost = 0
        for dataset in datasets:
            result = dataset.get(key, {})
            comparison = result.get('comparison', {})
            better_algorithm = comparison.get('better_algorithm', '')
            if better_algorithm == 'adaptive':
                adaptive_wins_best_cost += 1
        
        # Подсчет побед по elapsed_time
        adaptive_wins_elapsed_time = 0
        for dataset in datasets:
            result = dataset.get(key, {})
            non_adaptive_time = result.get('non_adaptive', {}).get('elapsed_time', float('inf'))
            adaptive_time = result.get('adaptive', {}).get('elapsed_time', float('inf'))
            if adaptive_time < non_adaptive_time:
                adaptive_wins_elapsed_time += 1
        
        statistics["iterations"][f"{iterations}_iterations"] = {
            "adaptive_wins_best_cost": adaptive_wins_best_cost,
            "adaptive_wins_best_cost_percent": round(adaptive_wins_best_cost / len(datasets) * 100, 1),
            "adaptive_wins_elapsed_time": adaptive_wins_elapsed_time,
            "adaptive_wins_elapsed_time_percent": round(adaptive_wins_elapsed_time / len(datasets) * 100, 1),
            "total_datasets": len(datasets)
        }
    
    return statistics


def main():
    """Главная функция."""
    if len(sys.argv) > 1:
        json_path = Path(sys.argv[1])
    else:
        # Ищем последний файл сравнения
        results_dir = Path(__file__).parent / "results"
        comparison_files = sorted(results_dir.glob("all_datasets_final_comparison_*.json"), reverse=True)
        if not comparison_files:
            print("Не найден файл сравнения!")
            print("Использование: python3 create_win_statistics.py [путь_к_json]")
            sys.exit(1)
        json_path = comparison_files[0]
        print(f"Используется файл: {json_path.name}\n")
    
    print("Создание статистики побед...")
    statistics = create_win_statistics(json_path)
    
    # Сохраняем в JSON
    output_dir = json_path.parent
    output_path = output_dir / f"adaptive_wins_statistics_{statistics['timestamp']}.json"
    
    with output_path.open('w', encoding='utf-8') as f:
        json.dump(statistics, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Статистика сохранена в: {output_path.name}")
    print("\n" + "=" * 70)
    print("СТАТИСТИКА ПОБЕД АДАПТИВНОГО АЛГОРИТМА")
    print("=" * 70)
    
    for iterations in [100, 1500, 3000]:
        key = f"{iterations}_iterations"
        stats = statistics["iterations"][key]
        print(f"\n{iterations} итераций:")
        print(f"  Побед по best_cost:        {stats['adaptive_wins_best_cost']}/{stats['total_datasets']} ({stats['adaptive_wins_best_cost_percent']}%)")
        print(f"  Побед по elapsed_time:     {stats['adaptive_wins_elapsed_time']}/{stats['total_datasets']} ({stats['adaptive_wins_elapsed_time_percent']}%)")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()







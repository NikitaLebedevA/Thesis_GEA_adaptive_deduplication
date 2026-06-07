#!/usr/bin/env python3
"""Проверяет прогресс выполнения сравнений и показывает статистику."""

import json
from pathlib import Path

results_dir = Path("results")

# Ищем итоговый файл сравнения
summary_files = sorted(results_dir.glob("all_datasets_comparison_*.json"), reverse=True)

if summary_files:
    print(f"Найден итоговый файл: {summary_files[0].name}")
    with summary_files[0].open() as f:
        data = json.load(f)
    
    print("\n" + "="*70)
    print("ИТОГОВАЯ СТАТИСТИКА")
    print("="*70)
    
    for iterations in [100, 1500]:
        stats = data[f"results_{iterations}_iterations"]["statistics"]
        print(f"\n{iterations} итераций:")
        print(f"  Всего датасетов: {stats['total_datasets']}")
        print(f"  Адаптивный лучше: {stats['adaptive_better']}")
        print(f"  Неадаптивный лучше: {stats['non_adaptive_better']}")
        print(f"  Равны: {stats['equal']}")
        print(f"  Среднее улучшение: {stats['improvement_percent']['mean']:.2f}%")
        print(f"  Медианное улучшение: {stats['improvement_percent']['median']:.2f}%")
        print(f"  Мин/Макс улучшение: {stats['improvement_percent']['min']:.2f}% / {stats['improvement_percent']['max']:.2f}%")
        
        print(f"\n  Детали по датасетам:")
        for dataset_result in data[f"results_{iterations}_iterations"]["datasets"]:
            model = dataset_result["model_name"]
            improvement = dataset_result["comparison"]["improvement_percent"]
            better = dataset_result["comparison"]["better_algorithm"]
            print(f"    {model}: {improvement:+.2f}% ({better})")
else:
    # Подсчитываем созданные файлы
    adaptive_files = list(results_dir.glob("*_adaptive_*.json"))
    nonadaptive_files = list(results_dir.glob("*_nonadaptive_*iter_*.json"))
    
    print(f"Итоговый файл еще не создан.")
    print(f"Создано файлов:")
    print(f"  Адаптивных: {len(adaptive_files)}")
    print(f"  Неадаптивных: {len(nonadaptive_files)}")
    print(f"  Всего: {len(adaptive_files) + len(nonadaptive_files)}")
    print(f"\nОжидается: 40 файлов (10 датасетов × 2 алгоритма × 2 итерации)")







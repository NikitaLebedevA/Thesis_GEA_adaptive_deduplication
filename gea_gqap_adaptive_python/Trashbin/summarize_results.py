#!/usr/bin/env python3
"""
Скрипт для суммирования результатов сравнения алгоритмов.
Подсчитывает статистику по best_cost и elapsed_time отдельно для 100 и 1500 итераций.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

def analyze_comparison(json_path: Path, save_json: bool = True):
    """Анализирует файл сравнения и выводит статистику."""
    with json_path.open('r', encoding='utf-8') as f:
        data = json.load(f)
    
    datasets = data.get('datasets', [])
    
    if not datasets:
        print("Нет данных для анализа!")
        return None
    
    print("=" * 80)
    print("СТАТИСТИКА СРАВНЕНИЯ АЛГОРИТМОВ")
    print("=" * 80)
    print(f"Всего датасетов: {len(datasets)}")
    print(f"Время создания: {data.get('timestamp', 'N/A')}")
    print()
    
    # Структура для сохранения в JSON
    summary_data = {
        "source_file": str(json_path.name),
        "timestamp": data.get('timestamp', 'N/A'),
        "total_datasets": len(datasets),
        "best_cost_metric": {},
        "elapsed_time_metric": {}
    }
    
    # Статистика по best_cost
    print("=" * 80)
    print("МЕТРИКА: best_cost (лучшая стоимость - чем меньше, тем лучше)")
    print("=" * 80)
    
    best_cost_summary = {}
    
    for iterations in [100, 1500, 3000]:
        key = f"results_{iterations}_iterations"
        print(f"\n{iterations} ИТЕРАЦИЙ:")
        print("-" * 80)
        
        adaptive_wins = 0
        non_adaptive_wins = 0
        equal = 0
        
        wins_details = []
        all_details = []
        
        for dataset in datasets:
            model_name = dataset['model_name']
            result = dataset[key]
            
            na_cost = result['non_adaptive']['best_cost']
            ad_cost = result['adaptive']['best_cost']
            
            if ad_cost < na_cost:
                adaptive_wins += 1
                improvement = ((na_cost - ad_cost) / na_cost) * 100
                detail = {
                    'model': model_name,
                    'winner': 'adaptive',
                    'na_cost': na_cost,
                    'ad_cost': ad_cost,
                    'improvement_pct': improvement
                }
                wins_details.append(detail)
                all_details.append(detail)
            elif na_cost < ad_cost:
                non_adaptive_wins += 1
                improvement = ((ad_cost - na_cost) / ad_cost) * 100
                detail = {
                    'model': model_name,
                    'winner': 'non_adaptive',
                    'na_cost': na_cost,
                    'ad_cost': ad_cost,
                    'improvement_pct': improvement
                }
                wins_details.append(detail)
                all_details.append(detail)
            else:
                equal += 1
                detail = {
                    'model': model_name,
                    'winner': 'equal',
                    'na_cost': na_cost,
                    'ad_cost': ad_cost,
                    'improvement_pct': 0
                }
                all_details.append(detail)
        
        adaptive_count = adaptive_wins
        non_adaptive_count = non_adaptive_wins
        equal_count = equal
        
        print(f"  Адаптивный алгоритм лучше:     {adaptive_count:2d} ({adaptive_count/len(datasets)*100:.1f}%)")
        print(f"  Неадаптивный алгоритм лучше:    {non_adaptive_count:2d} ({non_adaptive_count/len(datasets)*100:.1f}%)")
        print(f"  Равны:                          {equal_count:2d} ({equal_count/len(datasets)*100:.1f}%)")
        
        # Детали побед
        adaptive_details = [d for d in all_details if d['winner'] == 'adaptive']
        non_adaptive_details = [d for d in all_details if d['winner'] == 'non_adaptive']
        equal_details = [d for d in all_details if d['winner'] == 'equal']
        
        avg_adaptive_improvement = sum(d['improvement_pct'] for d in adaptive_details) / len(adaptive_details) if adaptive_details else 0
        avg_non_adaptive_improvement = sum(d['improvement_pct'] for d in non_adaptive_details) / len(non_adaptive_details) if non_adaptive_details else 0
        
        if adaptive_details:
            print(f"\n  Детали побед адаптивного алгоритма:")
            for d in sorted(adaptive_details, key=lambda x: x['improvement_pct'], reverse=True):
                print(f"    {d['model']:10s}: {d['na_cost']:12.2f} → {d['ad_cost']:12.2f} "
                      f"({d['improvement_pct']:+.2f}%)")
            print(f"    Среднее улучшение: {avg_adaptive_improvement:.2f}%")
        
        if non_adaptive_details:
            print(f"\n  Детали побед неадаптивного алгоритма:")
            for d in sorted(non_adaptive_details, key=lambda x: x['improvement_pct'], reverse=True):
                print(f"    {d['model']:10s}: {d['ad_cost']:12.2f} → {d['na_cost']:12.2f} "
                      f"({d['improvement_pct']:+.2f}%)")
            print(f"    Среднее улучшение: {avg_non_adaptive_improvement:.2f}%")
        
        # Сохраняем в структуру
        best_cost_summary[f"{iterations}_iterations"] = {
            "adaptive_wins": adaptive_count,
            "adaptive_wins_percent": round(adaptive_count/len(datasets)*100, 1),
            "non_adaptive_wins": non_adaptive_count,
            "non_adaptive_wins_percent": round(non_adaptive_count/len(datasets)*100, 1),
            "equal": equal_count,
            "equal_percent": round(equal_count/len(datasets)*100, 1),
            "average_adaptive_improvement_pct": round(avg_adaptive_improvement, 2),
            "average_non_adaptive_improvement_pct": round(avg_non_adaptive_improvement, 2),
            "adaptive_wins_details": [
                {
                    "model": d['model'],
                    "non_adaptive_cost": round(d['na_cost'], 2),
                    "adaptive_cost": round(d['ad_cost'], 2),
                    "improvement_pct": round(d['improvement_pct'], 2)
                }
                for d in sorted(adaptive_details, key=lambda x: x['improvement_pct'], reverse=True)
            ],
            "non_adaptive_wins_details": [
                {
                    "model": d['model'],
                    "non_adaptive_cost": round(d['na_cost'], 2),
                    "adaptive_cost": round(d['ad_cost'], 2),
                    "improvement_pct": round(d['improvement_pct'], 2)
                }
                for d in sorted(non_adaptive_details, key=lambda x: x['improvement_pct'], reverse=True)
            ],
            "all_datasets": [
                {
                    "model": d['model'],
                    "winner": d['winner'],
                    "non_adaptive_cost": round(d['na_cost'], 2),
                    "adaptive_cost": round(d['ad_cost'], 2),
                    "improvement_pct": round(d['improvement_pct'], 2)
                }
                for d in all_details
            ]
        }
    
    summary_data["best_cost_metric"] = best_cost_summary
    
    # Статистика по elapsed_time
    print("\n" + "=" * 80)
    print("МЕТРИКА: elapsed_time (время выполнения - чем меньше, тем лучше)")
    print("=" * 80)
    
    elapsed_time_summary = {}
    
    for iterations in [100, 1500, 3000]:
        key = f"results_{iterations}_iterations"
        print(f"\n{iterations} ИТЕРАЦИЙ:")
        print("-" * 80)
        
        adaptive_wins = 0
        non_adaptive_wins = 0
        equal = 0
        
        wins_details = []
        all_details = []
        
        for dataset in datasets:
            model_name = dataset['model_name']
            result = dataset[key]
            
            na_time = result['non_adaptive']['elapsed_time']
            ad_time = result['adaptive']['elapsed_time']
            
            if ad_time < na_time:
                adaptive_wins += 1
                improvement = ((na_time - ad_time) / na_time) * 100
                detail = {
                    'model': model_name,
                    'winner': 'adaptive',
                    'na_time': na_time,
                    'ad_time': ad_time,
                    'improvement_pct': improvement
                }
                wins_details.append(detail)
                all_details.append(detail)
            elif na_time < ad_time:
                non_adaptive_wins += 1
                improvement = ((ad_time - na_time) / ad_time) * 100
                detail = {
                    'model': model_name,
                    'winner': 'non_adaptive',
                    'na_time': na_time,
                    'ad_time': ad_time,
                    'improvement_pct': improvement
                }
                wins_details.append(detail)
                all_details.append(detail)
            else:
                equal += 1
                detail = {
                    'model': model_name,
                    'winner': 'equal',
                    'na_time': na_time,
                    'ad_time': ad_time,
                    'improvement_pct': 0
                }
                all_details.append(detail)
        
        adaptive_count = adaptive_wins
        non_adaptive_count = non_adaptive_wins
        equal_count = equal
        
        print(f"  Адаптивный алгоритм быстрее:   {adaptive_count:2d} ({adaptive_count/len(datasets)*100:.1f}%)")
        print(f"  Неадаптивный алгоритм быстрее:  {non_adaptive_count:2d} ({non_adaptive_count/len(datasets)*100:.1f}%)")
        print(f"  Равны:                          {equal_count:2d} ({equal_count/len(datasets)*100:.1f}%)")
        
        # Средние времена
        avg_na_time = sum(d['na_time'] for d in all_details) / len(all_details)
        avg_ad_time = sum(d['ad_time'] for d in all_details) / len(all_details)
        print(f"\n  Среднее время выполнения:")
        print(f"    Неадаптивный: {avg_na_time:.2f} с")
        print(f"    Адаптивный:   {avg_ad_time:.2f} с")
        print(f"    Отношение:    {avg_ad_time/avg_na_time:.3f}x")
        
        # Детали побед
        adaptive_details = [d for d in all_details if d['winner'] == 'adaptive']
        non_adaptive_details = [d for d in all_details if d['winner'] == 'non_adaptive']
        
        avg_adaptive_improvement = sum(d['improvement_pct'] for d in adaptive_details) / len(adaptive_details) if adaptive_details else 0
        avg_non_adaptive_improvement = sum(d['improvement_pct'] for d in non_adaptive_details) / len(non_adaptive_details) if non_adaptive_details else 0
        
        if adaptive_details:
            print(f"\n  Детали побед адаптивного алгоритма (быстрее):")
            for d in sorted(adaptive_details, key=lambda x: x['improvement_pct'], reverse=True):
                print(f"    {d['model']:10s}: {d['na_time']:8.2f}с → {d['ad_time']:8.2f}с "
                      f"({d['improvement_pct']:+.2f}% быстрее)")
            print(f"    Среднее ускорение: {avg_adaptive_improvement:.2f}%")
        
        if non_adaptive_details:
            print(f"\n  Детали побед неадаптивного алгоритма (быстрее):")
            for d in sorted(non_adaptive_details, key=lambda x: x['improvement_pct'], reverse=True):
                print(f"    {d['model']:10s}: {d['ad_time']:8.2f}с → {d['na_time']:8.2f}с "
                      f"({d['improvement_pct']:+.2f}% быстрее)")
            print(f"    Среднее ускорение: {avg_non_adaptive_improvement:.2f}%")
        
        # Сохраняем в структуру
        elapsed_time_summary[f"{iterations}_iterations"] = {
            "adaptive_wins": adaptive_count,
            "adaptive_wins_percent": round(adaptive_count/len(datasets)*100, 1),
            "non_adaptive_wins": non_adaptive_count,
            "non_adaptive_wins_percent": round(non_adaptive_count/len(datasets)*100, 1),
            "equal": equal_count,
            "equal_percent": round(equal_count/len(datasets)*100, 1),
            "average_non_adaptive_time": round(avg_na_time, 2),
            "average_adaptive_time": round(avg_ad_time, 2),
            "time_ratio": round(avg_ad_time/avg_na_time, 3),
            "average_adaptive_improvement_pct": round(avg_adaptive_improvement, 2),
            "average_non_adaptive_improvement_pct": round(avg_non_adaptive_improvement, 2),
            "adaptive_wins_details": [
                {
                    "model": d['model'],
                    "non_adaptive_time": round(d['na_time'], 2),
                    "adaptive_time": round(d['ad_time'], 2),
                    "improvement_pct": round(d['improvement_pct'], 2)
                }
                for d in sorted(adaptive_details, key=lambda x: x['improvement_pct'], reverse=True)
            ],
            "non_adaptive_wins_details": [
                {
                    "model": d['model'],
                    "non_adaptive_time": round(d['na_time'], 2),
                    "adaptive_time": round(d['ad_time'], 2),
                    "improvement_pct": round(d['improvement_pct'], 2)
                }
                for d in sorted(non_adaptive_details, key=lambda x: x['improvement_pct'], reverse=True)
            ],
            "all_datasets": [
                {
                    "model": d['model'],
                    "winner": d['winner'],
                    "non_adaptive_time": round(d['na_time'], 2),
                    "adaptive_time": round(d['ad_time'], 2),
                    "improvement_pct": round(d['improvement_pct'], 2)
                }
                for d in all_details
            ]
        }
    
    summary_data["elapsed_time_metric"] = elapsed_time_summary
    
    print("\n" + "=" * 80)
    print("АНАЛИЗ ЗАВЕРШЕН")
    print("=" * 80)
    
    # Сохраняем в JSON
    if save_json:
        output_dir = json_path.parent
        summary_path = output_dir / f"comparison_summary_{data.get('timestamp', 'summary')}.json"
        with summary_path.open('w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Статистика сохранена в: {summary_path.name}")
    
    return summary_data


if __name__ == "__main__":
    if len(sys.argv) > 1:
        json_path = Path(sys.argv[1])
    else:
        # Ищем последний файл сравнения
        results_dir = Path(__file__).parent / "results"
        comparison_files = sorted(results_dir.glob("all_datasets_final_comparison_*.json"), reverse=True)
        if not comparison_files:
            print("Не найден файл сравнения!")
            print("Использование: python3 summarize_results.py [путь_к_json]")
            sys.exit(1)
        json_path = comparison_files[0]
        print(f"Используется файл: {json_path.name}\n")
    
    analyze_comparison(json_path, save_json=True)


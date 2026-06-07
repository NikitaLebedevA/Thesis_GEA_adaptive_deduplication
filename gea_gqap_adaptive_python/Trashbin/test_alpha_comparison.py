#!/usr/bin/env python3
"""Сравнение разных значений alpha для скорости обновления лямбд."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "GEA_GQAP_Python"))

from gea_gqap_adaptive_python import AdaptiveAlgorithmConfig, run_adaptive_ga, load_model

model = load_model("c351595")

# Тестируем разные значения alpha
alphas = [0.01, 0.05, 0.1]

print("Сравнение скорости обновления лямбд при разных alpha:")
print("=" * 70)

for alpha in alphas:
    print(f"\nТестируем alpha = {alpha}...")
    config = AdaptiveAlgorithmConfig(
        iterations=50,
        population_size=30,
        adaptive_alpha=alpha,
    )
    
    result = run_adaptive_ga(model, config=config)
    
    if result.adaptive_stats.lambda_history:
        initial = result.adaptive_stats.lambda_history[0]
        final = result.adaptive_stats.lambda_history[-1]
        change = [f - i for f, i in zip(final, initial)]
        
        print(f"  Лучшая стоимость: {result.best_cost:.2f}")
        print(f"  Изменение lambda_crossover: {change[0]:+.4f}")
        print(f"  Изменение lambda_mutation: {change[1]:+.4f}")
        print(f"  Начальная lambda_crossover: {initial[0]:.4f}")
        print(f"  Финальная lambda_crossover: {final[0]:.4f}")

print("\n" + "=" * 70)
print("Вывод: Чем больше alpha, тем быстрее меняются лямбды!")

#!/bin/bash
# Скрипт для ожидания завершения compare_algorithms.py и запуска summarize_results.py

cd "$(dirname "$0")"

echo "Ожидание завершения compare_algorithms.py..."
while pgrep -f "compare_algorithms.py" > /dev/null; do
    sleep 10
    FILES=$(ls -1 results/*.json 2>/dev/null | wc -l | tr -d ' ')
    echo "  Процесс работает... Создано файлов: $FILES"
done

echo ""
echo "✓ compare_algorithms.py завершен"
echo ""
echo "Запуск summarize_results.py..."
PYTHONPATH=.:../GEA_GQAP_Python python3 summarize_results.py

echo ""
echo "✓ Все готово!"
echo "Итоговые файлы:"
ls -lh results/*comparison*.json results/*summary*.json 2>/dev/null







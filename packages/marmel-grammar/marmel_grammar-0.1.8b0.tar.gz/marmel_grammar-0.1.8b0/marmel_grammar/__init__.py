
"""
🚀 MARMEL-GRAMMAR v0.1.8b - Самая мощная библиотека русской морфологии и транслитерации

Создатель: Dev-Marmel
Telegram: @dev_marmel
"""

from .grammar import MarmelGrammar
from . import dataset

__version__ = "0.1.8b"
__author__ = "Dev-Marmel"
__email__ = "marmelgpt@gmail.com"
__description__ = "Самая мощная библиотека русской морфологии и транслитерации для Python"

__all__ = [
    "MarmelGrammar",
    "dataset",
]

def info():
    print(f"""
🚀 MARMEL-GRAMMAR v{__version__}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📧 Автор: {__author__}
📱 Telegram: @dev_marmel  
📝 Описание: {__description__}

🌟 Возможности:
• Транслитерация английских имён в русские
• Склонение имён по всем падежам
• Спряжение глаголов с умным определением рода
• Определение рода имён
• Создание предложений и стихов
• Анализ контекста текста
• Перевод базовых слов
• Умное склонение глаголов по роду

🚀 Использование:
from marmel_grammar import MarmelGrammar
grammar = MarmelGrammar()
print(grammar.asc("Мария", "пукнуть"))  # Мария пукнула

📖 Полная документация в README.md
    """)

def demo():
    grammar = MarmelGrammar()
    
    print("🎯 ДЕМОНСТРАЦИЯ MARMEL-GRAMMAR")
    print("=" * 40)
    
    names = ["Alexander", "Maria", "Gazenvagen"]
    print("\n📝 ТРАНСЛИТЕРАЦИЯ:")
    for name in names:
        russian = grammar.transliterate_to_russian(name)
        gender = grammar.detect_gender(russian)
        print(f"  {name} → {russian} ({gender})")
    
    print("\n📚 СКЛОНЕНИЕ (Александр):")
    cases = ['nom', 'gen', 'dat', 'acc', 'ins', 'prep']
    for case in cases:
        form = grammar.decline("Александр", case)
        print(f"  {case}: {form}")
    
    print("\n💬 УМНЫЕ ПРЕДЛОЖЕНИЯ:")
    print(f"  {grammar.asc('Мария', 'танцевать')}")
    print(f"  {grammar.asc('Иван', 'читать')}")
    print(f"  {grammar.asc('Саша', 'работать')}")
    
    print("\n✅ Демонстрация завершена! Используйте MarmelGrammar() для начала работы.")


"""
MARMEL-GRAMMAR - Самая мощная библиотека русской морфологии и транслитерации

Создатель: Dev-Marmel
Telegram: @dev_marmel
"""

from .grammar import MarmelGrammar
from . import dataset

__version__ = "0.1.8"
__author__ = "Dev-Marmel"
__email__ = "marmelgpt@gmail.com"
__description__ = "Самая мощная библиотека русской морфологии и транслитерации для Python"

__all__ = [
    "MarmelGrammar",
    "dataset",
]

# Краткая информация о библиотеке
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
• Спряжение глаголов
• Определение рода имён
• Создание предложений и стихов
• Анализ контекста текста
• Перевод базовых слов

🚀 Использование:
from marmel_grammar import MarmelGrammar
grammar = MarmelGrammar()
print(grammar.transliterate_to_russian("Alexander"))  # Александр

📖 Полная документация в README.md
    """)

# Быстрая демонстрация
def demo():
    """Демонстрация основных возможностей"""
    grammar = MarmelGrammar()
    
    print("🎯 ДЕМОНСТРАЦИЯ MARMEL-GRAMMAR")
    print("=" * 40)
    
    # Транслитерация
    names = ["Alexander", "Maria", "Gazenvagen"]
    print("\n📝 ТРАНСЛИТЕРАЦИЯ:")
    for name in names:
        russian = grammar.transliterate_to_russian(name)
        gender = grammar.detect_gender(russian)
        print(f"  {name} → {russian} ({gender})")
    
    # Склонение
    print("\n📚 СКЛОНЕНИЕ (Александр):")
    cases = ['nom', 'gen', 'dat', 'acc', 'ins', 'prep']
    for case in cases:
        form = grammar.decline("Александр", case)
        print(f"  {case}: {form}")
    
    # Предложения
    print("\n💬 ПРЕДЛОЖЕНИЯ:")
    print(f"  {grammar.make_sentence('Мария', 'читать', 'книга')}")
    print(f"  {grammar.make_sentence('Иван', 'работать', 'проект', 'present')}")
    
    print("\n✅ Демонстрация завершена! Используйте MarmelGrammar() для начала работы.")

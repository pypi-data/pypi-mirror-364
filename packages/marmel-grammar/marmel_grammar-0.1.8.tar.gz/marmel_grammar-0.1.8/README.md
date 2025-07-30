
# 🚀 MARMEL-GRAMMAR

**Самая мощная библиотека русской морфологии и транслитерации для Python!**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-TOP%201%20🏆-gold.svg)](https://replit.com)

---

## 📞 Контакты

**Создатель:** Dev-Marmel  
**Telegram:** [@dev_marmel](https://t.me/dev_marmel)  
**Библиотека:** marmel_grammar  

---

## 🔧 Установка

### Через pip:
```bash
pip install marmel-grammar
```

### Из исходного кода:
```bash
git clone https://github.com/dev-marmel/marmel-grammar.git
cd marmel-grammar
python setup.py install
```

---

## 🌟 Основные возможности

- 🔥 **Транслитерация** - английские → русские имена
- 📚 **Склонение имён** - все 6 падежей
- 🔄 **Спряжение глаголов** - прошедшее/настоящее время
- 🧠 **Определение рода** - мужской/женский/унисекс
- 💬 **Создание предложений** - грамматически корректные фразы
- 🌍 **Перевод слов** - русский ↔ английский
- 📊 **Анализ контекста** - категоризация объектов
- ⚡ **Высокая производительность** с кэшированием

---

## 🚀 Быстрый старт

```python
from marmel_grammar import MarmelGrammar

# Создаём экземпляр
grammar = MarmelGrammar()

# Транслитерация
print(grammar.transliterate_to_russian("Alexander"))  # Александр
print(grammar.transliterate_to_russian("Gazenvagen")) # Газенваген

# Склонение
print(grammar.decline("Иван", "gen"))    # Ивана
print(grammar.decline("Мария", "dat"))   # Марии
print(grammar.decline("Саша", "acc"))    # Сашу (унисекс)

# Спряжение
print(grammar.conjugate("делать", "past", "Он"))      # делал
print(grammar.conjugate("писать", "present", "я"))    # пишу

# Создание предложений
print(grammar.make_sentence("Мария", "читать", "книга"))  
# Мария читала книгу.
```

---

## 📖 Классы и методы

### 🏗️ Класс `MarmelGrammar`

Основной класс библиотеки для работы с русской морфологией.

#### Инициализация:
```python
grammar = MarmelGrammar()
```

#### Основные переменные класса:
- `GENDER_EXCEPTIONS: Dict[str, str]` - исключения для определения рода
- `NAMES: Dict[str, Dict[str, Dict[str, str]]]` - словарь имён с падежами
- `VERBS: Dict[str, Dict[str, Dict[str, str]]]` - глаголы с формами
- `TRANSLATIONS: Dict[str, str]` - словарь переводов
- `SPECIAL_NAMES: Dict[str, str]` - специальные имена для транслитерации
- `TRANSLIT_MAP: Dict[str, str]` - карта транслитерации

---

### 📝 Методы транслитерации

#### `transliterate_to_russian(text: str) -> str`
Преобразует английский текст в русский.

```python
grammar.transliterate_to_russian("John")      # Джон
grammar.transliterate_to_russian("Vladimir")  # Владимир
```

#### `transliterate_to_english(text: str) -> str`
Преобразует русский текст в английский.

```python
grammar.transliterate_to_english("Владимир")  # Vladimir
```

---

### 📚 Методы склонения

#### `detect_gender(name: str) -> str`
Определяет род имени: 'male', 'female', 'unisex'.

```python
grammar.detect_gender("Иван")     # male
grammar.detect_gender("Мария")    # female  
grammar.detect_gender("Саша")     # unisex
```

#### `decline(name: str, case: str, gender: str = None) -> str`
Склоняет имя по падежам.

**Падежи:**
- `nom` - именительный (кто? что?)
- `gen` - родительный (кого? чего?)
- `dat` - дательный (кому? чему?)
- `acc` - винительный (кого? что?)
- `ins` - творительный (кем? чем?)
- `prep` - предложный (о ком? о чём?)

```python
grammar.decline("Александр", "gen")   # Александра
grammar.decline("Анна", "dat")        # Анне
grammar.decline("Саша", "ins")        # Сашей
```

#### `get_all_forms(name: str) -> Dict[str, str]`
Возвращает все падежные формы имени.

```python
forms = grammar.get_all_forms("Иван")
# {'nom': 'Иван', 'gen': 'Ивана', 'dat': 'Ивану', ...}
```

---

### 🔄 Методы спряжения

#### `conjugate(verb: str, tense: str, subject: str) -> str`
Спрягает глагол по временам и лицам.

**Времена:**
- `past` - прошедшее время
- `present` - настоящее время

```python
# Прошедшее время
grammar.conjugate("делать", "past", "Он")    # делал
grammar.conjugate("делать", "past", "Она")   # делала
grammar.conjugate("писать", "past", "Саша")  # писал (унисекс→муж)

# Настоящее время
grammar.conjugate("работать", "present", "я")    # работаю
grammar.conjugate("читать", "present", "ты")     # читаешь
grammar.conjugate("говорить", "present", "он")   # говорит
```

---

### 💬 Методы создания предложений

#### `make_sentence(subj: str, verb: str, obj: str, tense: str = 'past') -> str`
Создаёт грамматически корректное предложение.

```python
grammar.make_sentence("Мария", "читать", "книга")
# Мария читала книгу.

grammar.make_sentence("Иван", "работать", "проект", "present")  
# Иван работает проект.
```

#### `advanced_sentence(subj: str, verb: str, obj: str, adjective: str = None, tense: str = 'past') -> str`
Создаёт расширенное предложение с прилагательным.

```python
grammar.advanced_sentence("Анна", "читать", "книга", "интересную")
# Анна читала интересную книгу.
```

---

### 🎭 Творческие методы

#### `create_poem(name: str, verb: str) -> str`
Создаёт стихотворение с именем и глаголом.

```python
poem = grammar.create_poem("Анна", "работать")
print(poem)
# Стихотворение про Анна:
# У Анны есть мечта,
# К Анне приходит вдохновение...
```

#### `find_rhyme_ending(name: str) -> List[str]`
Находит рифмующиеся окончания для имени.

```python
grammar.find_rhyme_ending("Анна")  # ['я', 'на', 'ла']
```

---

### 🌍 Методы перевода и анализа

#### `translate(text: str) -> str`
Переводит русские слова на английский.

```python
grammar.translate("кот собака дом")  # cat dog house
```

#### `analyze_context(text: str) -> Dict[str, float]`
Анализирует контекст текста по категориям.

```python
context = grammar.analyze_context("кот собака играют")
# {'animal': 1.7, 'person': 0, 'object': 0}
```

#### `word_frequency(text: str) -> Dict[str, int]`
Подсчитывает частотность слов в тексте.

```python
freq = grammar.word_frequency("кот кот собака кот")
# {'кот': 3, 'собака': 1}
```

---

### 📊 Утилиты

#### `batch_transliterate(names: List[str]) -> Dict[str, str]`
Массовая транслитерация списка имён.

```python
names = ["Alexander", "Maria", "John"]
result = grammar.batch_transliterate(names)
# {'Alexander': 'Александр', 'Maria': 'Мария', 'John': 'Джон'}
```

#### `name_statistics() -> Dict[str, int]`
Статистика по базе данных имён.

```python
stats = grammar.name_statistics()
# {'male_names': 7, 'female_names': 7, 'unisex_names': 3, ...}
```

#### `add_name(name: str, gender: str, cases: Dict[str, str])`
Добавляет новое имя в базу данных.

```python
cases = {
    'nom': 'Максим', 'gen': 'Максима', 'dat': 'Максиму',
    'acc': 'Максима', 'ins': 'Максимом', 'prep': 'Максиме'
}
grammar.add_name('Максим', 'male', cases)
```

---

## 🤖 Использование в Telegram боте

### Простейший пример:

```python
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from marmel_grammar import MarmelGrammar

# Инициализация грамматики
grammar = MarmelGrammar()

async def start(update: Update, context):
    await update.message.reply_text(
        "🚀 Привет! Я бот с библиотекой MARMEL-GRAMMAR!\n"
        "Отправь мне английское имя - я переведу и просклоняю!"
    )

async def process_name(update: Update, context):
    user_input = update.message.text.strip()
    
    # Транслитерация
    russian_name = grammar.transliterate_to_russian(user_input)
    
    # Определение рода
    gender = grammar.detect_gender(russian_name)
    gender_emoji = "👨" if gender == "male" else "👩" if gender == "female" else "👤"
    
    # Все формы
    forms = grammar.get_all_forms(russian_name)
    
    # Создание предложения
    sentence = grammar.make_sentence(russian_name, "работать", "проект")
    
    # Стихотворение
    poem = grammar.create_poem(russian_name, "изучать")
    
    response = f"""
🎯 **{user_input}** → **{russian_name}** {gender_emoji}

📚 **Склонение:**
• И.п. (кто?): {forms['nom']}
• Р.п. (кого?): {forms['gen']}  
• Д.п. (кому?): {forms['dat']}
• В.п. (кого?): {forms['acc']}
• Т.п. (кем?): {forms['ins']}
• П.п. (о ком?): {forms['prep']}

💬 **Предложение:** {sentence}

🎭 **Стихотворение:**
{poem}
    """
    
    await update.message.reply_text(response)

async def decline_name(update: Update, context):
    if len(context.args) < 2:
        await update.message.reply_text("Использование: /decline <имя> <падеж>")
        return
    
    name = context.args[0]
    case = context.args[1].lower()
    
    try:
        declined = grammar.decline(name, case)
        gender = grammar.detect_gender(name)
        
        await update.message.reply_text(
            f"📝 {name} ({gender}) в падеже '{case}': **{declined}**"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def conjugate_verb(update: Update, context):
    if len(context.args) < 3:
        await update.message.reply_text("Использование: /conjugate <глагол> <время> <субъект>")
        return
    
    verb = context.args[0]
    tense = context.args[1]
    subject = context.args[2]
    
    try:
        conjugated = grammar.conjugate(verb, tense, subject)
        await update.message.reply_text(
            f"🔄 {verb} ({tense}, {subject}): **{conjugated}**"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

def main():
    # Замените YOUR_BOT_TOKEN на токен вашего бота
    application = Application.builder().token("YOUR_BOT_TOKEN").build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("decline", decline_name))
    application.add_handler(CommandHandler("conjugate", conjugate_verb))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_name))
    
    print("🤖 Бот запущен!")
    application.run_polling()

if __name__ == '__main__':
    main()
```

### Расширенные возможности для бота:

```python
# Обработка нескольких имён сразу
async def batch_process(update: Update, context):
    names = update.message.text.split()
    results = grammar.batch_transliterate(names)
    
    response = "🔄 **Массовая обработка:**\n"
    for eng, rus in results.items():
        gender = grammar.detect_gender(rus)
        response += f"• {eng} → {rus} ({gender})\n"
    
    await update.message.reply_text(response)

# Создание персональных поздравлений
async def create_greeting(update: Update, context):
    name = update.message.text.strip()
    rus_name = grammar.transliterate_to_russian(name)
    gender = grammar.detect_gender(rus_name)
    
    greeting = f"Дорог{'ой' if gender == 'male' else 'ая'} {rus_name}!"
    sentence = grammar.make_sentence(rus_name, "работать", "проект")
    poem = grammar.create_poem(rus_name, "изучать")
    
    await update.message.reply_text(f"{greeting}\n{sentence}\n\n{poem}")

# Анализ текста
async def analyze_text(update: Update, context):
    text = update.message.text
    context_analysis = grammar.analyze_context(text)
    frequency = grammar.word_frequency(text)
    translated = grammar.translate(text)
    
    response = f"""
📊 **Анализ текста:**
🔍 Контекст: {context_analysis}
📈 Частые слова: {dict(list(frequency.items())[:5])}
🌍 Перевод: {translated}
    """
    
    await update.message.reply_text(response)
```

---

## 🎯 Примеры использования

### Персонализированные приветствия:
```python
def create_personal_greeting(english_name):
    grammar = MarmelGrammar()
    
    # Транслитерация и определение рода
    russian_name = grammar.transliterate_to_russian(english_name)
    gender = grammar.detect_gender(russian_name)
    
    # Персонализация по роду
    if gender == 'male':
        greeting = f"Добро пожаловать, {russian_name}!"
        role = "товарищ"
    elif gender == 'female':
        greeting = f"Добро пожаловать, {russian_name}!"
        role = "подруга"
    else:
        greeting = f"Добро пожаловать, {russian_name}!"
        role = "друг"
    
    # Создание предложения
    sentence = grammar.make_sentence(russian_name, "изучать", "программирование")
    
    return f"{greeting} Наш{role} {sentence}"

print(create_personal_greeting("Alexander"))
# Добро пожаловать, Александр! Нашtvarish Александр изучал программирование.
```

### Обработка форм:
```python
def process_registration_form(first_name, last_name):
    grammar = MarmelGrammar()
    
    # Обработка имени и фамилии
    ru_first = grammar.transliterate_to_russian(first_name)
    ru_last = grammar.transliterate_to_russian(last_name)
    
    # Получение всех форм
    first_forms = grammar.get_all_forms(ru_first)
    
    # Создание документов
    documents = {
        'passport': f"Паспорт выдан: {first_forms['dat']} {ru_last}",
        'contract': f"Договор с: {first_forms['ins']} {ru_last}",
        'reference': f"Справка о: {first_forms['prep']} {ru_last}"
    }
    
    return documents
```

---

## 📈 Производительность

- ⚡ **Кэширование** - все частые операции кэшируются
- 🚀 **Оптимизация** - O(1) доступ к словарям
- 💾 **Память** - эффективное использование RAM
- 🔄 **Масштабирование** - поддержка больших объёмов данных

---

## 🤝 Поддержка и развитие

### Связь с разработчиком:
- **Telegram:** [@dev_marmel](https://t.me/dev_marmel)
- **Issues:** Создавайте issues в репозитории
- **Предложения:** Пишите идеи в Telegram

### Планы развития:
- [ ] Поддержка множественного числа
- [ ] Расширенный словарь (100k+ слов)
- [ ] ML-модели для улучшения точности
- [ ] API для удалённого использования
- [ ] Поддержка других славянских языков

---

## 📄 Лицензия

MIT License - используйте свободно в любых проектах!

---

## 🏆 Заключение

**MARMEL-GRAMMAR** - это не просто библиотека, это мощный инструмент для работы с русской морфологией. Идеально подходит для:

- 🤖 **Telegram ботов**
- 🌐 **Web приложений**
- 📱 **Мобильных приложений**
- 🔧 **CLI утилит**
- 📊 **Анализа данных**

**Начните использовать MARMEL-GRAMMAR сегодня и сделайте ваши приложения более умными!** 🚀

---

*Создано с ❤️ командой **Dev-Marmel***

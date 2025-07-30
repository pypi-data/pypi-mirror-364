# marmel_grammar.py

class Male:
    EXCEPTIONS = {
        'Павел': 'Павла',
        'Лев': 'Льва',
        'Юрий': 'Юрия',
        'Пётр': 'Петра',
        'Игорь': 'Игоря',
        'Илья': 'Илью'
    }

    @staticmethod
    def to_accusative(name: str) -> str:
        name = ''.join(ch for ch in name if ch.isalpha()).capitalize()
        if not name:
            return ''
        if name in Male.EXCEPTIONS:
            return Male.EXCEPTIONS[name]
        if name.endswith('й'):
            return name[:-1] + 'я'
        if name.endswith('а'):
            return name[:-1] + 'у'
        if name.endswith('я'):
            return name[:-1] + 'ю'
        if name[-1] in 'бвгджзклмнпрстфхцчшщ':
            return name + 'а'
        return name

class Female:
    EXCEPTIONS = {
        'Наталья': 'Наталью',
        'Мария': 'Марию',
        'Виктория': 'Викторию'
    }

    @staticmethod
    def to_accusative(name: str) -> str:
        name = ''.join(ch for ch in name if ch.isalpha()).capitalize()
        if not name:
            return ''
        if name in Female.EXCEPTIONS:
            return Female.EXCEPTIONS[name]
        if name.endswith('а'):
            return name[:-1] + 'у'
        if name.endswith('я'):
            return name[:-1] + 'ю'
        return name

class ENtoRU:
    EXCEPTIONS = {
        'Alexander': 'Александр',
        'Alexandra': 'Александра',
        'Svetlana': 'Светлана',
        'Yuri': 'Юрий',
        'Mikhail': 'Михаил',
        'Olga': 'Ольга',
        'Tatiana': 'Татьяна',
        'Dmitry': 'Дмитрий',
        'Natalia': 'Наталья',
        'Konstantin': 'Константин',
        'Maria': 'Мария',
        'Ilya': 'Илья',
        'Petr': 'Пётр',
        'Peter': 'Питер',
        'Lev': 'Лев',
        'Igor': 'Игорь',
        'Victoria': 'Виктория',
        'Elena': 'Елена',
        'Anna': 'Анна',
        'Sergey': 'Сергей',
        'Vladimir': 'Владимир',
        'Honeylady': 'Ханиледи',
        'Noah': 'Ной',
        'Nika': 'Ника',
    }

    translit_map = {
        'shch': 'щ', 'yo': 'ё', 'zh': 'ж', 'ch': 'ч', 'sh': 'ш',
        'ye': 'е', 'yu': 'ю', 'ya': 'я', 'ey': 'ей', 'ay': 'ай', 'oy': 'ой',
        'a': 'а', 'b': 'б', 'c': 'к', 'd': 'д', 'e': 'е', 'f': 'ф', 'g': 'г', 'h': 'х', 'i': 'и',
        'j': 'дж', 'k': 'к', 'l': 'л', 'm': 'м', 'n': 'н', 'o': 'о', 'p': 'п', 'q': 'кв', 'r': 'р',
        's': 'с', 't': 'т', 'u': 'у', 'v': 'в', 'w': 'в', 'x': 'кс', 'y': 'и', 'z': 'з',
        ' ': ' ',
    }

    @staticmethod
    def transliterate(name_en: str) -> str:
        name_en = name_en.strip()
        if name_en in ENtoRU.EXCEPTIONS:
            return ENtoRU.EXCEPTIONS[name_en]
        capitalized_name = ' '.join(word.capitalize() for word in name_en.split())
        if capitalized_name in ENtoRU.EXCEPTIONS:
            return ENtoRU.EXCEPTIONS[capitalized_name]
        words = name_en.split()
        result = []
        for word in words:
            w = ''
            i = 0
            lower_word = word.lower()
            while i < len(lower_word):
                if lower_word[i:i+4] in ENtoRU.translit_map:
                    w += ENtoRU.translit_map[lower_word[i:i+4]]
                    i += 4
                elif lower_word[i:i+3] in ENtoRU.translit_map:
                    w += ENtoRU.translit_map[lower_word[i:i+3]]
                    i += 3
                elif lower_word[i:i+2] in ENtoRU.translit_map:
                    w += ENtoRU.translit_map[lower_word[i:i+2]]
                    i += 2
                else:
                    w += ENtoRU.translit_map.get(lower_word[i], lower_word[i])
                    i += 1
            result.append(w.capitalize())
        return ' '.join(result)

    @staticmethod
    def to_accusative(name_en: str, gender: str) -> str:
        name_ru = ENtoRU.transliterate(name_en)
        if gender.lower() == 'male':
            return Male.to_accusative(name_ru)
        return Female.to_accusative(name_ru)

def decline(name: str, gender: str) -> str:
    cls = Male if gender.lower() == 'male' else Female
    return cls.to_accusative(name)

class Verb:
    verbs = {
        'ударить': 'ударил',
        'поцеловать': 'поцеловал',
        'обнять': 'обнял',
        'пукнуть': 'пукнул',
    }

    @staticmethod
    def detect_gender_by_name(name: str) -> str:
        name = ''.join(ch for ch in name if ch.isalpha()).capitalize().replace('ё', 'е')
        if name in Male.EXCEPTIONS:
            return 'male'
        if name in Female.EXCEPTIONS:
            return 'female'
        if name[-1] in 'аыяь':
            return 'female'
        if name[-1] in 'ймнртлзсвгбджкхцчшщ':
            return 'male'
        return 'male'

    @staticmethod
    def to_past_tense(verb: str, name: str) -> str:
        base = Verb.verbs.get(verb.lower(), verb)
        gender = Verb.detect_gender_by_name(name)
        if gender == 'female' and base.endswith('л'):
            return base + 'а'
        return base
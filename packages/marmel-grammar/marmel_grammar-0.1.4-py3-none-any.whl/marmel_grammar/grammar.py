# marmel_grammar/grammar.py
class Male:
    EXCEPTIONS = {
        'Павел': {
            'nominative': 'Павел',
            'genitive': 'Павла',
            'dative': 'Павлу',
            'accusative': 'Павла',
            'instrumental': 'Павлом',
            'prepositional': 'Павле'
        },
        'Лев': {
            'nominative': 'Лев',
            'genitive': 'Льва',
            'dative': 'Льву',
            'accusative': 'Льва',
            'instrumental': 'Львом',
            'prepositional': 'Льве'
        },
        'Юрий': {
            'nominative': 'Юрий',
            'genitive': 'Юрия',
            'dative': 'Юрию',
            'accusative': 'Юрия',
            'instrumental': 'Юрием',
            'prepositional': 'Юрии'
        },
        'Пётр': {
            'nominative': 'Пётр',
            'genitive': 'Пётра',
            'dative': 'Пётру',
            'accusative': 'Пётра',
            'instrumental': 'Пётром',
            'prepositional': 'Пётре'
        },
        'Игорь': {
            'nominative': 'Игорь',
            'genitive': 'Игоря',
            'dative': 'Игорю',
            'accusative': 'Игоря',
            'instrumental': 'Игорем',
            'prepositional': 'Игоре'
        },
        'Илья': {
            'nominative': 'Илья',
            'genitive': 'Ильи',
            'dative': 'Илье',
            'accusative': 'Илью',
            'instrumental': 'Ильёй',
            'prepositional': 'Илье'
        }
    }

    @staticmethod
    def _get_base_name(name: str) -> str:
        cleaned_name = ''.join(char for char in name if char.isalpha() or char.isspace())
        return cleaned_name.strip().capitalize()

    @staticmethod
    def nominative(name: str) -> str:
        base_name = Male._get_base_name(name)
        if base_name in Male.EXCEPTIONS:
            return Male.EXCEPTIONS[base_name]['nominative']
        return base_name

    @staticmethod
    def genitive(name: str) -> str:
        base_name = Male._get_base_name(name)
        if base_name in Male.EXCEPTIONS:
            return Male.EXCEPTIONS[base_name]['genitive']
        if base_name.endswith('й'):
            return base_name[:-1] + 'я'
        elif base_name.endswith('ь'):
            return base_name[:-1] + 'я'
        elif base_name.endswith('а'):
            return base_name[:-1] + 'ы'
        elif base_name.endswith('я'):
            return base_name[:-1] + 'и'
        elif base_name[-1] in 'бвгджзклмнпрстфхцчшщ':
            return base_name + 'а'
        else:
            return base_name + 'а'

    @staticmethod
    def dative(name: str) -> str:
        base_name = Male._get_base_name(name)
        if base_name in Male.EXCEPTIONS:
            return Male.EXCEPTIONS[base_name]['dative']
        if base_name.endswith('й'):
            return base_name[:-1] + 'ю'
        elif base_name.endswith('ь'):
            return base_name[:-1] + 'ю'
        elif base_name.endswith('а'):
            return base_name[:-1] + 'е'
        elif base_name.endswith('я'):
            return base_name[:-1] + 'е'
        elif base_name[-1] in 'бвгджзклмнпрстфхцчшщ':
            return base_name + 'у'
        else:
            return base_name + 'у'

    @staticmethod
    def accusative(name: str) -> str:
        base_name = Male._get_base_name(name)
        if base_name in Male.EXCEPTIONS:
            return Male.EXCEPTIONS[base_name]['accusative']
        if base_name.endswith('й'):
            return base_name[:-1] + 'я'
        elif base_name.endswith('а'):
            return base_name[:-1] + 'у'
        elif base_name.endswith('я'):
            return base_name[:-1] + 'ю'
        elif base_name[-1] in 'бвгджзклмнпрстфхцчшщ':
            return base_name + 'а'
        else:
            return base_name

    @staticmethod
    def instrumental(name: str) -> str:
        base_name = Male._get_base_name(name)
        if base_name in Male.EXCEPTIONS:
            return Male.EXCEPTIONS[base_name]['instrumental']
        if base_name.endswith('й'):
            return base_name[:-1] + 'ем'
        elif base_name.endswith('ь'):
            return base_name[:-1] + 'ем'
        elif base_name.endswith('а'):
            return base_name[:-1] + 'ой'
        elif base_name.endswith('я'):
            return base_name[:-1] + 'ей'
        elif base_name[-1] in 'жчшщ':
            return base_name + 'ем'
        elif base_name[-1] in 'бвгджзклмнпрстфхцчшщ':
            return base_name + 'ом'
        else:
            return base_name + 'ом'

    @staticmethod
    def prepositional(name: str) -> str:
        base_name = Male._get_base_name(name)
        if base_name in Male.EXCEPTIONS:
            return Male.EXCEPTIONS[base_name]['prepositional']
        if base_name.endswith('й'):
            return base_name[:-1] + 'и'
        elif base_name.endswith('ь'):
            return base_name[:-1] + 'е'
        elif base_name.endswith('а'):
            return base_name[:-1] + 'е'
        elif base_name.endswith('я'):
            return base_name[:-1] + 'е'
        elif base_name[-1] in 'бвгджзклмнпрстфхцчшщ':
            return base_name + 'е'
        else:
            return base_name + 'е'

    @staticmethod
    def decline(name: str) -> dict:
        return {
            'nominative': Male.nominative(name),
            'genitive': Male.genitive(name),
            'dative': Male.dative(name),
            'accusative': Male.accusative(name),
            'instrumental': Male.instrumental(name),
            'prepositional': Male.prepositional(name)
        }


class Female:
    EXCEPTIONS = {
        'Любовь': {
            'nominative': 'Любовь',
            'genitive': 'Любови',
            'dative': 'Любови',
            'accusative': 'Любовь',
            'instrumental': 'Любовью',
            'prepositional': 'Любови'
        },
        'Наталья': {
            'nominative': 'Наталья',
            'genitive': 'Натальи',
            'dative': 'Наталье',
            'accusative': 'Наталью',
            'instrumental': 'Натальей',
            'prepositional': 'Наталье'
        },
        'Мария': {
            'nominative': 'Мария',
            'genitive': 'Марии',
            'dative': 'Марии',
            'accusative': 'Марию',
            'instrumental': 'Марией',
            'prepositional': 'Марии'
        },
        'Виктория': {
            'nominative': 'Виктория',
            'genitive': 'Виктории',
            'dative': 'Виктории',
            'accusative': 'Викторию',
            'instrumental': 'Викторией',
            'prepositional': 'Виктории'
        }
    }

    @staticmethod
    def _get_base_name(name: str) -> str:
        cleaned_name = ''.join(char for char in name if char.isalpha() or char.isspace())
        return cleaned_name.strip().capitalize()

    @staticmethod
    def nominative(name: str) -> str:
        base_name = Female._get_base_name(name)
        if base_name in Female.EXCEPTIONS:
            return Female.EXCEPTIONS[base_name]['nominative']
        return base_name

    @staticmethod
    def genitive(name: str) -> str:
        base_name = Female._get_base_name(name)
        if base_name in Female.EXCEPTIONS:
            return Female.EXCEPTIONS[base_name]['genitive']
        if base_name.endswith('а'):
            return base_name[:-1] + 'ы'
        elif base_name.endswith('я'):
            return base_name[:-1] + 'и'
        elif base_name.endswith('ь'):
            return base_name[:-1] + 'и'
        else:
            return base_name + 'ы'

    @staticmethod
    def dative(name: str) -> str:
        base_name = Female._get_base_name(name)
        if base_name in Female.EXCEPTIONS:
            return Female.EXCEPTIONS[base_name]['dative']
        if base_name.endswith('а'):
            return base_name[:-1] + 'е'
        elif base_name.endswith('я'):
            return base_name[:-1] + 'е'
        elif base_name.endswith('ь'):
            return base_name[:-1] + 'и'
        else:
            return base_name + 'е'

    @staticmethod
    def accusative(name: str) -> str:
        base_name = Female._get_base_name(name)
        if base_name in Female.EXCEPTIONS:
            return Female.EXCEPTIONS[base_name]['accusative']
        if base_name.endswith('а'):
            return base_name[:-1] + 'у'
        elif base_name.endswith('я'):
            return base_name[:-1] + 'ю'
        else:
            return base_name

    @staticmethod
    def instrumental(name: str) -> str:
        base_name = Female._get_base_name(name)
        if base_name in Female.EXCEPTIONS:
            return Female.EXCEPTIONS[base_name]['instrumental']
        if base_name.endswith('а'):
            return base_name[:-1] + 'ой'
        elif base_name.endswith('я'):
            return base_name[:-1] + 'ей'
        elif base_name.endswith('ь'):
            return base_name[:-1] + 'ью'
        else:
            return base_name + 'ой'

    @staticmethod
    def prepositional(name: str) -> str:
        base_name = Female._get_base_name(name)
        if base_name in Female.EXCEPTIONS:
            return Female.EXCEPTIONS[base_name]['prepositional']
        if base_name.endswith('а'):
            return base_name[:-1] + 'е'
        elif base_name.endswith('я'):
            return base_name[:-1] + 'е'
        elif base_name.endswith('ь'):
            return base_name[:-1] + 'и'
        else:
            return base_name + 'е'

    @staticmethod
    def decline(name: str) -> dict:
        return {
            'nominative': Female.nominative(name),
            'genitive': Female.genitive(name),
            'dative': Female.dative(name),
            'accusative': Female.accusative(name),
            'instrumental': Female.instrumental(name),
            'prepositional': Female.prepositional(name)
        }


class Verb:
    @staticmethod
    def past_tense(verb_base: str, gender: str) -> str:
        verb_base = verb_base.strip()
        if gender == 'female':
            return verb_base + 'ла'
        elif gender == 'male':
            if verb_base.endswith('ла'):
                return verb_base[:-1]
            else:
                return verb_base + 'л'
        return verb_base


class EN_NAME_TO_RU:
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
        'Peter': 'Пётр',
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
        'Peter Jones': 'Питер Джонс',
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
    def translit(name_en: str) -> str:
        name_en = name_en.strip()
        if name_en in EN_NAME_TO_RU.EXCEPTIONS:
            return EN_NAME_TO_RU.EXCEPTIONS[name_en]

        capitalized_name = ' '.join(word.capitalize() for word in name_en.split())
        if capitalized_name in EN_NAME_TO_RU.EXCEPTIONS:
            return EN_NAME_TO_RU.EXCEPTIONS[capitalized_name]

        words = name_en.split()
        transliterated_words = []
        for word in words:
            word_cap = word.capitalize()
            if word_cap in EN_NAME_TO_RU.EXCEPTIONS:
                transliterated_words.append(EN_NAME_TO_RU.EXCEPTIONS[word_cap])
            else:
                transliterated_word = ''
                for char in word.lower():
                    transliterated_word += EN_NAME_TO_RU.translit_map.get(char, char)
                transliterated_words.append(transliterated_word.capitalize())
        return ' '.join(transliterated_words)

    @staticmethod
    def decline_translit(name_en: str, gender: str, case: str = 'accusative') -> str:
        name_ru = EN_NAME_TO_RU.translit(name_en)
        if not name_ru:
            return ""

        cls = Male if gender.lower() == 'male' else Female
        case_methods = {
            'nominative': cls.nominative,
            'genitive': cls.genitive,
            'dative': cls.dative,
            'accusative': cls.accusative,
            'instrumental': cls.instrumental,
            'prepositional': cls.prepositional
        }
        return case_methods.get(case, cls.accusative)(name_ru)

    @staticmethod
    def accusative_translit(name_en: str, gender: str) -> str:
        return EN_NAME_TO_RU.decline_translit(name_en, gender, 'accusative')


def get_gender_class(gender: str):
    return Male if gender.lower() == 'male' else Female


def decline_name(name: str, gender: str, case: str = 'accusative') -> str:
    cls = get_gender_class(gender)
    case_methods = {
        'nominative': cls.nominative,
        'genitive': cls.genitive,
        'dative': cls.dative,
        'accusative': cls.accusative,
        'instrumental': cls.instrumental,
        'prepositional': cls.prepositional
    }
    if case in case_methods:
        return case_methods[case](name)
    else:
        raise ValueError(f"Неизвестный падеж: {case}")

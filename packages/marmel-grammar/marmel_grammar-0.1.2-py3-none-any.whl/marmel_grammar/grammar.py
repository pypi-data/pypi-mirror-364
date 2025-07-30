class Male:
    EXCEPTIONS = {
        'Павел': 'Павла',
        'Лев': 'Льва',
        'Юрий': 'Юрия',
        'Пётр': 'Пётра',
        'Игорь': 'Игоря',
        'Илья': 'Илью',
        'Петр': 'Пётра',
    }

    @staticmethod
    def accusative(name: str) -> str:
        name = name.strip().capitalize()
        if name in Male.EXCEPTIONS:
            return Male.EXCEPTIONS[name]
        if name.endswith('й'):
            return name[:-1] + 'я'
        elif name.endswith('а'):
            return name[:-1] + 'у'
        elif name.endswith('я'):
            return name[:-1] + 'ю'
        elif name[-1] in 'бвгджзклмнпрстфхцчшщ':
            return name + 'а'
        else:
            return name


class Female:
    @staticmethod
    def accusative(name: str) -> str:
        name = name.strip().capitalize()
        if name.endswith('а'):
            return name[:-1] + 'у'
        elif name.endswith('я'):
            return name[:-1] + 'ю'
        else:
            return name


class Verb:
    @staticmethod
    def past_tense(verb_base: str, gender: str) -> str:
        verb_base = verb_base.strip()
        if gender == 'female':
            if verb_base.endswith('л'):
                return verb_base + 'а'
            elif verb_base.endswith('ла'):
                return verb_base
        return verb_base


class EN_NAME_TO_RU:
    EXCEPTIONS = {
        'Alexander': 'Александр',
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
        'Lev': 'Лев',
        'Igor': 'Игорь',
    }

    translit_map = {
        'shch': 'щ', 'yo': 'ё', 'zh': 'ж', 'ch': 'ч', 'sh': 'ш', 'ye': 'е', 'yu': 'ю', 'ya': 'я',
        'a': 'а', 'b': 'б', 'v': 'в', 'g': 'г', 'd': 'д', 'e': 'е', 'z': 'з', 'i': 'и', 'j': 'й',
        'k': 'к', 'l': 'л', 'm': 'м', 'n': 'н', 'o': 'о', 'p': 'п', 'r': 'р', 's': 'с', 't': 'т',
        'u': 'у', 'f': 'ф', 'h': 'х', 'c': 'ц', 'y': 'ы',
    }

    @staticmethod
    def translit(name_en: str) -> str:
        name_en_cap = name_en.capitalize()
        if name_en_cap in EN_NAME_TO_RU.EXCEPTIONS:
            return EN_NAME_TO_RU.EXCEPTIONS[name_en_cap]

        name_en = name_en.lower()
        result = ''
        i = 0
        while i < len(name_en):
            for length in (4, 3, 2):
                chunk = name_en[i:i+length]
                if chunk in EN_NAME_TO_RU.translit_map:
                    result += EN_NAME_TO_RU.translit_map[chunk]
                    i += length
                    break
            else:
                result += name_en[i]
                i += 1
        return result.capitalize()

    @staticmethod
    def accusative_translit(name_en: str, gender: str) -> str:
        name_ru = EN_NAME_TO_RU.translit(name_en)
        cls = Male if gender == 'male' else Female
        return cls.accusative(name_ru)


def get_gender_class(gender: str):
    return Male if gender == 'male' else Female

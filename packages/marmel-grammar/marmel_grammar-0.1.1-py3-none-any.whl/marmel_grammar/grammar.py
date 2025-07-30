class Male:
    EXCEPTIONS = {
        'Павел': 'Павла',
        'Лев': 'Льва',
        'Юрий': 'Юрия',
        'Пётр': 'Петра',
        'Игорь': 'Игоря',
        'Илья': 'Илью',
        'Петр': 'Петра',
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

class NumberDeclension:
    @staticmethod
    def years(number: int) -> str:
        n = abs(number) % 100
        n1 = n % 10
        if 11 <= n <= 19:
            form = 'лет'
        elif n1 == 1:
            form = 'год'
        elif 2 <= n1 <= 4:
            form = 'года'
        else:
            form = 'лет'
        return f'{number} {form}'

    @staticmethod
    def hours(number: int) -> str:
        n = abs(number) % 100
        n1 = n % 10
        if 11 <= n <= 19:
            form = 'часов'
        elif n1 == 1:
            form = 'час'
        elif 2 <= n1 <= 4:
            form = 'часа'
        else:
            form = 'часов'
        return f'{number} {form}'

    @staticmethod
    def minutes(number: int) -> str:
        n = abs(number) % 100
        n1 = n % 10
        if 11 <= n <= 19:
            form = 'минут'
        elif n1 == 1:
            form = 'минута'
        elif 2 <= n1 <= 4:
            form = 'минуты'
        else:
            form = 'минут'
        return f'{number} {form}'

    @staticmethod
    def format_big_number(number: int) -> str:
        def format_float(num):
            if num.is_integer():
                return str(int(num))
            return f'{num:.1f}'

        abs_num = abs(number)
        sign = '-' if number < 0 else ''
        if abs_num >= 1_000_000_000:
            val = abs_num / 1_000_000_000
            return f'{sign}{format_float(val)} млрд'
        elif abs_num >= 1_000_000:
            val = abs_num / 1_000_000
            return f'{sign}{format_float(val)} млн'
        elif abs_num >= 1_000:
            val = abs_num / 1_000
            return f'{sign}{format_float(val)} тыс.'
        else:
            s = f'{abs_num:,}'.replace(',', '.')
            return f'{sign}{s}'

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
        return Case.male(name, 'accusative')


class Female:
    @staticmethod
    def accusative(name: str) -> str:
        return Case.female(name, 'accusative')

class Case:
    CASES = ['nominative', 'genitive', 'dative', 'accusative', 'instrumental', 'prepositional']

    @staticmethod
    def male(name: str, case: str) -> str:
        name = name.strip().capitalize()

        if case not in Case.CASES:
            return name

        if case == 'nominative':
            return name

        if name in Male.EXCEPTIONS and case == 'accusative':
            return Male.EXCEPTIONS[name]

        if case == 'genitive' or (case == 'accusative' and name[-1] in 'бвгджзклмнпрстфхцчшщ'):
            return name + 'а'
        elif case == 'dative':
            return name + 'у'
        elif case == 'accusative':
            if name.endswith('й'):
                return name[:-1] + 'я'
            elif name.endswith('а'):
                return name[:-1] + 'у'
            elif name.endswith('я'):
                return name[:-1] + 'ю'
            else:
                return name + 'а'
        elif case == 'instrumental':
            if name.endswith('й'):
                return name[:-1] + 'ем'
            elif name[-1] in 'бвгджзклмнпрстфхцчшщ':
                return name + 'ом'
            elif name.endswith('а'):
                return name[:-1] + 'ой'
            else:
                return name
        elif case == 'prepositional':
            return 'о ' + name + 'е'
        return name

    @staticmethod
    def female(name: str, case: str) -> str:
        name = name.strip().capitalize()

        if case not in Case.CASES:
            return name

        if case == 'nominative':
            return name
        elif case == 'genitive':
            if name.endswith('а'):
                return name[:-1] + 'ы'
            elif name.endswith('я'):
                return name[:-1] + 'и'
        elif case == 'dative':
            if name.endswith('а') or name.endswith('я'):
                return name[:-1] + 'е'
        elif case == 'accusative':
            if name.endswith('а'):
                return name[:-1] + 'у'
            elif name.endswith('я'):
                return name[:-1] + 'ю'
        elif case == 'instrumental':
            if name.endswith('а'):
                return name[:-1] + 'ой'
            elif name.endswith('я'):
                return name[:-1] + 'ей'
        elif case == 'prepositional':
            return 'о ' + name[:-1] + 'е'

        return name


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
                chunk = name_en[i:i + length]
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
        return EN_NAME_TO_RU.translit_case(name_en, gender, 'accusative')

    @staticmethod
    def translit_case(name_en: str, gender: str, case: str) -> str:
        name_ru = EN_NAME_TO_RU.translit(name_en)
        return Case.male(name_ru, case) if gender == 'male' else Case.female(name_ru, case)


def get_gender_class(gender: str):
    return Male if gender == 'male' else Female

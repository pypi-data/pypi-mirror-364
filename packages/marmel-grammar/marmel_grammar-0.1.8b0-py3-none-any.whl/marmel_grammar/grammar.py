
import re
from functools import lru_cache
from typing import Dict, List, Tuple, Union, Optional
from .dataset import *

class MarmelGrammar:
    
    def __init__(self):
        self._load_dataset()
        self._init_reverse_translit()
    
    def _load_dataset(self):
        self.GENDER_EXCEPTIONS = GENDER_EXCEPTIONS
        self.NAMES = NAMES
        self.VERBS = VERBS
        self.TRANSLATIONS = TRANSLATIONS
        self.CONTEXT_RULES = CONTEXT_RULES
        self.SPECIAL_NAMES = SPECIAL_NAMES
        self.TRANSLIT_MAP = TRANSLIT_MAP
    
    def _init_reverse_translit(self):
        self.REVERSE_TRANSLIT_MAP = {v: k for k, v in self.TRANSLIT_MAP.items()}
    
    @lru_cache(maxsize=1000)
    def detect_gender(self, name: str) -> str:
        name = name.strip().replace("ё", "е").capitalize()
        if name in self.GENDER_EXCEPTIONS:
            return self.GENDER_EXCEPTIONS[name]
        if name.endswith(('а', 'я', 'ия')):
            return 'female'
        if name.endswith('ь'):
            return 'male'
        return 'male'

    @lru_cache(maxsize=1000)
    def decline(self, name: str, case: str, gender: str = None) -> str:
        gender = gender or self.detect_gender(name)
        
        if gender in self.NAMES and name in self.NAMES[gender] and case in self.NAMES[gender][name]:
            return self.NAMES[gender][name][case]
        
        if case == 'nom':
            return name
        elif case == 'gen':
            if gender == 'female' or (gender == 'unisex' and name.endswith(('а', 'я'))):
                if name.endswith('а'):
                    return name[:-1] + 'ы'
                elif name.endswith('я'):
                    return name[:-1] + 'и'
                return name[:-1] + 'и'
            elif gender == 'unisex' and name.endswith('а'):
                return name[:-1] + 'и'
            return name + 'а'
        elif case == 'dat':
            if gender == 'male' or (gender == 'unisex' and not name.endswith(('а', 'я'))):
                return name + 'у'
            else:
                if name.endswith(('а', 'я')):
                    return name[:-1] + 'е'
                return name + 'е'
        elif case == 'acc':
            if gender == 'male' or (gender == 'unisex' and not name.endswith(('а', 'я'))):
                return name + 'а'
            else:
                if name.endswith('а'):
                    return name[:-1] + 'у'
                return name[:-1] + 'ю'
        elif case == 'ins':
            if gender == 'male' or (gender == 'unisex' and not name.endswith(('а', 'я'))):
                return name + 'ом'
            else:
                if name.endswith('а'):
                    return name[:-1] + 'ой'
                return name[:-1] + 'ей'
        elif case == 'prep':
            if gender == 'male' or (gender == 'unisex' and not name.endswith(('а', 'я'))):
                return name + 'е'
            else:
                if name.endswith(('а', 'я')):
                    return name[:-1] + 'е'
                return name + 'е'
        
        return name

    @lru_cache(maxsize=500)
    def conjugate(self, verb: str, tense: str, subject: str) -> str:
        if verb in self.VERBS and tense in self.VERBS[verb]:
            forms = self.VERBS[verb][tense]
            
            if tense == 'past':
                if subject.lower() in ('они', 'вы', 'мы'):
                    return forms['pl']
                gender = self.detect_gender(subject)
                if gender == 'male':
                    return forms['m']
                elif gender == 'female':
                    return forms['f']
                elif gender == 'unisex':
                    return forms['m']
                else:
                    return forms['n']
            
            elif tense == 'present':
                subject_lower = subject.lower()
                if subject_lower in forms:
                    return forms[subject_lower]
                else:
                    return forms.get('он', verb)
        
        return verb

    def smart_conjugate(self, verb: str, subject: str, tense: str = 'past') -> str:
        base_verb = verb.lower()
        
        if base_verb in self.VERBS:
            return self.conjugate(base_verb, tense, subject)
        
        if base_verb.endswith('ть'):
            stem = base_verb[:-2]
            gender = self.detect_gender(subject)
            
            if tense == 'past':
                if gender == 'female':
                    return stem + 'ла'
                elif gender == 'male':
                    return stem + 'л'
                else:
                    return stem + 'ло'
            elif tense == 'present':
                return stem + 'ет'
        
        return verb

    def asc(self, name: str, verb: str, tense: str = 'past') -> str:
        declined_name = self.decline(name, 'nom')
        conjugated_verb = self.smart_conjugate(verb, name, tense)
        return f"{declined_name} {conjugated_verb}"

    def make_sentence(self, subj: str, verb: str, obj: str, tense: str = 'past') -> str:
        declined_subj = self.decline(subj, 'nom')
        conjugated_verb = self.conjugate(verb, tense, subj)
        declined_obj = self.decline(obj, 'acc')
        
        return f"{declined_subj} {conjugated_verb} {declined_obj}."

    def transliterate_to_russian(self, text: str) -> str:
        original_text = text.lower().strip()
        
        if original_text in self.SPECIAL_NAMES:
            return self.SPECIAL_NAMES[original_text]
        
        result = ""
        i = 0
        
        while i < len(original_text):
            found = False
            for length in [4, 3, 2, 1]:
                if i + length <= len(original_text):
                    substr = original_text[i:i+length]
                    if substr in self.TRANSLIT_MAP:
                        result += self.TRANSLIT_MAP[substr]
                        i += length
                        found = True
                        break
            
            if not found:
                result += original_text[i]
                i += 1
        
        return result.capitalize()

    def transliterate_to_english(self, text: str) -> str:
        result = ""
        for char in text.lower():
            result += self.REVERSE_TRANSLIT_MAP.get(char, char)
        return result.capitalize()

    def translate(self, text: str) -> str:
        words = re.findall(r'\w+|[^\w]', text)
        translated = []
        for word in words:
            clean_word = word.lower().strip()
            if clean_word in self.TRANSLATIONS:
                translated.append(self.TRANSLATIONS[clean_word])
            else:
                translated.append(word)
        return ' '.join(translated)

    def analyze_context(self, text: str) -> Dict[str, float]:
        context = {'animal': 0, 'person': 0, 'object': 0}
        words = re.findall(r'\w+', text.lower())
        for word in words:
            if word in self.CONTEXT_RULES:
                for ctx, score in self.CONTEXT_RULES[word].items():
                    context[ctx] += score
        return context
    
    def add_name(self, name: str, gender: str, cases: Dict[str, str]):
        if gender not in self.NAMES:
            self.NAMES[gender] = {}
        self.NAMES[gender][name] = cases
    
    def get_all_forms(self, name: str) -> Dict[str, str]:
        gender = self.detect_gender(name)
        cases = ['nom', 'gen', 'dat', 'acc', 'ins', 'prep']
        return {case: self.decline(name, case, gender) for case in cases}
    
    def create_poem(self, name: str, verb: str) -> str:
        forms = self.get_all_forms(name)
        conjugated_verb = self.conjugate(verb, 'present', name)
        return f"""Стихотворение про {forms['nom']}:
        
У {forms['gen']} есть мечта,
К {forms['dat']} приходит вдохновение,
Все видят {forms['acc']} в деле,
С {forms['ins']} работать - наслаждение,
О {forms['prep']} говорят с восхищением!

{forms['nom']} {conjugated_verb} каждый день!"""
    
    def batch_transliterate(self, names: List[str]) -> Dict[str, str]:
        return {name: self.transliterate_to_russian(name) for name in names}
    
    def name_statistics(self) -> Dict[str, int]:
        total_male = len(self.NAMES.get('male', {}))
        total_female = len(self.NAMES.get('female', {}))
        total_unisex = len(self.NAMES.get('unisex', {}))
        total_verbs = len(self.VERBS)
        total_translations = len(self.TRANSLATIONS)
        
        return {
            'male_names': total_male,
            'female_names': total_female,
            'unisex_names': total_unisex,
            'total_names': total_male + total_female + total_unisex,
            'verbs': total_verbs,
            'translations': total_translations
        }
    
    def advanced_sentence(self, subj: str, verb: str, obj: str, 
                         adjective: str = None, tense: str = 'past') -> str:
        declined_subj = self.decline(subj, 'nom')
        conjugated_verb = self.conjugate(verb, tense, subj)
        declined_obj = self.decline(obj, 'acc')
        
        if adjective:
            return f"{declined_subj} {conjugated_verb} {adjective} {declined_obj}."
        return f"{declined_subj} {conjugated_verb} {declined_obj}."
    
    def find_rhyme_ending(self, name: str) -> str:
        endings = {
            'а': ['я', 'на', 'ла'], 'я': ['а', 'ня', 'ля'],
            'й': ['ей', 'ий', 'ой'], 'р': ['ар', 'ер', 'ор'],
            'н': ['ан', 'ен', 'он'], 'л': ['ал', 'ел', 'ол']
        }
        last_char = name[-1].lower()
        return endings.get(last_char, ['ой', 'ей', 'ий'])
    
    def word_frequency(self, text: str) -> Dict[str, int]:
        words = re.findall(r'\w+', text.lower())
        freq = {}
        for word in words:
            freq[word] = freq.get(word, 0) + 1
        return dict(sorted(freq.items(), key=lambda x: x[1], reverse=True))

    def smart_verb_suggestion(self, name: str) -> List[str]:
        gender = self.detect_gender(name)
        common_verbs = ['танцевать', 'петь', 'читать', 'работать', 'играть', 'смеяться']
        return [self.asc(name, verb) for verb in common_verbs]

    def conjugate_any_verb(self, verb: str, subject: str, tense: str = 'past') -> str:
        gender = self.detect_gender(subject)
        base_verb = verb.lower().strip()
        
        if base_verb in self.VERBS:
            return self.conjugate(base_verb, tense, subject)
        
        if base_verb.endswith('ть'):
            stem = base_verb[:-2]
            if tense == 'past':
                if gender == 'female':
                    return stem + 'ла'
                elif gender == 'male':
                    return stem + 'л'
                else:
                    return stem + 'ло'
            elif tense == 'present':
                if gender in ['male', 'female']:
                    return stem + 'ет'
                return stem + 'ет'
        
        return verb

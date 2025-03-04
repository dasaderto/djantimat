# -*- coding: utf-8 -*-

import re

import pymorphy2

from .models import Slang

word_pattern = r'[А-яA-z0-9\-\*]+'


def distance(a, b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n, m)) space
        a, b = b, a
        n, m = m, n

    current_row = range(n + 1)  # Keep current and previous row, not entire matrix
    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
            if a[j - 1] != b[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)

    return current_row[n]


d = {'а': ['а', 'a', '@'],
     'б': ['б', '6', 'b'],
     'в': ['в', 'b', 'v'],
     'г': ['г', 'r', 'g'],
     'д': ['д', 'd', 'g'],
     'е': ['е', 'e'],
     'ё': ['ё', 'e'],
     'ж': ['ж', 'zh', '*'],
     'з': ['з', '3', 'z'],
     'и': ['и', 'u', 'i'],
     'й': ['й', 'u', 'i'],
     'к': ['к', 'k', 'i{', '|{'],
     'л': ['л', 'l', 'ji'],
     'м': ['м', 'm'],
     'н': ['н', 'h', 'n'],
     'о': ['о', 'o', '0'],
     'п': ['п', 'n', 'p'],
     'р': ['р', 'r', 'p'],
     'с': ['с', 'c', 's'],
     'т': ['т', 'm', 't'],
     'у': ['у', 'y', 'u'],
     'ф': ['ф', 'f'],
     'х': ['х', 'x', 'h', '}{'],
     'ц': ['ц', 'c', 'u,'],
     'ч': ['ч', 'ch'],
     'ш': ['ш', 'sh'],
     'щ': ['щ', 'sch'],
     'ь': ['ь', 'b'],
     'ы': ['ы', 'bi'],
     'ъ': ['ъ'],
     'э': ['э', 'e'],
     'ю': ['ю', 'io'],
     'я': ['я', 'ya']
     }


class PymorphyProc(object):
    morph = pymorphy2.MorphAnalyzer()

    @staticmethod
    def test(text):
        return len([w for w in PymorphyProc._gen(text)])

    @staticmethod
    def replace(text, repl='[censored]'):
        words = {}
        for word in PymorphyProc._gen(text):
            text = text.replace(word, repl)
        return text

    @staticmethod
    def wrap(text, wrap=('<span style="color:red;">', '</span>',)):
        words = {}
        for word in PymorphyProc._gen(text):
            words[word] = '%s%s%s' % (wrap[0], word, wrap[1],)
        for word, wrapped in words.items():
            text = text.replace(word, wrapped)
        return text

    @staticmethod
    def _gen(text):
        words = PymorphyProc.get_words()
        data = " ".join(re.findall(word_pattern, text))
        prepared_data = ""
        for datum in data.split(" "):
            if len(datum) > 2:
                prepared_data += " " + datum + " "
            else:
                prepared_data += datum
        prepared_data = prepared_data.replace("  ", " ")
        prepared_data = list(filter(lambda x: x, prepared_data.split(" ")))
        for datum in prepared_data:
            for word in [word for word in words if len(word) <= len(datum)+2]:
                for part in range(len(datum)):
                    fragment = datum[part: part + len(word)]
                    if (distance(fragment, word) <= len(word) * 0.25) and \
                            (part <= 2 or part+len(word) < len(word)):
                        yield fragment

    @staticmethod
    def get_words():
        return Slang.objects.values_list('word', flat=True)


class RegexpProc(object):
    PATTERN_1 = r''.join((
        r'\w{0,5}[хx]([хx\s\!@#\$%\^&*+-\|\/]{0,6})',
        r'[уy]([уy\s\!@#\$%\^&*+-\|\/]{0,6})[ёiлeеюийя]\w{0,7}|\w{0,6}[пp]',
        r'([пp\s\!@#\$%\^&*+-\|\/]{0,6})[iие]([iие\s\!@#\$%\^&*+-\|\/]{0,6})',
        r'[3зс]([3зс\s\!@#\$%\^&*+-\|\/]{0,6})[дd]\w{0,10}|[сcs][уy]',
        r'([уy\!@#\$%\^&*+-\|\/]{0,6})[4чkк]\w{1,3}|\w{0,4}[bб]',
        r'([bб\s\!@#\$%\^&*+-\|\/]{0,6})[lл]([lл\s\!@#\$%\^&*+-\|\/]{0,6})',
        r'[yя]\w{0,10}|\w{0,8}[её][bб][лске@eыиаa][наи@йвл]\w{0,8}|\w{0,4}[еe]',
        r'([еe\s\!@#\$%\^&*+-\|\/]{0,6})[бb]([бb\s\!@#\$%\^&*+-\|\/]{0,6})',
        r'[uу]([uу\s\!@#\$%\^&*+-\|\/]{0,6})[н4ч]\w{0,4}|\w{0,4}[еeё]',
        r'([еeё\s\!@#\$%\^&*+-\|\/]{0,6})[бb]([бb\s\!@#\$%\^&*+-\|\/]{0,6})',
        r'[нn]([нn\s\!@#\$%\^&*+-\|\/]{0,6})[уy]\w{0,4}|\w{0,4}[еe]',
        r'([еe\s\!@#\$%\^&*+-\|\/]{0,6})[бb]([бb\s\!@#\$%\^&*+-\|\/]{0,6})',
        r'[оoаa@]([оoаa@\s\!@#\$%\^&*+-\|\/]{0,6})[тnнt]\w{0,4}|\w{0,10}[ё]',
        r'([ё\!@#\$%\^&*+-\|\/]{0,6})[б]\w{0,6}|\w{0,4}[pп]',
        r'([pп\s\!@#\$%\^&*+-\|\/]{0,6})[иeеi]([иeеi\s\!@#\$%\^&*+-\|\/]{0,6})',
        r'[дd]([дd\s\!@#\$%\^&*+-\|\/]{0,6})[oоаa@еeиi]',
        r'([oоаa@еeиi\s\!@#\$%\^&*+-\|\/]{0,6})[рr]\w{0,12}',
    ))

    PATTERN_2 = r'|'.join((
        r"(\b[сs]{1}[сsц]{0,1}[uуy](?:[ч4]{0,1}[иаakк][^ц])\w*\b)",
        r"(\b(?!пло|стра|[тл]и)(\w(?!(у|пло)))*[хx][уy](й|йа|[еeё]|и|я|ли|ю)(?!га)\w*\b)",
        r"(\b(п[oо]|[нз][аa])*[хx][eе][рp]\w*\b)",
        r"(\b[мm][уy][дd]([аa][кk]|[oо]|и)\w*\b)",
        r"(\b\w*д[рp](?:[oо][ч4]|[аa][ч4])(?!л)\w*\b)",
        r"(\b(?!(?:кило)?[тм]ет)(?!смо)[а-яa-z]*(?<!с)т[рp][аa][хx]\w*\b)",
        r"(\b[к|k][аaoо][з3z]+[eе]?ё?л\w*\b)",
        r"(\b(?!со)\w*п[еeё]р[нд](и|иc|ы|у|н|е|ы)\w*\b)",
        r"(\b\w*[бп][ссз]д\w+\b)",
        r"(\b([нnп][аa]?[оo]?[xх])\b)",
        r"(\b([аa]?[оo]?[нnпбз][аa]?[оo]?)?([cс][pр][аa][^зжбсвм])\w*\b)",
        r"(\b\w*([оo]т|вы|[рp]и|[оo]|и|[уy]){0,1}([пnрp][iиеeё]{0,1}[3zзсcs][дd])\w*\b)",
        r"(\b(вы)?у?[еeё]?би?ля[дт]?[юоo]?\w*\b)",
        r"(\b(?!вело|ски|эн)\w*[пpp][eеиi][дd][oaоаеeирp](?![цянгюсмйчв])[рp]?(?![лт])\w*\b)",
        r"(\b(?!в?[ст]{1,2}еб)(?:(?:в?[сcз3о][тяaа]?[ьъ]?|вы|п[рp][иоo]|[уy]|р[aа][з3z][ьъ]?|к[оo]н[оo])?[её]б[а-яa-z]*)|(?:[а-яa-z]*[^хлрдв][еeё]б)\b)",
        r"(\b[з3z][аaоo]л[уy]п[аaeеин]\w*\b)",
    ))

    regexp = re.compile(PATTERN_1, re.U | re.I)

    @staticmethod
    def test(text):
        return bool(RegexpProc.regexp.findall(text))

    @staticmethod
    def replace(text, repl='[censored]'):
        return RegexpProc.regexp.sub(repl, text)

    @staticmethod
    def wrap(text, wrap=('<span style="color:red;">', '</span>',)):
        words = {}
        for word in re.findall(word_pattern, text):
            if len(word) < 3:
                continue
            if RegexpProc.regexp.findall(word):
                words[word] = '%s%s%s' % (wrap[0], word, wrap[1],)
        for word, wrapped in words.items():
            text = text.replace(word, wrapped)
        return text

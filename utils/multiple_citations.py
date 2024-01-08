import requests
import json
import nltk
import re
# from cite_location import CiteLocation
from citation_parse import CitationParse
# from context_length import ContextLength

class MultipleCitations:

# check if sentence and length
    def filterData(self,context):
        res = self.citationStyleRound(context)
        if res is None:
            res = self.citationStyleSquare(context)
        return res
        

    def citationStyleRound(self, context):
        name1 = "[\.\[\]A-Za-zÀ-Üà-øoù-ÿŒœß-]+( ?[\.\[\]A-Za-zÀ-Üà-øoù-ÿŒœß-]+)?"
        author1 = f"{name1}"
        author2 = f"{name1} (and|&) {name1}"
        author3 = f"{name1}, {name1}, (and|&) {name1}"
        author4 = f"{name1}, {name1}, {name1}, (and|&) {name1}"
        author5OrMore = f"{name1} et al\."

        page1 = f"(,? (p\.)?(pp\.)?(chap\.)?(Ch\.)?(pg\.)?(para\.)?(para\.)?(Tab\.)?(Fig\.)?(Algorithm)?(Example)?(Sec\.)?(eq\.)? \(?\d+(?:-\d+)?\)?)?"
        page2 = f"(,? \d+(?:-\d+)?)?"
        nd = f"(,? n.d.)?"
        alpha = f"[a-z]?"

        pattern1 = "[\[\(]" + author5OrMore + "(,? \d{4}[a-z]?)(,? \d{4}?[a-z]?)?(,?[a-z]?)?" + nd + page1 + page2 + "[\)\]]"
        pattern2 = "[\[\(]" + author4 + "(,? \d{4}[a-z]?)(,? \d{4}?[a-z]?)?(,?[a-z]?)?" + nd + page1 + page2 + "[\)\]]"
        pattern3 = "[\[\(]" + author3 + "(,? \d{4}[a-z]?)(,? \d{4}?[a-z]?)?(,?[a-z]?)?" + nd + page1 + page2 + "[\)\]]"
        pattern4 = "[\[\(]" + author2 + "(,? \d{4}[a-z]?)(,? \d{4}?[a-z]?)?(,?[a-z]?)?" + nd + page1 + page2 + "[\)\]]"
        pattern5 = "[\[\(]" + author1 + "(,? \d{4}[a-z]?)(,? \d{4}?[a-z]?)?(,?[a-z]?)?" + nd + page1 + page2 + "[\)\]]"

        author1 = f"(see|see also|e\.g\.,|see e\.g\.,|accord|cf\.|but cf\.|but see|contra|compare|viz\., )?{name1}"
        author2 = f"( (and|&) {name1})?"
        author3 = f"(, {name1}, (and|&) {name1})?"
        author4 = f"(, {name1}, {name1}, (and|&) {name1})?"
        author5OrMore = f"( et al\.)?"
        authors = author1 + author2 + author3 + author4 + author5OrMore
        pattern = authors + "(,? \d{4}?[a-z]?)?(,? \d{4}?[a-z]?)?" + nd + page1 + page2 + "[\)\]]"
        matches1 = re.findall(pattern, context)

        pattpg1 = "[\[\(]" + author1 + author5OrMore + "(,? \d{4}?[a-z]?)?(,? \d{4}?[a-z]?)?(,?[a-z]?)?" + nd + page1 + page2 + "[\)\]]"
        pattpg2 = "[\[\(]" + author1 + author4 + "(,? \d{4}?[a-z]?)?(,? \d{4}?[a-z]?)?(,?[a-z]?)?" + nd + page1 + page2 + "[\)\]]"
        pattpg3 = "[\[\(]" + author1 + author3 + "(,? \d{4}?[a-z]?)?(,? \d{4}?[a-z]?)?(,?[a-z]?)?" + nd + page1 + page2 + "[\)\]]"
        pattpg4 = "[\[\(]" + author1 + author2 + "(,? \d{4}?[a-z]?)?(,? \d{4}?[a-z]?)?(,?[a-z]?)?" + nd + page1 + page2 + "[\)\]]"
        pattpg5 = "[\[\(]" + author1 + "(,? \d{4}?[a-z]?)?(,? \d{4}?[a-z]?)?(,?[a-z]?)?" + nd + page1 + page2 + "[\)\]]"

        # -----------------------------------------------------------------------------------------------------------------------------------------------

        name2 = "[A-Za-zÀ-Üà-øoù-ÿŒœß-]+"
        author1 = f"{name2}"
        author2 = f"( (and|&) {name2})?"
        author3 = f"(, {name2}, (and|&) {name2})?"
        author4 = f"(, {name2}, {name2}, (and|&) {name2})?"
        author5OrMore = f"( et al\.)?"

        authors = author1 + author2 + author3 + author4 + author5OrMore

        pattern6 = authors + " ,?[\[\(]\d{4}?(\d+)?"+ alpha + "(, \d{4}?)?"+ alpha + nd + page1 + page2 +"[\)\]]"

        page3 = "[\[\(](p\.)?(pp\.)?(chap\.)?(Ch\.)?(pg\.)?(para\.)?(para\.)?(Tab\.)?(Fig\.)?(Algorithm)?(Example)?(Sec\.)?(eq\.)?(Appendix)? \(?\d+(?:-\d+)?\)?[\)\]]"
        #context = "This is (Jones et al., 1994, eq. (8)) fine."

        if re.findall(page3, context):
            s = re.search(page3, context)
            start = s.start()
            end = s.end()
            context = context[:start] + "" + context[end:]

        matches2 = re.findall(pattern6, context)

        if len(matches1) > 1 or len(matches2) > 1:
            matchLen = len(matches1) + len(matches2)
            citeString = []

            for i in range(matchLen):
                if (len(matches2) >= 1):
                    match = re.search(pattern6, context)
                elif (len(matches1) >= 1):
                    if (len(re.findall(pattern1, context)) >= 1):
                        match = re.search(pattern1, context)
                    elif (len(re.findall(pattern2, context)) >= 1):
                        match = re.search(pattern2, context)
                    elif (len(re.findall(pattern3, context)) >= 1):
                        match = re.search(pattern3, context)
                    elif (len(re.findall(pattern4, context)) >= 1):
                        match = re.search(pattern4, context)
                    elif (len(re.findall(pattern5, context)) >= 1):
                        match = re.search(pattern5, context)

                        # including signals
                    elif (len(re.findall(pattpg1, context)) >= 1):
                        match = re.search(pattpg1, context)
                    elif (len(re.findall(pattpg2, context)) >= 1):
                        match = re.search(pattpg2, context)
                    elif (len(re.findall(pattpg3, context)) >= 1):
                        match = re.search(pattpg3, context)
                    elif (len(re.findall(pattpg4, context)) >= 1):
                        match = re.search(pattpg4, context)
                    elif (len(re.findall(pattpg5, context)) >= 1):
                        match = re.search(pattpg5, context)
                    else:

                        match = None
                else:
                    match = None

                if match:
                    start_index = match.start()
                    end_index = match.end()

                    # get citation from specific location
                    citeString.append(context[start_index:end_index])

                    # check multiples
                    context = context[:start_index] + "<REF>" + context[end_index:]

            return (context, citeString)
        else:

            return None

    def citationStyleSquare(self, context):
        name2 = "[\.\[\]A-Za-zÀ-Üà-øoù-ÿŒœß-]+( ?[\.\[\]A-Za-zÀ-Üà-øoù-ÿŒœß-]+)?"
        author1 = f"{name2}"
        author2 = f"( (and|&) {name2})?"
        author3 = f"(, {name2}, (and|&) {name2})?"
        author4 = f"(, {name2}, {name2}, (and|&) {name2})?"
        author5OrMore = f"( et al\.)?"

        authors = author1 + author2 + author3 + author4 + author5OrMore

        # context = "This is  [6, Appendix IV] fine."
        # r = '^M{0,3}(CM|CD|D?C{0,3})?(XC|XL|L?X{0,3})?(IX|IV|V?I{0,3})?'
        signals = "(see|see also|e\.g\.,|see e\.g\.,|accord|cf\.|but cf\.|but see|contra|compare|viz\.,)?"
        page1 = f"(,? (p\.)?(pp\.)?(chap\.)?(Ch\.)?(pg\.)?(para\.)?(para\.)?(Tab\.)?(Fig\.)?(Algorithm)?(Example)?(Sec\.)?(eq\.)?(Appendix)? \(?\d+(?:-\d+)?\)?(, (p\.)?(pp\.)? \d+(?:-\d+)?)?)?"
        page2 = f"(,? \d+(?:-\d+)?)?"

        # pattern match of [1], [1, p. 123], [1, pp. 123], [1, pp. 44-50],: [1, p. 44-50], [see 21]
        pattern = "[\[]" + signals + " ?\d+" + page1 + page2 +"[\]]"
        matches = re.findall(pattern, context)

        if len(matches) > 1:
            citeString = []

            for i in range(len(matches)):
                # for natbib : Jones et al. [21]
                # match = re.search(authPattern, context)

                match = re.search(pattern, context)

                if match:
                    start_index = match.start()
                    end_index = match.end()

                    # get citation from specific location
                    citeString.append(context[start_index:end_index])

                    # replace citation with <REF>
                    context = context[:start_index] + "<REF>" + context[end_index:]
            return (context, citeString)
        else:
            return None



# with open('all.json') as f:
#     d = json.load(f)

# c = MultipleCitations()

# t = c.citationStyleSquare("This is [1] and [2] others too")

# print(t)
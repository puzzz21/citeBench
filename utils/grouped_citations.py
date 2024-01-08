import requests
import json
import nltk
import re
from citation_parse import CitationParse

class GroupedCitation:
    
    def filterData(self, context):
        res = self.citationStyleRound(context)
        if res is None:
            res = self.citationStyleSquare(context)
        return res

    def citationStyleSquare(self, context):
        start_index = context.find("[")
        end_index = context.find("]")
        str = context[start_index:end_index + 1]

        pattern1 = "\d+"
        match1 = re.findall(pattern1, str)

        pattern2 = "\d+\-\d+"
        match2 = re.findall(pattern2, str)

        pattern3 = "\[\d+]\-\[\d+\]"
        match3 = re.findall(pattern3, str)

        pattern4 = r"\[\d+(?:,\d+)*\]"
        match4 = re.findall(pattern4, context)

        citeString = ""

        if len(match2) == 1:
            citeString = "[" + match2[0] + "]"
        elif len(match1) > 1:
            citeString = "[" + ",".join(match1) + "]"
        elif len(match3) > 0:
            citeString = match3
        elif len(match4) > 0:
            citeString = ",".join(match4)
            index = context.find(citeString)
            start_index = index
            end_index = index + len(citeString) - 1

        # print(start_index)
        # print(end_index)


        matches = context.find(citeString)

        if matches:
            # print(matches)
            str = context[start_index:end_index + 1]
            ref = context[:start_index] + "<ref>" + context[end_index + 1:]
            return (ref, str)
        else:
            return None

    def citationStyleRound(self,context):
        m = self.patterMatch(context)

        if m[4] != "" and ";" in m[4]:
            # check multiples
            new_context = context[:m[1]] + "<REF>" + context[m[2] + 1:]
            cp = CitationParse()

            m2 = self.patterMatch(new_context)

            x = cp.citationStyleRound(new_context,None, None)
            # y = re.findall(m[3], new_context)

            if x == None and m2[4] == "":
                return (new_context, m[4])
            else:
                return None
        else:
            return None

    def patterMatch(self, context):
        start_index = context.find("(")
        end_index = context.find(")")
        str = context[start_index:end_index + 1]

        name1 = "[\.\[\]A-Za-zÀ-Üà-øoù-ÿŒœß-]+( ?[\.\[\]A-Za-zÀ-Üà-øoù-ÿŒœß-]+)?"

        page1 = f"(,? (p\.)?(pp\.)?(chap\.)?(Ch\.)?(pg\.)?(para\.)?(para\.)?(Tab\.)?(Fig\.)?(Algorithm)?(Example)?(Sec\.)?(eq\.)? \(?\d+(?:-\d+)?\)?)?"
        page2 = f"(,? \d+(?:-\d+)?)?"
        nd = f"(,? n.d.)?"
        alpha = f"[a-z]?"

        author1 = f"(see|see also|e\.g\.,|see e\.g\.,|accord|cf\.|but cf\.|but see|contra|compare|viz\., )?{name1}"
        author2 = f"( (and|&) {name1})?"
        author3 = f"(, {name1}, (and|&) {name1})?"
        author4 = f"(, {name1}, {name1}, (and|&) {name1})?"
        author5OrMore = f"( et al\.)?"
        authors = author1 + author2 + author3 + author4 + author5OrMore

        pattern = authors + "(,? \d{4}?[a-z]?)?(,? \d{4}?[a-z]?)?" + nd + page1 + page2
        matches1 = re.findall(pattern, str)

        if matches1 == None:
            return None
        else:
            return (matches1, start_index, end_index, pattern, str)


    def getLength(self, context):
        # Get length of the context

        wordsLen = len(context.split())
        if wordsLen <= 10:
            return "short"
        elif wordsLen > 10 and wordsLen <= 20:
            return "medium"
        else:
            return "long"


# with open('all.json') as f:
#     d = json.load(f)


# c = GroupedCitation()

# context = "This is [1],[2],[3],[4] and others too."
# print(c.citationStyleSquare(context))


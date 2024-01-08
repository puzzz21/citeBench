import requests
import json
import nltk
import re

class CitationParse:
    
    def groupedCitationStyleRound(self,context):
        m = self.patterMatch(context)

        if m[4] != "" and ";" in m[4]:
            # check multiples
            new_context = context[:m[1]] + "<REF>" + context[m[2] + 1:]

            m2 = self.patterMatch(new_context)

            # x = citationStyleRound(new_context)
            # y = re.findall(m[3], new_context)

            if m2[4] == "":
                return (new_context, m[4])
            else:
                return None
        else:
            return None
        
    def patterMatch(self, context):
        start_index = context.find("(")
        end_index = context.find(")")
        str = context[start_index:end_index + 1]
        romanCh = '(M{0,3}(CM|CD|D?C{0,3})?(XC|XL|L?X{0,3})?(IX|IV|V?I{0,3})?)?'


        name1 = "[\.\[\]A-Za-zÀ-Üà-øoù-ÿŒœß-]+( ?[\.\[\]A-Za-zÀ-Üà-øoù-ÿŒœß-]+)?"

        page1 = f"(,? (p\.)?(pp\.)?([cC]hap\.)?([cC]h\.)?([pP]g\.)?([pP]ara\.)?([tT]ab\.)?([fF]ig\.)?([aA]lgorithm)?([eE]xample)?([sS]ec\.)?([eE]q\.)?([aA]ppendix)?([lL]emma)? {romanCh}\(?\d+(?:-\d+)?\)?)?"
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
        

    def citationStyleRound(self, context, authorList, year):
        # pattern match of (abc et al., 2019) or [abc et al.,2019] or (abc et al., 2019, p. 2) (abc et al., 2019, pp. 2) (abc et al., 2019, 2)
        # abc et al. (2019, 2), abc et al. (2019, p. 2), abc et al. (2019, pp. 2)
        # (Smith n.d.), Smith (n.d.)
        # (Jackson, 2013a) (Jackson, abc, 2013a) (Jackson, abc, xyz, 2013a) (Jackson et al., 2013a, 2013b) (Jackson, 2013a, 2013b) (Bednarik and test, 2003a, 2005b)
        # (Bednarik, Bednarik, and test, 2003a) (Bednarik and test, 2003a) (Bednarik & test, 2003a, 2003b) (Bednarik, Bednarik, & test, 2003a) (Bednarik, Bednarik, & test, 2003a, 2003b)
        # (Bednarik, Bednarik, Bednarik, & test, 2003a, 2003b)
        # Gass and Varonis (1984)   Gass & Varonis (1984)   Jackson (2013, p. 12)  Jackson (2013, 12)
        # Jackson (1994a, 1994b) Jackson et al. (1994a, 1994b)
        # (U.S Flood, 1993)
        # ACM:  [Philips 2001]  [Whitaker and abc 2014]  [Vicente et al. 2021]
        # ACM: (Vicente et al. 2021) (Whitaker and abc 2014)
        # Harvard:  (Singh, 2015, p. 13) Wilson (2015, pp. 12-14) (Jones et al., 2016, p. 155) Jones et al. (2016, p. 155)
        # (Smith n.d.) (Johnson and Smith 2017, 119)  (E. Johnson, 2001)
        # signals: (see|see also|e.g.,|see e.g.,|accord|cf.|but cf.|but see|contra|Compare|viz., test et al., 1994)
        # Jones et al. (1990, chap. 2) (Jones et al., 1990, chap. 2)  (see Jones et al., 1990, chap. 2)
        # This is (see Jones et al., 1990, p. 1) fine (p. 1).
        # [1, p. 1]  (Jones et al., 1994, eq. (8))
        # (World Health Organization [WHO], 1990)
        # (e.g., Jenkins & Morgan, 2010)
        # (viz., test, 1994)
        # (viz., Black & Avery, 2008)

        name1 = "[\.\[\]A-Za-zÀ-Üà-øoù-ÿŒœß-]+( ?[\.\[\]A-Za-zÀ-Üà-øoù-ÿŒœß-]+)?"
        author1 = f"{name1}"
        author2 = f"{name1} (and|&) {name1}"
        author3 = f"{name1}, {name1}, (and|&) {name1}"
        author4 = f"{name1}, {name1}, {name1}, (and|&) {name1}"
        author5OrMore = f"{name1} et al\."

        romanCh = '(M{0,3}(CM|CD|D?C{0,3})?(XC|XL|L?X{0,3})?(IX|IV|V?I{0,3})?)?'

        page1 = f"(,? (p\.)?(pp\.)?([cC]hap\.)?([cC]h\.)?([pP]g\.)?([pP]ara\.)?([tT]ab\.)?([fF]ig\.)?([aA]lgorithm)?([eE]xample)?([sS]ec\.)?([eE]q\.)?([aA]ppendix)?([lL]emma)? {romanCh}\(?\d+(?:-\d+)?\)?)?"
        page2 = f"(,? \d+(?:-\d+)?)?"
        nd = f"(,? n.d.)?"
        alpha = f"[a-z]?"

        pattern1 = "[\[\(]" + author5OrMore + "(,? \d{4}[a-z]?)(,? \d{4}?[a-z]?)?(,?[a-z]?)?" + nd + page1 + page2 + "[\)\]]"
        pattern2 = "[\[\(]" + author4 + "(,? \d{4}[a-z]?)(,? \d{4}?[a-z]?)?(,?[a-z]?)?" + nd + page1 + page2 + "[\)\]]"
        pattern3 = "[\[\(]" + author3 + "(,? \d{4}[a-z]?)(,? \d{4}?[a-z]?)?(,?[a-z]?)?" + nd + page1 + page2 + "[\)\]]"
        pattern4 = "[\[\(]" + author2 + "(,? \d{4}[a-z]?)(,? \d{4}?[a-z]?)?(,?[a-z]?)?" + nd + page1 + page2 + "[\)\]]"
        pattern5 = "[\[\(]" + author1 + "(,? \d{4}[a-z]?)(,? \d{4}?[a-z]?)?(,?[a-z]?)?" + nd + page1 + page2 + "[\)\]]"

        author1 = f"(see |see also |e\.g\., |see e\.g\., |accord |cf\. |but cf\. |but see |contra |compare |viz\., )?{name1}"
        author2 = f"( (and|&) {name1})?"
        author3 = f"(, {name1}, (and|&) {name1})?"
        author4 = f"(, {name1}, {name1}, (and|&) {name1})?"
        author5OrMore = f"( et al\.)?"
        
        authors = author1 + author2 + author3 + author4 + author5OrMore

        pattern = authors + "(,? \d{4}[a-z]?)(,? \d{4}?[a-z]?)?" + nd + page1 + page2
        matches1 = re.findall(pattern, context)
        

        pattpg1 = "[\[\(]" + author1 + author5OrMore + "(,? \d{4}[a-z]?)(,? \d{4}?[a-z]?)?(,?[a-z]?)?" + nd + page1 + page2 + "[\)\]]"
        pattpg2 = "[\[\(]" + author1 + author4 + "(,? \d{4}[a-z]?)(,? \d{4}?[a-z]?)?(,?[a-z]?)?" + nd + page1 + page2 + "[\)\]]"
        pattpg3 = "[\[\(]" + author1 + author3 + "(,? \d{4}[a-z]?)(,? \d{4}?[a-z]?)?(,?[a-z]?)?" + nd + page1 + page2 + "[\)\]]"
        pattpg4 = "[\[\(]" + author1 + author2 + "(,? \d{4}[a-z]?)(,? \d{4}?[a-z]?)?(,?[a-z]?)?" + nd + page1 + page2 + "[\)\]]"
        pattpg5 = "[\[\(]" + author1 + "(,? \d{4}[a-z]?)(,? \d{4}?[a-z]?)?(,?[a-z]?)?" + nd + page1 + page2 + "[\)\]]"

        # -----------------------------------------------------------------------------------------------------------------------------------------------

        name2 = "[A-Za-zÀ-Üà-øoù-ÿŒœß-]+"
        author1 = f"{name2}"
        author2 = f"( (and|&) {name2})?"
        author3 = f"(, {name2}, (and|&) {name2})?"
        author4 = f"(, {name2}, {name2}, (and|&) {name2})?"
        author5OrMore = f"( et al\.)?"

        authors = author1 + author2 + author3 + author4 + author5OrMore

        pattern6 = authors + " ,?[\[\(]\d{4}(\d+)?"+ alpha + "(, \d{4}?)?"+ alpha + nd + page1 + page2 +"[\)\]]"

        page3 = "[\[\(](p\.)?(pp\.)?([cC]hap\.)?([cC]h\.)?([pP]g\.)?([pP]ara\.)?([tT]ab\.)?([fF]ig\.)?([aA]lgorithm)?([eE]xample)?([sS]ec\.)?([eE]q\.)?([aA]ppendix)?([lL]emma)? {romanCh}\(?\d+(?:-\d+)?\)?[\)\]]"
        #context = "This is (Jones et al., 1994, eq. (8)) fine."

        if re.findall(page3, context):
            s = re.search(page3, context)
            start = s.start()
            end = s.end()
            context = context[:start] + "" + context[end:]

        matches2 = re.findall(pattern6, context)
        
        grouped = self.groupedCitationStyleRound(context)

        if (len(matches1) == 1 or len(matches2) == 1) and grouped is None:
            
            if (len(matches2) == 1):
                match = re.search(pattern6, context)
            elif (len(matches1) == 1):
                    # without including signals
                if (len(re.findall(pattern1, context)) == 1):
                    match = re.search(pattern1, context)
                elif (len(re.findall(pattern2, context)) == 1):
                    match = re.search(pattern2, context)
                elif (len(re.findall(pattern3, context)) == 1):
                    match = re.search(pattern3, context)
                elif (len(re.findall(pattern4, context)) == 1):
                    match = re.search(pattern4, context)
                elif (len(re.findall(pattern5, context)) == 1):
                    match = re.search(pattern5, context)
                    # including signals
                elif (len(re.findall(pattpg1, context)) == 1):
                    match = re.search(pattpg1, context)
                elif (len(re.findall(pattpg2, context)) == 1):
                    match = re.search(pattpg2, context)
                elif (len(re.findall(pattpg3, context)) == 1):
                    match = re.search(pattpg3, context)
                elif (len(re.findall(pattpg4, context)) == 1):
                    match = re.search(pattpg4, context)
                elif (len(re.findall(pattpg5, context)) == 1):
                    match = re.search(pattpg5, context)
                else:
                    match = None

            else:
                match = None

            if match:
                start_index = match.start()
                end_index = match.end()

                # get citation from specific location
                citeString = context[start_index:end_index]

                # check multiples
                new_context = context[:start_index] + "<REF>" + context[end_index:]

                return (new_context, citeString)
            
        elif len(matches1) > 1 or len(matches2) > 1 or grouped is not None:
            return "many"
        else:
            return None

    def citationStyleSquare(self, context, authorList, year):

        # context = "This is  [6, Appendix IV] fine."

        # context = "This is  [6, Appendix IV] fine."
        romanCh = '(M{0,3}(CM|CD|D?C{0,3})?(XC|XL|L?X{0,3})?(IX|IV|V?I{0,3})?)?'

        signals = "(see|see also|e\.g\.,|see e\.g\.,|accord|cf\.|but cf\.|but see|contra|compare|viz\.,)?"

        page1 = f"(,? (p\.)?(pp\.)?([cC]hap\.)?([cC]h\.)?([pP]g\.)?([pP]ara\.)?([tT]ab\.)?([fF]ig\.)?([aA]lgorithm)?([eE]xample)?([sS]ec\.)?([eE]q\.)?([aA]ppendix)?([lL]emma)? {romanCh}(\(?\d+(?:-\d+)?\)?(, (p\.)?(pp\.)? \d+(?:-\d+)?)?)?)?"

        page2 = f"(,? \d+(?:-\d+)?)?"

        # pattern match of [1], [1, p. 123], [1, pp. 123], [1, pp. 44-50],: [1, p. 44-50], [see 21]
        pattern = "[\[]" + signals + " ?\d+" + page1 + page2 +"[\]]"
        
        matches = re.findall(pattern, context)

         #pattern match of [1-10]
        dashPattern = r"[\[]\d+-\d+[\]]"
        dashMatches = re.findall(dashPattern, context)

        # #pattern match of [1]-[10]
        dashPattern2 = r"[\[]\d+[\]]-[\[]\d+[\]]"
        dashMatches2 = re.findall(dashPattern2, context)

        # pattern match of [1,2,3,10]
        commaPattern = r"[\[]\d+\,\d+\,?"
        commaMatches = re.findall(commaPattern, context)
        
        authors = self.getAuthorName(authorList)
                    

        if authors:
            authorPatttern = authors + " " + pattern
            authorMatch = re.findall(authorPatttern, context)
        else:
            authorMatch = []

        if len(authorMatch) == 1:
                # for natbib : Jones et al. [21]
            match = re.search(authorPatttern, context)
        elif len(matches) == 1 and len(dashMatches) == 0 and len(dashMatches2) == 0 and len(commaMatches) == 0 :
            match = re.search(pattern, context)
        else:
            match = None

        if match:
            start_index = match.start()
            end_index = match.end()

                # get citation from specific location
            citeString = context[start_index:end_index]

                # replace citation with <REF>
            new_context = context[:start_index] + "<REF>" + context[end_index:]

            return (new_context, citeString)
        else:
            return None


    def citationStyleSuperScript(self, context, authorList, year):
        pattern = r"\u00B2|\u00B3|\u2070|\u2071|\u2074|\u2075|\u2076|\u2077|\u2078|\u2079"

        match = re.findall(pattern, context)

        if len(match) == 1:

            match = re.search(pattern, context)

            if match:
                start_index = match.start()
                end_index = match.end()

                # get citation from specific location
                citeString = context[start_index:end_index]
                
                isNotAuthCite = True
                for auth in authorList:
                    a = auth.split(" ")
                    if a[len(a) - 1] in citeString:
                        isNotAuthCite = False
                        
                if isNotAuthCite:    
                    start_index = context.find("[")
                    citeString = context[start_index:end_index]

                # replace citation with <REF>
                new_context = context[:start_index] + "<REF>" + context[end_index:]

                return (new_context, citeString)
        else:
            return None

    def citationStyleNoBracket(self, context, authorList, year):
        name = "[\.\[\]A-Za-zÀ-Üà-øoù-ÿŒœß-]+( ?[\.\[\]A-Za-zÀ-Üà-øoù-ÿŒœß-]+)?"
        author1 = f"{name}"
        author2 = f"( (and|&) {name})?"
        author3 = f"(, {name}, (and|&) {name})?"
        author4 = f"(, {name}, {name}, (and|&) {name})?"
        author5OrMore = f"( et al\.)?"

        authors = author1 + author2 + author3 + author4 + author5OrMore

        romanCh = '(M{0,3}(CM|CD|D?C{0,3})?(XC|XL|L?X{0,3})?(IX|IV|V?I{0,3})?)?'
        page1 = f"(,? (p\.)?(pp\.)?([cC]hap\.)?([cC]h\.)?([pP]g\.)?([pP]ara\.)?([tT]ab\.)?([fF]ig\.)?([aA]lgorithm)?([eE]xample)?([sS]ec\.)?([eE]q\.)?([aA]ppendix)?([lL]emma)? {romanCh}\(?\d+(?:-\d+)?\)?)?"
        page2 = f"(,? \d+(?:-\d+)?)?"
        nd = f"(,? n.d.)?"

        pattern = authors + "(,? \d{4}[a-z]?)(,? \d{4}?[a-z]?)?" + nd + page1 + page2

        match = re.search(pattern, context)
        matches = re.findall(pattern, context)

        if match and len(matches) == 1:
            start_index = match.start()
            end_index = match.end()

            # get citation from specific location
            citeString = context[start_index:end_index]

            authorCitation = self.getAuthorName(authorList)

            if authorCitation is None: return None
            
            if authorCitation in citeString and str(year) in citeString:
                new_context = context[:start_index] + "<REF>" + context[end_index:]
                return (new_context, citeString)
            else:
                return None



    def citationStylePartial(self, context, authorList, year):
        authors = self.getAuthorName(authorList)
        if authors is None: return None
        position = context.find(authors)
        yearPos = context.find(str(year))
        if position >= 0:
            newContext = context[:position] + "<REF>" + context[position + len(authors):]
            return (newContext, authors)
        elif yearPos >= 0:
            if context[yearPos - 1] == "(":
                yearPos = yearPos - 1
                newContext = context[:yearPos] + "<REF>" + context[yearPos + len(str(year)) + 2:]
                return (newContext, "(" + str(year) + ")")
            else:
                newContext = context[:yearPos] + "<REF>" + context[yearPos + len(str(year)):]
                return (newContext, str(year))
        else:
            return None

    def citationStyleCase(self, context, authorList, year):
        authors = self.getAuthorFullName(authorList)
        position = context.lower().find(authors.lower())
        yearPos = context.find(str(year))
        if (position >= 0 and yearPos >= 0):
            authorName1 = authors + " (" + str(year) + ")"
            authorName2 = authors + " " + str(year)
            authorName3 = "(" + authors + ", " + str(year) + ")"
            authorName4 = authors + ", " + str(year)
            pos1 = context.lower().find(authorName1.lower())
            pos2 = context.lower().find(authorName2.lower())
            pos3 = context.lower().find(authorName3.lower())
            pos4 = context.lower().find(authorName4.lower())
            if (pos1 >= 0):
                newContext = context[:pos1] + "<REF>" + context[pos1 + len(authorName1):]
                return (newContext, context[pos1:pos1 + len(authorName1)])
            elif (pos2 >= 0):
                newContext = context[:pos2] + "<REF>" + context[pos2 + len(authorName2):]
                return (newContext, context[pos2:pos2 + len(authorName2)])
            elif (pos3 >= 0):
                newContext = context[:pos3] + "<REF>" + context[pos3 + len(authorName3):]
                return (newContext, context[pos3:pos3 + len(authorName3)])
            elif (pos4 >= 0):
                newContext = context[:pos4] + "<REF>" + context[pos4 + len(authorName4):]
                return (newContext, context[pos4:pos4 + len(authorName4)])
            else:
                return None
        elif position >= 0 and yearPos < 0:
            newContext = context[:position] + "<REF>" + context[position + len(authors):]
            return (newContext, context[position:position + len(authors)])

    def citationStyleNoBracket(self, context, authorList, year):
        name = "[\.\[\]A-Za-zÀ-Üà-øoù-ÿŒœß-]+( ?[\.\[\]A-Za-zÀ-Üà-øoù-ÿŒœß-]+)?"
        author1 = f"{name}"
        author2 = f"( (and|&) {name})?"
        author3 = f"(, {name}, (and|&) {name})?"
        author4 = f"(, {name}, {name}, (and|&) {name})?"
        author5OrMore = f"( et al\.)?"

        authors = author1 + author2 + author3 + author4 + author5OrMore

        romanCh = '(M{0,3}(CM|CD|D?C{0,3})?(XC|XL|L?X{0,3})?(IX|IV|V?I{0,3})?)?'

        page1 = f"(,? (p\.)?(pp\.)?([cC]hap\.)?([cC]h\.)?([pP]g\.)?([pP]ara\.)?([tT]ab\.)?([fF]ig\.)?([aA]lgorithm)?([eE]xample)?([sS]ec\.)?([eE]q\.)?([aA]ppendix)?([lL]emma)? {romanCh}\(?\d+(?:-\d+)?\)?)?"
        page2 = f"(,? \d+(?:-\d+)?)?"
        nd = f"(,? n.d.)?"

        pattern = authors + "(,? \d{4}?[a-z]?)?(,? \d{4}?[a-z]?)?" + nd + page1 + page2

        match = re.search(pattern, context)

        if match:
            start_index = match.start()
            end_index = match.end()

            # get citation from specific location
            citeString = context[start_index:end_index]

            authorCitation = self.getAuthorName(authorList)

            if authorCitation:
                position = citeString.find(authorCitation)
            else:
                position = -1

            if (position == 0):
                new_context = context[:start_index] + "<REF>" + context[end_index:]
                return (new_context, citeString)
            elif (position > 0):
                new_context = context[:start_index + position] + "<REF>" + context[end_index:]
                return (new_context, citeString)
            else:
                return None

    def citationStyleVancouver(self, context, authorList, year):
        authors = self.getAuthorName(authorList)

        signals = "(see|see also|e\.g\.,|see e\.g\.,|accord|cf\.|but cf\.|but see|contra|compare|viz\.,)?"
        romanCh = '(M{0,3}(CM|CD|D?C{0,3})?(XC|XL|L?X{0,3})?(IX|IV|V?I{0,3})?)?'

        page1 = f"(,? (p\.)?(pp\.)?([cC]hap\.)?([cC]h\.)?([pP]g\.)?([pP]ara\.)?([tT]ab\.)?([fF]ig\.)?([aA]lgorithm)?([eE]xample)?([sS]ec\.)?([eE]q\.)?([aA]ppendix)?([lL]emma)? {romanCh}\(?\d+(?:-\d+)?\)?(, (p\.)?(pp\.)? \d+(?:-\d+)?)?)?"
        page2 = f"(,? \d+(?:-\d+)?)?"
        # Equation (3) Eq. (3)
        
        # pattern match of (1), (1, p. 123), (1, pp. 123), (1, pp. 44-50),: (1, p. 44-50), (see 21)
        if authors:
            authPattern = authors + " [\(]" + signals + " ?\d+" + page1 + page2 +"[\)]"
            authMatch = re.findall(authPattern, context)
            authorNameStyle = self.getVancouverAuthorName(authorList)
            position = context.find(authorNameStyle)
        else:
            authMatch = []
            position = -1
            

        pattern = "[\(]" + signals + " ?\d+" + page1 + page2 +"[\)]"


        match = re.findall(pattern, context)

       
        # authorStyleMatch =  re.findall(authPattern, context)

        negPattern = "([eE]quation|[eE]q\.) [\(]\d[\)]"
        negMatch = re.findall(negPattern, context)

        if (len(match) == 1 or len(authMatch) == 1) and len(negMatch) < 1:

            if len(authMatch) == 1:
                match = re.search(authPattern, context)
            else:
                match = re.search(pattern, context)

            if match:
                start_index = match.start()
                end_index = match.end()

                # get citation from specific location
                citeString = context[start_index:end_index]

                # replace citation with <REF>
                newContext = context[:start_index] + "<REF>" + context[end_index:]

                return (newContext, citeString)
        elif (position >= 0 ):
            citeString = context[position:position + len(authorNameStyle)]
            newContext = context[:position] + "<REF>" + context[position + len(authorNameStyle):]
            return (newContext, citeString)
        else:
            return None

    def getAuthorFullName(self, authors):
        lastNameAuthor = authors[0]
        return lastNameAuthor

    def getAuthorName(self, authors):
        isNameLen = True
        lastNameAuthor = None
        
        for i in authors:
            chCheck = [x in ["(",";",")"] for x in i]
            if len(i.split(" ")) <= 1 or True in chCheck:
                isNameLen = False
                                    
        if isNameLen:
            if (len(authors) > 3):
                lastNameAuthor = authors[0].split(" ")[1] + " et al."
            elif (len(authors) == 3):
                lastNameAuthor = authors[0].split(" ")[1] + ", " + authors[1].split(" ")[1] + ", and " + authors[2].split(" ")[1]
            elif (len(authors) == 2):
                lastNameAuthor = authors[0].split(" ")[1] + ", and " + authors[1].split(" ")[1]
            else:
                lastNameAuthor = authors[0].split(" ")[1]

        return lastNameAuthor

    def getVancouverAuthorName(self, authors):
        ath = [x.split()[1] + " " + x.split()[0] for x in authors]


        if (len(authors) > 6):
            name = (", ").join(ath[:6]) + " et al."
        elif (len(authors) <= 6 and len(authors) > 1):
            name = (", ").join(ath)
        else:
            ath = authors[0].split(" ")
            name = ath[1] + " " + ath[0]

        return name

    def multipleCitationStyleRound(self, context):
        print(1)
        
        
   
        

# cp = CitationParse()
# sent = "Along a different [1] used a genetic algorithm to solve the order allocation problem of a manufacturer among multiple suppliers when supply disruptions occur and quantity discounts exist."
# authors = ["F James", "J Pieters", "G Deptford", "R Harrison", "E Bregman", "A Empson", "T Abc"]

# year = 1998
# (1, 2), (1, 4 - 7),

# 1, pp.
# 44 - 50]
# Algorithms: [1, Algorithm 2]
# Appendices: [2, Appendix II]
# Chapters: [3, Ch. 4]
# Equations: [4, eq.(1)]
# Examples: [5, Example 3]
# Figures: [6, Fig. 1]
# Lemmas: [7, Lemma 2]
# Paragraphs: [8, para. 10]
# Sections: [9, Sec. 14]
# Tables: [10, Tab. 5]

# print(cp.citationStyleSquare("Naming the authors [7, para. 2].",authors, 100))
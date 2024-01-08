import requests


class APIRequest:

    def __inti__(self):
        print("1")

    def readS2ORC(self):
        key = 'X-API-Key'
        secret = '9SRyIGUz4I7uk3H314wxW521fMySE3qR5WPY7I60'
        url = 'https://api.semanticscholar.org/datasets/v1/release/2022-08-16/dataset/papers'
        headers = {
            'Accept': '*/*',
            key: secret
        }

        response = requests.get(url, headers=headers)
        res = response.json()
        return res

    def getPaper(self,id):
        key = 'X-API-Key'
        secret = '9SRyIGUz4I7uk3H314wxW521fMySE3qR5WPY7I60'

        headers = {
            'Accept': '*/*',
            key: secret
        }

        r = requests.post(
            'https://api.semanticscholar.org/graph/v1/paper/batch',
            params={'fields': 'abstract,year,citationCount,fieldsOfStudy,publicationVenue,journal,publicationDate,authors'},
            json={"ids": [id]},
            headers=headers
        )


        res = r.json()
        return res

    def getRefData(self, id):
        key = 'X-API-Key'
        secret = '9SRyIGUz4I7uk3H314wxW521fMySE3qR5WPY7I60'

        headers = {
            'Accept': '*/*',
            key: secret,
            'Content-Type':'application/json'
        }

        r = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/" + id + "/references",
            params={'fields': 'intents,isInfluential,paperId,corpusId,title,venue,publicationVenue,year,referenceCount,citationCount,influentialCitationCount,fieldsOfStudy,publicationTypes,publicationDate,journal,citationStyles'},
            headers=headers
        )


        res = r.json()
        return res
    
    def getMetaBatch(ids):
        key = 'X-API-Key'
        secret = '9SRyIGUz4I7uk3H314wxW521fMySE3qR5WPY7I60'

        headers = {
            'Accept': '*/*',
            key: secret,
            'Content-Type':'application/json'
        }

        r = requests.post(
            "https://api.semanticscholar.org/graph/v1/paper/batch",
            params={'fields': 'paperId,corpusId,title,venue,publicationVenue,year,authors.authorId,authors.externalIds,authors.url,authors.name,authors.aliases,authors.affiliations,authors.homepage,authors.paperCount,authors.citationCount,authors.hIndex,externalIds,abstract,referenceCount,citationCount,influentialCitationCount,fieldsOfStudy,isOpenAccess,s2FieldsOfStudy,publicationTypes,publicationDate,journal,citationStyles'},
            json={"ids":ids},
            headers=headers
        )

        res = r.json()
        return res
    
    
    def getAbstract(ids):
        key = 'X-API-Key'
        secret = '9SRyIGUz4I7uk3H314wxW521fMySE3qR5WPY7I60'

        headers = {
            'Accept': '*/*',
            key: secret,
            'Content-Type':'application/json'
        }

        r = requests.post(
            "https://api.semanticscholar.org/graph/v1/paper/batch",
            params={'fields': 'abstract'},
            json={"ids":ids},
            headers=headers
        )

        res = r.json()
        return res
    
    
    def getMetaInfo(id):
        key = 'X-API-Key'
        secret = '9SRyIGUz4I7uk3H314wxW521fMySE3qR5WPY7I60'

        headers = {
            'Accept': '*/*',
            key: secret,
            'Content-Type':'application/json'
        }

        r = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/" + id+ "?fields=abstract,year,citationCount,fieldsOfStudy,publicationVenue,journal,publicationDate,authors",
            headers=headers
        )

        res = r.json()
        return res

    def getMetaBatch2(ids):
        key = 'X-API-Key'
        secret = '08nUufESEn900G2VnSUq2aaMUTWC7vjx4NhPVvJ7'

        headers = {
            'Accept': '*/*',
            key: secret,
            'Content-Type':'application/json'
        }

        r = requests.post(
            "https://api.semanticscholar.org/graph/v1/paper/batch",
            params={'fields': 'paperId,corpusId,title,venue,publicationVenue,year,authors.authorId,authors.externalIds,authors.url,authors.name,authors.aliases,authors.affiliations,authors.homepage,authors.paperCount,authors.citationCount,authors.hIndex,externalIds,abstract,referenceCount,citationCount,influentialCitationCount,fieldsOfStudy,isOpenAccess,s2FieldsOfStudy,publicationTypes,publicationDate,journal,citationStyles'},
            json={"ids":ids},
            headers=headers
        )

        res = r.json()
        return res

    def getData(self, id):
        return self.getPaper(id)
    
    def getCitingData(self, id):
        key = 'X-API-Key'
        secret = '08nUufESEn900G2VnSUq2aaMUTWC7vjx4NhPVvJ7'

        headers = {
            'Accept': '*/*',
            key: secret,
            'Content-Type':'application/json'
        }

        r = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/" + id + "/citations",
            params={'fields': 'intents,isInfluential,paperId,corpusId,title,venue,publicationVenue,year,referenceCount,citationCount,influentialCitationCount,fieldsOfStudy,publicationTypes,publicationDate,journal,citationStyles,contexts,authors,isOpenAccess,externalIds,abstract'},
            headers=headers
        )


        res = r.json()
        return res
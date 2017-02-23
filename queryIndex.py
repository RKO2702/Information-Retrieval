import spell
import sys
import re
from porterStemmer import PorterStemmer
from collections import defaultdict
import copy
from nltk.stem.wordnet import WordNetLemmatizer
lmtzr = WordNetLemmatizer()

porter=PorterStemmer()

class QueryIndex:

    def __init__(self):
        self.index={}
        self.titleIndex={}
        self.tf={}
        self.idf={}


    def intersectLists(self,lists):
        if len(lists)==0:
            return []

        lists.sort(key=len)
        return list(reduce(lambda x,y: set(x)&set(y),lists))


    def getStopwords(self):
        f=open(self.stopwordsFile, 'r')
        stopwords=[line.rstrip() for line in f]
        self.sw=dict.fromkeys(stopwords)
        f.close()


    def getTerms(self, line):
        line=line.lower()
        line=re.sub(r'[^a-z0-9 ]',' ',line)
        line=line.split()
        line=[x for x in line if x not in self.sw]
        line=[ porter.stem(word, 0, len(word)-1) for word in line]
        return line


    def Postings(self, terms):

        return [ self.index[t] for t in terms ]


    def getDocs(self, postings):

        return [ [x[0] for x in post] for post in postings ]


    def readIndex(self):

        f=open(self.indexFile, 'r');

        self.numDocuments=int(f.readline().rstrip())
        for line in f:
            line=line.rstrip()
            term, postings, tf, idf = line.split('|')
            postings=postings.split(';')
            postings=[x.split(':') for x in postings]
            postings=[ [int(x[0]), map(int, x[1].split(','))] for x in postings ]
            self.index[term]=postings

            tf=tf.split(',')
            self.tf[term]=map(float, tf)

            self.idf[term]=float(idf)
        f.close()


        f=open(self.titleIndexFile, 'r')
        for line in f:
            pageid, title = line.rstrip().split(' ', 1)
            self.titleIndex[int(pageid)]=title
        f.close()


    def dotProduct(self, v1, v2):
        if len(v1)!=len(v2):
            return 0
        return sum([ x*y for x,y in zip(v1,v2) ])


    def ranking(self, terms, docs):

        dVectors=defaultdict(lambda: [0]*len(terms))
        queryVector=[0]*len(terms)
        for termIndex, term in enumerate(terms):
            if term not in self.index:
                continue

            queryVector[termIndex]=self.idf[term]

            for docIndex, (doc, postings) in enumerate(self.index[term]):
                if doc in docs:
                    dVectors[doc][termIndex]=self.tf[term][docIndex]

        #calculate the score of each doc
        docScores=[ [self.dotProduct(curDocVec, queryVector), doc] for doc, curDocVec in dVectors.iteritems() ]
        docScores.sort(reverse=True)
        result=[x[1] for x in docScores][:15]
        #print document titles instead if document id's
        result=[ self.titleIndex[x] for x in result ]
        print '\n'.join(result), '\n'


    def queryType(self,q):
        if '"' in q:
            return 'phrase'
        elif len(q.split()) > 1:
            return 'free'
        else:
            return 'one_word'


    def one_word(self,q):
        '''One Word Query'''
        originalQuery=q
        q=self.getTerms(q)
        if len(q)==0:
            print ''
            return
        elif len(q)>1:
            self.free(originalQuery)
            return

        #q contains only 1 term
        term=q[0]
        if term not in self.index:

            term=spell.correct(term,self.spellCheck)
            #term=spell.correct(term)
            print 'did you meant',
            term=lmtzr.lemmatize(term)
            q=[]
            q.append(term)
            print term
        postings=self.index[term]
        #print postings
        docs=[x[0] for x in postings]
        #print docs
        self.ranking(q, docs)


    def free(self,q):

        q=self.getTerms(q)
        if len(q)==0:
            print ''
            return

        li=set()
        for term in q:
            try:
                postings=self.index[term]
                docs=[x[0] for x in postings]
                li=li|set(docs)
            except:
                #term not in index
                pass

        li=list(li)
        self.ranking(q, li)


    def phrase(self,q):
        '''Phrase Query'''
        originalQuery=q
        q=self.getTerms(q)
        if len(q)==0:
            print ''
            return
        elif len(q)==1:
            self.one_word(originalQuery)
            return

        phraseDocs=self.phraseDocs(q)
        self.ranking(q, phraseDocs)


    def phraseDocs(self, q):

        phraseDocs=[]
        length=len(q)

        for t in q:
            if t not in self.index:

                return []

        postings=self.Postings(q)
        docs=self.getDocs(postings)

        docs=self.intersectLists(docs)

        for i in xrange(len(postings)):
            postings[i]=[x for x in postings[i] if x[0] in docs]


        postings=copy.deepcopy(postings)

        for i in xrange(len(postings)):
            for j in xrange(len(postings[i])):
                postings[i][j][1]=[x-i for x in postings[i][j][1]]


        result=[]
        for i in xrange(len(postings[0])):
            li=self.intersectLists( [x[i][1] for x in postings] )
            if li==[]:
                continue
            else:
                result.append(postings[0][i][0])

        return result


    def inputFile(self):
        param=sys.argv
        self.stopwordsFile=param[1]
        self.indexFile=param[2]
        self.titleIndexFile=param[3]
        self.spellCheck=param[4]


    def queryIndex(self):
        self.inputFile()
        self.readIndex()
        self.getStopwords()

        while True:
            print 'Enter query'
            #q=sys.stdin.readline()
            q=raw_input()
            if q=='':
                break
            print 'Enter number:'
            s=raw_input()
            if s=='1':
                print lmtzr.lemmatize(q)
            elif s=='2':
                print spell.correct(q,self.spellCheck)
            else:
                qt=self.queryType(q)
                if qt=='one_word':
                    self.one_word(q)
                elif qt=='free':
                    self.free(q)
                elif qt=='phrase':
                    self.phrase(q)


if __name__=='__main__':
    q=QueryIndex()
    q.queryIndex()

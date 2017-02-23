#kss
import sys
import re
from porterStemmer import PorterStemmer
from collections import defaultdict
from array import array
import gc
import math

porter=PorterStemmer()

class InvertedIndex:

    def __init__(self):
        self.index=defaultdict(list)
        self.titleIndex={}
        self.tf=defaultdict(list)

        self.df=defaultdict(int)
        self.numDocuments=0


    def getStopwords(self):

        f=open(self.swFile, 'r')
        stopwords=[lin.rstrip() for lin in f]
        self.sw=dict.fromkeys(stopwords)
        f.close()


    def getTerms(self, lines):

        lines=lines.lower()
        lines=re.sub(r'[^a-z0-9 ]',' ',lines)
        lines=lines.split()
        lines=[x for x in lines if x not in self.sw]
        lines=[ porter.stem(word, 0, len(word)-1) for word in lines]
        return lines


    def traverse(self):

        docs=[]
        for line in self.collFile:
            if line=='</page>\n':
                break
            docs.append(line)

        curPage=''.join(docs)
        page_id=re.search('<id>(.*?)</id>', curPage, re.DOTALL)
        page_title=re.search('<title>(.*?)</title>', curPage, re.DOTALL)
        page_text=re.search('<text>(.*?)</text>', curPage, re.DOTALL)

        if page_id==None or page_title==None or page_text==None:
            return {}

        dic={}
        dic['id']=page_id.group(1)
        dic['title']=page_title.group(1)
        dic['text']=page_text.group(1)

        return dic


    def writeFile(self):

        f=open(self.indexFile, 'w')

        print >>f, self.numDocuments
        self.numDocuments=float(self.numDocuments)
        for t in self.index.iterkeys():
            postinglist=[]
            for po in self.index[t]:
                docID=po[0]
                positions=po[1]
                postinglist.append(':'.join([str(docID) ,','.join(map(str,positions))]))
            #print data
            postingData=';'.join(postinglist)
            tfData=','.join(map(str,self.tf[t]))
            idfData='%.4f' % (self.numDocuments/self.df[t])
            print >> f, '|'.join((t, postingData, tfData, idfData))
        f.close()


        f=open(self.titleIndexFile,'w')
        for page_id, title in self.titleIndex.iteritems():
            print >> f, page_id, title
        f.close()


    def inputFile(self):

        parameter=sys.argv
        self.swFile=parameter[1]
        self.collectionFile=parameter[2]
        self.indexFile=parameter[3]
        self.titleIndexFile=parameter[4]


    def invertedIndex(self):

        self.inputFile()
        self.collFile=open(self.collectionFile,'r')
        self.getStopwords()


        gc.disable()

        pagedict={}
        pagedict=self.traverse()

        while pagedict != {}:
            lines='\n'.join((pagedict['title'],pagedict['text']))
            pageid=int(pagedict['id'])
            terms=self.getTerms(lines)

            self.titleIndex[pagedict['id']]=pagedict['title']

            self.numDocuments+=1


            termdictPage={}
            for position, term in enumerate(terms):
                try:
                    termdictPage[term][1].append(position)
                except:
                    termdictPage[term]=[pageid, array('I',[position])]


            normal=0
            for term, posting in termdictPage.iteritems():
                normal+=len(posting[1])**2
            normal=math.sqrt(normal)


            for terms, posting in termdictPage.iteritems():
                self.tf[terms].append('%.4f' % (len(posting[1])/normal))
                self.df[terms]+=1


            for termPage, postingPage in termdictPage.iteritems():
                self.index[termPage].append(postingPage)

            pagedict=self.traverse()


        gc.enable()

        self.writeFile()


if __name__=="__main__":
    c=InvertedIndex()
    c.invertedIndex()



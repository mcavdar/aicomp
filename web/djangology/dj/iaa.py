"""
The module computes inter annotator agreement statistics.
"""
from dj.models import *

def _getAnnotations(annotator1, annotator2, doc):
    return Annotation.objects.filter(document=doc,annotator=annotator1),Annotation.objects.filter(document=doc,
                                                                                                  annotator=annotator2)

def _t(a): return (a.begin_index,a.end_index)

def _overlap(t1,t2): return len(set(range(t1[0],t1[1])).intersection(set(range(t2[0],t2[1]))))

def _matchSpan(annotator1, annotator2, doc, f):
    annotations1,annotations2=_getAnnotations(annotator1,annotator2,doc)
    inds1,inds2=map(_t,annotations1),map(_t,annotations2)
    def f1(t):
        for i in inds2:
            if f(t,i):
                return True
        return False
    def f2(t):
        for i in inds1:
            if f(t,i):
                return True
        return False
    hits=map(f1, inds1).count(True)
    misses1=map(f1, inds1).count(False)
    misses2= map(f2, inds2).count(False)
    return Stats(hits, misses1, misses2)

def _matchClass(annotator1, annotator2, doc, f):
    annotations1,annotations2=_getAnnotations(annotator1,annotator2,doc)
    result={}
    annotationTypes=AnnotationType.objects.filter(project=doc.project)
    for at in annotationTypes:
        ant1,ant2=filter(lambda a: a.annotation_type==at,annotations1),filter(lambda a: a.annotation_type==at,
                                                                              annotations2)
        def f1(a):
            for i in ant2:
                if f(_t(a),_t(i)):
                    return True
            return False
        def f2(a):
            for i in ant1:
                if f(_t(a),_t(i)):
                    return True
            return False
        hits=map(f1, ant1).count(True)
        misses1=map(f1, ant1).count(False)
        misses2= map(f2, ant2).count(False)
        result[at.type]=Stats(hits,misses1,misses2)
    return result;

def matchExactSpan(annotator1, annotator2, doc):
    """ Compares the annotations of two annotators over a document.
    Only exact span matches are considered a hit. Returns a tuple of size 3 -
    the hits (number of spans annotated  by both annotators),
    the number of false positive annoations of annotator1, the number of false
    positive annotations of annotator2.

    Keyword arguments:
    annotator1 -- An Annotator object represenging the first annotator.
    annotator2 -- An Annotator object represenging the second annotator.
    doc -- Document oject prepresenting the text annotated by both annotators.


    """
    return _matchSpan(annotator1, annotator2, doc, lambda x,y: x==y)

def matchOverlapSpan(annotator1, annotator2, doc):
    """ Compares the annotations of two annotators over a document.
    Any overlapping span matches are considered a hit. Returns a tuple of size 3 -
    hits (number of spans annotated  by both annotators),
    the number of false positive annoations of annotator1, the number of false
    positive annotations of annotator2.

    Keyword arguments:
    annotator1 -- An Annotator object represenging the first annotator.
    annotator2 -- An Annotator object represenging the second annotator.
    doc -- Document oject prepresenting the text annotated by both annotators.


    """
    return _matchSpan(annotator1, annotator2, doc, _overlap)

def matchClassOverlapSpan(annotator1, annotator2, doc):
    """ Compares the annotations of two annotators over a document.
    Any overlapping span matches marked as the same annotation type are considered a hit.
    Returns a dictionary with keys all annotation types applicable to the document's project,
    and values tuples of size 3 - hits (number of spans annotated  by both annotators),
    the number of false positive annoations of annotator1, the number of false
    positive annotations of annotator2.

    Keyword arguments:
    annotator1 -- An Annotator object represenging the first annotator.
    annotator2 -- An Annotator object represenging the second annotator.
    doc -- Document oject prepresenting the text annotated by both annotators.

    """
    return _matchClass(annotator1, annotator2, doc, _overlap)

def matchClassExactSpan(annotator1, annotator2, doc):
    """ Compares the annotations of two annotators over a document.
    Only exact span matches marked as the same annotation type are considered a hit.
    Returns a dictionary with keys all annotation types applicable to the document's project,
    and values tuples of size 3 - the hits (number of spans annotated  by both annotators),
    the number of false positive annoations of annotator1, the number of false
    positive annotations of annotator2.

    Keyword arguments:
    annotator1 -- An Annotator object represenging the first annotator.
    annotator2 -- An Annotator object represenging the second annotator.
    doc -- Document oject prepresenting the text annotated by both annotators.


    """
    return _matchClass(annotator1, annotator2, doc, lambda x,y:x==y)

class Stats:
    def __init__(self,hits,misses1,misses2):
        self.hits=hits
        self.misses1=misses1
        self.misses2=misses2

    def matches(self): return self.hits*2.0
    def nonMatches(self): return self.misses1+self.misses2
    def iaaPercent(self):
        if self.matches()==0 and self.nonMatches()==0:
            return 0
        return round(self.matches()/(self.matches()+self.nonMatches())*100,2)
    def truePositive(self): return self.hits
    def falsePositive(self): return self.misses2
    def falseNegative(self):return self.misses1
    def precision(self):
        if not (self.truePositive()+self.falsePositive()): return 0
        return round(100.0*self.truePositive()/(self.truePositive()+self.falsePositive()),2)
    def recall(self):
        if not (self.truePositive()+self.falseNegative()): return 0
        return round(100.0*self.truePositive()/(self.truePositive()+self.falseNegative()),2)
    def fscore(self):
        if (self.precision()+self.recall())==0: return 0
        return round(2.0*(self.precision()*self.recall())/(self.precision()+self.recall()),2)

    def __add__(self, other):
        self.hits+=other.hits
        self.misses1+=other.misses1
        self.misses2+=other.misses2

class IaaStats:
    keys=['exactSpan','overlapSpan','classExactSpan','classOverlapSpan']
    class DocStats:
        def __init__(self,doc,**keywords):
            self.doc=doc
            #tuple of 3 values
            self.exactSpan=keywords['exactSpan']
            self.overlapSpan=keywords['overlapSpan']
            #dict - annotation type to triples
            self.classExactSpan=keywords['classExactSpan']
            self.classOverlapSpan=keywords['classOverlapSpan']
      
    def __init__(self,annotator1,annotator2,annotationTypes):
        self.annotator1=annotator1
        self.annotator2=annotator2
        self.annotationTypes=annotationTypes
        self.docStats=[]
        #triples
        self.exactSpan=Stats(0,0,0)
        self.overlapSpan=Stats(0,0,0)
        self.classExactSpan={}
        self.classOverlapSpan={}
        #dict - annotation type to triples
        for at in self.annotationTypes:
            self.classExactSpan[at]=Stats(0,0,0)
            self.classOverlapSpan[at]=Stats(0,0,0)


    def add(self,docStats):
        self.docStats.append(docStats)
        self.exactSpan+docStats.exactSpan
        self.overlapSpan+docStats.overlapSpan
        for at in self.annotationTypes:
            self.classExactSpan[at]+docStats.classExactSpan[at]
            self.classOverlapSpan[at]+docStats.classOverlapSpan[at]

def iaa(annotator1,annotator2, p):
    annotationTypes=map(lambda x: x.type,AnnotationType.objects.filter(project=p))
    docs=annotator1.documents.filter(project=p)
    iaaStats=IaaStats(annotator1,annotator2,annotationTypes)
    for doc in docs:
        docStats=IaaStats.DocStats(doc,exactSpan=matchExactSpan(annotator1, annotator2, doc),
                                   overlapSpan=matchOverlapSpan(annotator1, annotator2, doc),
                                   classExactSpan=matchClassExactSpan(annotator1, annotator2, doc),
                                   classOverlapSpan=matchClassOverlapSpan(annotator1, annotator2, doc))
        iaaStats.add(docStats)
    return iaaStats   








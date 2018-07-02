def overlap(tuple1, tuple2):
    for i in range(tuple1[0],tuple1[1]):
        if i in range(tuple2[0],tuple2[1]):
            return True
    return False

def findIndices(txt, word):
    result=[]
    begin_index=txt.find(word)
    while begin_index>-1:
        result.append((begin_index, len(word)+begin_index))
        begin_index=txt.find(word,len(word)+begin_index)
    return result

def htmlFormat(txt, annotations):
    indexTuples=map(lambda x: (x.begin_index, x.end_index), annotations)
    annotations=sorted(annotations, cmp=lambda x,y: cmp (y.begin_index, x.begin_index))
    eSpan='</a>'
    counter=-1
    for k in annotations:
       if (counter>0 and k.end_index>counter):
           continue
       cssClass= 'category%s'%k.annotation_type.id
       bSpan='<a class="%s" id="annotation_%s">'%(cssClass, k.id)
       txt='%s%s%s%s%s'%(txt[0:k.begin_index],bSpan,
                         txt[k.begin_index:k.end_index],
                         eSpan,txt[k.end_index:])
       counter=k.begin_index
    return txt
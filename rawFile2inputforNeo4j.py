import csv

def a_sub_b(a, b):
    return [x for x in a if x not in b]

def vtermTonterm(term):
    tokens = term.split(':')
    tokens = tokens[:len(tokens)-2]
    refinedTerm = ""
    for token in tokens:
        refinedTerm = refinedTerm + token + ":"
    refinedTerm = refinedTerm[0:-1]
    return refinedTerm

def getTermlist(str):
    strlist = str.split(":")
    termlist = list()
    for i in range(len(strlist)):
        if i % 2 == 0:
            termlist.append(strlist[i])
    return termlist

def containOrNot(vterm, ntermlist):
    refinedTerm = vtermTonterm(vterm)
    vterms = getTermlist(refinedTerm)
    nterms = list()
    for nterm in ntermlist:
        for nword in getTermlist(nterm):
            nterms.append(nword)
    vterms = list(set(vterms))
    nterms = list(set(nterms))
    if len(a_sub_b(vterms, nterms)) != 0:
        return "NotSame"

def getOptimalset(vnpairs):
    answer = list()
    for pair in vnpairs:
        vwords = getTermlist(vtermTonterm(pair[0]))
        nterms = pair[1]

        for i in range(len(nterms)):
            for j in range(i+1, len(nterms)):
                if vwords == getTermlist(nterms[i])+getTermlist(nterms[j]):
                    answer.append([pair[0], [nterms[i], nterms[j]]])
    return answer

rf = open("./IRA.csv", 'r')
rdr = csv.reader(rf)
wf = open("./output.csv", 'w')
wtr = csv.writer(wf, lineterminator='\n')

nterms = list()
vterms = list()

next(rdr)
preSentence = "initial"
# wtr.writerow(["ID", "SENTENCE", "ORG_NTERMS", "ORG_VTERMS", "REDUCED_PAIRS", "OPTIMAL SET", "RDF_TRIPLES"])
wtr.writerow(["ID", "DATE", "SENTENCE", "SUBJ", "PRED", "OBJ"])

for cur_row in rdr:
    sentence = cur_row[6]
    term = cur_row[1]
    pos = cur_row[3]
    id = cur_row[5]
    date = cur_row[2]

    if preSentence == "initial":
        if pos == 'NOUN':
            nterms.append(term)
        if pos == 'VERB':
            if len(term.split(":")) >= 5:
                vterms.append(term)

    if sentence == preSentence:
        if pos == 'NOUN':
            nterms.append(term)
        if pos == 'VERB':
            if len(term.split(":")) >= 5:
                vterms.append(term)
    else:
        copy_vterms = vterms.copy()
        vnpairs = list()

        for vterm in copy_vterms:
            copy_nterms = nterms.copy()
            vwords = getTermlist(vterm)
            for nterm in nterms:
                nwords = getTermlist(nterm)
                if vwords == a_sub_b(vwords, nwords): #nterm이 vterm에 포함되어 있는지? 만약 불포함되어있다면, nterm 집합에서 삭제하여 더 이상 다루지 않음
                    if nterm in copy_nterms:
                        copy_nterms.remove(nterm)
            vnpairs.append([vterm, copy_nterms])
        copy_vnpairs = vnpairs.copy()

        for pair in vnpairs:
            if containOrNot(pair[0], pair[1]) == "NotSame":
                copy_vnpairs.remove(pair)

        optimalSets = getOptimalset(copy_vnpairs)
        triples = list()

        for optset in optimalSets:
            _subject = optset[1][0]
            _object = optset[1][1]
            _predicate = getTermlist(optset[0])[len(getTermlist(optset[0]))-1]
            triples.append([_subject, _predicate, _object])

        if preSentence != "initial":
            # wtr.writerow([int(id)-1, preSentence, nterms, vterms, copy_vnpairs, optimalSets, triples])
            if len(triples) != 0:
                for triple in triples:
                    sub = triple[0]
                    pred = triple[1]
                    obj = triple[2]
                    wtr.writerow([int(id)-1, date, preSentence, sub, pred, obj])

        nterms = list()
        vterms = list()

        if pos == 'NOUN':
            nterms.append(term)
        if pos == 'VERB':
            if len(term.split(":")) >= 5:
                vterms.append(term)

    preSentence = sentence  # 한 문장에 대한 처리가 마무리 되면, 초기화를 시켜줌


    # 이하는 항상 반복되는 명령들



#verb tuple에 대해,
#verb 제외한 terms를 만족하는. 두개의 최적 쌍을 찾음.



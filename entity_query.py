from neo4j import GraphDatabase

def getQueryResult(keyword):
    uri = "bolt://localhost:7687"
    driver = GraphDatabase.driver(uri, auth=None, encrypted=False)
    q_results = list()

    print("Input keywords : {key}".format(key=keyword))

    inputkeywords = list()
    num_keywords = 0
    if keyword.find('"') == -1:
        inputkeywords = keyword.split()
        num_keywords = len(inputkeywords)
    else: #not implemented yet
        exit()
    def exec_query(tx, args):
        for record in tx.run(gen_query(args)):
            q_results.append(str(record["rels"]))

    def gen_query(args):
        subj_statement = ""
        obj_statement = ""
        for keyword in args:
            # subj_statement = subj_statement + "(s.name CONTAINS toLower('" + keyword + "') or s.name CONTAINS '" + keyword + "') and "
            subj_statement = subj_statement + "(s.name =~ '(?i).*" + keyword + ".*') and "
        for keyword in args:
            # obj_statement = obj_statement + "(o.name CONTAINS toLower('" + keyword + "') or o.name CONTAINS '" + keyword + "') and "
            obj_statement = obj_statement + "(o.name =~ '(?i).*" + keyword + ".*') and "
        query_statement = "MATCH t=(s)-[p]->(o) WHERE " + subj_statement[:-5] + " or " + obj_statement[:-5] + " RETURN t as nodes, p as rels"
        print("Executed query: {}".format(query_statement))
        return query_statement

    with driver.session() as session:
        session.read_transaction(exec_query, inputkeywords)

    driver.close()

    results = list()
    no = 1

    for line in q_results:
        if len(line) == 0:
            break

        sentence = line[line.find("'sentence': ")+len("'sentence': ")+1:line.find(", 'date':")-1]
        date = line[line.find("'date': ")+len("'date': ")+1:line.find(", 'sentid':")-1]
        sent_id = line[line.find("'sentid': ")+len("'sentid': ")+1:line.find(" 'uri': 'https://nist.gov/relation")-2]
        pred_id_start_pos = line.find("<Relationship id=") + len("<Relationship id=")
        pred_id_end_pos = line.find(" nodes")

        pred_id = line[pred_id_start_pos:pred_id_end_pos]

        sub_start_pos = line.find("labels=frozenset({'") + len("labels=frozenset({'")
        sub_end_pos = line.find("}) ")
        sub_id_start_pos = line.find("<Node id=") + len("<Node id=")
        sub_id = line[sub_id_start_pos:sub_start_pos - len("labels=frozenset({'")]
        sub = line[sub_start_pos:sub_end_pos-1]
        line = line[sub_end_pos+1:]

        obj_start_pos = line.find("labels=frozenset({'") + len("labels=frozenset({'")
        obj_end_pos = line.find("}) properties=")
        obj_id_start_pos = line.find("<Node id=") + len("<Node id=")
        obj_id = line[obj_id_start_pos:obj_start_pos - len("labels=frozenset({'")]
        obj = line[obj_start_pos:obj_end_pos-1]
        line = line[obj_end_pos+1:]

        pred_start_pos = line.find("type='") + len("type='")
        pred_end_pos = line.find("' properties")
        pred = line[pred_start_pos:pred_end_pos]
        # Exact Match_START
        sub_terms = sub.split(":")
        obj_terms = obj.split(":")

        _flag = True
        # Re-Search Entities in Results
        if len(inputkeywords) == 1 and ":" in inputkeywords[0]:
            if inputkeywords[0] != sub and inputkeywords[0] != obj:
                _flag = False
        else: #Initial Search using Input form
            for i in range(num_keywords):
                if inputkeywords[i].casefold() not in (terms.casefold() for terms in sub_terms) \
                        and inputkeywords[i].casefold() not in (terms.casefold() for terms in obj_terms):
                    _flag = False

        if _flag == False:
            continue
        # Exact Match_END
        results.append([no, sub, pred, obj, sentence])

        no = no + 1

    return results


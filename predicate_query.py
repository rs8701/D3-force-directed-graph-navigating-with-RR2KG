from neo4j import GraphDatabase

def getQueryResult(keyword):
    uri = "bolt://localhost:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "1234"), encrypted=False)
    q_results = list()


    inputkeyword = keyword

    def samplequery(tx):
        for record in tx.run("MATCH t=(s)-[p:"+inputkeyword+"]->(o) RETURN t as nodes, p as rels"):
            q_results.append(str(record["rels"]))


    with driver.session() as session:
        session.read_transaction(samplequery)

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

        results.append([no, sub, pred, obj, sentence])

        # results.append([sub,pred,obj])
        # return sub, pred, obj

        no = no + 1

    return results


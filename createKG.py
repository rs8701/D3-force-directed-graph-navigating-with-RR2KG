import csv
import re
import sys

from py2neo import Graph, Node, Relationship

def main(string):
    class Database:
        connection = None
        def __init__(self):
            # self.connection = Graph("bolt://localhost:7687", auth=None, encrypted=False)
            self.connection = Graph("bolt://localhost:7687", auth=("neo4j", "1234"), encrypted=False)
            print("Neo4j is connected")
        def conn(self):
            if self.connection is not None:
                return self.connection
            self.connection = self.__init__()
            return self.connection

    dbs = Database()
    # g = Graph("bolt://localhost:7687", auth=None, encrypted=False)
    g = Graph("bolt://localhost:7687", auth=("neo4j", "1234"), encrypted=False)

    inputName = string
    input_file = csv.DictReader(open(inputName, encoding='UTF-8'))
    progress = 0
    for row in input_file:
        row = dict(row)
        sub = str(row['SUBJ'])
        obj = str(row['OBJ'])
        pred = str(row['PRED'])

        subjURI = ""
        for element in sub.split(":"):
            subjURI += element
        objURI = ""
        for element in obj.split(":"):
            objURI += element

        _subjURI = re.sub('[^0-9a-zA-Z]', '', subjURI)
        _objURI = re.sub('[^0-9a-zA-Z]', '', objURI)

        suburi = 'https://nist.gov/entity#'+_subjURI.lower()
        objuri = 'https://nist.gov/entity#'+_objURI.lower()
        preduri = 'https://nist.gov/relation#' + row['PRED']
        sent = row['SENTENCE']
        sentid = row['ID']
        date = row['DATE']
        pattern1 = re.compile('[a-z]')
        m = pattern1.match(pred)

        if m == None :
            continue

        # tx = g.begin()
        # sub = Node(className, name=subtext, sentence=sent, document=doc)
        # tx.create(sub)
        # tx.commit()


        tx = g.begin()

        _subject = g.nodes.match(uri=suburi).first()
        _object = g.nodes.match(uri=objuri).first()
        # _predicate = g.relationships.match(uri=preduri).first()

        if _subject is None and _object is None: #NO SUBJECT, NO OBJECT
            _subject = Node(sub, name=sub, uri=suburi)
            _object = Node(obj, name=obj, uri=objuri)
            tx.create(_subject)
            tx.create(_object)
            _predicate = Relationship(_subject, pred, _object, uri=preduri, sentid=sentid, sentence=sent, date=date)
            tx.create(_predicate)


        elif _subject is None and _object is not None: #NO SUBJECT, YES OBJECT
            _subject = Node(sub, name=sub, uri=suburi)
            tx.create(_subject)
            _predicate = Relationship(_subject, pred, _object, uri=preduri, sentid=sentid, sentence=sent, date=date)
            tx.create(_predicate)


        elif _subject is not None and _object is None: #YES SUBJECT, NO OBJECT
                _object = Node(obj, name=obj, uri=objuri)
                tx.create(_object)
                _predicate = Relationship(_subject, pred, _object, uri=preduri, sentid=sentid, sentence=sent, date=date)
                tx.create(_predicate)

        else: #YES SUBJECT, YES OBJECT
                _predicate = Relationship(_subject, pred, _object, uri=preduri, sentid=sentid, sentence=sent, date=date)
                tx.create(_predicate)


            # _predicate = g.relationships.match(sentence=sent).first()
            # if _predicate is None:
            #     print("HERE")
            #     print(row)
            #     _predicate = Relationship(_subject, pred, _object, uri=preduri, document=doc, sentence=sent)
            #     tx.create(_predicate)
            # else:
            #     continue

        tx.commit()

        if progress % 1000 == 0:
            print("Progress = {}".format(progress))
        progress = progress + 1

    print("Finished")

# def createNode(tx, className, name, sent, doc):
#     result = tx.run("CREATE (n:" + className + " { name:"+ name +", sent:"+sent+", doc:"+doc+"})")
#     return result.single()[0]

if __name__ == "__main__":
    main(sys.argv[1])
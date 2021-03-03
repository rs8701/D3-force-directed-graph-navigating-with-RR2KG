from neo4j import GraphDatabase
import json
import os


def draw(keyword):

    if os.path.isfile('trace.json'):
        os.remove('trace.json')
    if os.path.isfile('graph.json'):
        os.remove('graph.json')
    uri = "bolt://localhost:7687"

    driver = GraphDatabase.driver(uri, auth=("neo4j", "1234"), encrypted=False)
    q_results = list()
    print("1번째 그래프 탐색, 선택된 노드 키워드: {}".format(keyword))
    def entquery(tx):
        for record in tx.run("MATCH t=(s)-[p]->(o) WHERE s.name =~ '(?i)" + keyword + "' \
                             or o.name =~ '(?i)" + keyword + "' RETURN t as nodes, p as rels Limit 10"):
            q_results.append(str(record["rels"]))

    with driver.session() as session:
        session.read_transaction(entquery)
    driver.close()

    node_ids = dict()
    nodes = list()
    links_temp = list()
    links = list()
    links_st = set()
    uid = 0
    for line in q_results:
        if len(line) == 0:
            break
        sentence = line[line.find("'sentence': ") + len("'sentence': ") + 1:line.find(", 'date':") - 1]
        if line.find(", 'date':") == -1:
            sentence = line[line.find("'sentence': ") + len("'sentence': ") + 1:line.find(", 'sentid':") - 1]
        date = line[line.find("'date': ") + len("'date': ") + 1:line.find(", 'sentid':") - 1]
        sent_id = line[
                  line.find("'sentid': ") + len("'sentid': ") + 1:line.find(" 'uri': 'https://nist.gov/relation") - 2]
        pred_id_start_pos = line.find("<Relationship id=") + len("<Relationship id=")
        pred_id_end_pos = line.find(" nodes")

        pred_id = line[pred_id_start_pos:pred_id_end_pos]

        sub_start_pos = line.find("labels=frozenset({'") + len("labels=frozenset({'")
        sub_end_pos = line.find("}) ")
        sub_id_start_pos = line.find("<Node id=") + len("<Node id=")
        sub_id = line[sub_id_start_pos:sub_start_pos - len("labels=frozenset({'")]
        sub = line[sub_start_pos:sub_end_pos - 1]
        line = line[sub_end_pos + 1:]

        obj_start_pos = line.find("labels=frozenset({'") + len("labels=frozenset({'")
        obj_end_pos = line.find("}) properties=")
        obj_id_start_pos = line.find("<Node id=") + len("<Node id=")
        obj_id = line[obj_id_start_pos:obj_start_pos - len("labels=frozenset({'")]
        obj = line[obj_start_pos:obj_end_pos - 1]
        line = line[obj_end_pos + 1:]

        pred_start_pos = line.find("type='") + len("type='")
        pred_end_pos = line.find("' properties")
        pred = line[pred_start_pos:pred_end_pos]

        if str(sub) in node_ids:
            pass
        else:
            node_ids[str(sub)] = uid
            uid = uid + 1
        if str(obj) in node_ids:
            pass
        else:
            node_ids[str(obj)] = uid
            uid = uid + 1

        links.append({'source': node_ids[sub], 'target': node_ids[obj], 'type': pred, 'sent': sentence})
    #     if (node_ids[sub], node_ids[obj]) not in links_st:
    #         links_st.add((node_ids[sub], node_ids[obj]))
    #         links_temp.append([node_ids[sub], node_ids[obj], [pred], [sentence]])
    #     else:
    #         for link in links_temp:
    #             if link[0] == node_ids[sub] and link[1] == node_ids[obj]:
    #                 link[2].append(pred)
    #                 link[3].append(sentence)
    #
    # print("실험중")
    # print(links)
    # print(links_temp)
    for name, id in node_ids.items():
        nodes.append({'id': id, 'name': name})

    # graph_file = 'graph'+str(socket.gethostname())+'.json'
    # trace_file = 'trace'+str(socket.gethostname())+'.json'
    with open('graph.json', 'w') as f:
        json.dump({'nodes': nodes, 'links': links}, f, indent=4,)
    with open('trace.json', 'w') as f:
        json.dump({'nodes': nodes, 'links': links}, f, indent=4,)


def new_draw(keyword, limit, filter):

    history_node_ids = dict() #previous node/id dictionary
    cur_node_ids = dict() #current node/id dictionary
    cur_nodes = list() #current node/id list
    cur_links = list() #current link list


    with open('trace.json') as json_file:
        data = json.load(json_file)
        for line in data['nodes']:
            history_node_ids[line['name']] = line['id']
        history_nodes = data['nodes'].copy()
        history_links = data['links'].copy()

    print("연속된 그래프 탐색, 선택된 노드 키워드 (id): {} ({})".format(keyword, history_node_ids[keyword]))

    uri = "bolt://localhost:7687"
    starting_uid = len(history_node_ids)
    driver = GraphDatabase.driver(uri, auth=("neo4j", "1234"), encrypted=False)
    q_results = list()
    inputkeyword = keyword
    # if filter == "":
    def entquery(tx):
        for record in tx.run("MATCH t=(s)-[p]->(o) WHERE s.name =~ '(?i)" + inputkeyword + "' \
                             or o.name =~ '(?i)" + inputkeyword + "' RETURN t as nodes, p as rels LIMIT " + limit):
            q_results.append(str(record["rels"]))
    # else:
    #     def entquery(tx):
    #         for record in tx.run("MATCH t=(s)-[p]->(o) WHERE (s.name =~ '(?i)" + inputkeyword + "' \
    #                              or o.name =~ '(?i)" + inputkeyword + "') \
    #                              and s.name CONTAINS '" + filter + "' or o.name CONTAINS '" + filter + "' RETURN t as nodes, p as rels Limit " + limit):
    #             str_path = str(record["rels"])+"\n"
    #             output_f.write(str_path)
    with driver.session() as session:
        session.read_transaction(entquery)
    driver.close()

    for line in q_results:
        if len(line) == 0:
            break
        sentence = line[line.find("'sentence': ") + len("'sentence': ") + 1:line.find(", 'date':") - 1]

        if line.find(", 'date':") == -1:
            sentence = line[line.find("'sentence': ") + len("'sentence': ") + 1:line.find(", 'sentid':") - 1]

        date = line[line.find("'date': ") + len("'date': ") + 1:line.find(", 'sentid':") - 1]
        sent_id = line[line.find("'sentid': ") + len("'sentid': ") + 1:line.find(" 'uri': 'https://nist.gov/relation") - 2]
        pred_id_start_pos = line.find("<Relationship id=") + len("<Relationship id=")
        pred_id_end_pos = line.find(" nodes")
        pred_id = line[pred_id_start_pos:pred_id_end_pos]
        sub_start_pos = line.find("labels=frozenset({'") + len("labels=frozenset({'")
        sub_end_pos = line.find("}) ")
        sub_id_start_pos = line.find("<Node id=") + len("<Node id=")
        sub_id = line[sub_id_start_pos:sub_start_pos - len("labels=frozenset({'")]
        sub = line[sub_start_pos:sub_end_pos - 1]
        line = line[sub_end_pos + 1:]
        obj_start_pos = line.find("labels=frozenset({'") + len("labels=frozenset({'")
        obj_end_pos = line.find("}) properties=")
        obj_id_start_pos = line.find("<Node id=") + len("<Node id=")
        obj_id = line[obj_id_start_pos:obj_start_pos - len("labels=frozenset({'")]
        obj = line[obj_start_pos:obj_end_pos - 1]
        line = line[obj_end_pos + 1:]
        pred_start_pos = line.find("type='") + len("type='")
        pred_end_pos = line.find("' properties")
        pred = line[pred_start_pos:pred_end_pos]

        if str(sub) in history_node_ids:
            pass
        else:
            cur_node_ids[str(sub)] = starting_uid #새로이 생성된 sub에 대해 id발급
            history_node_ids[str(sub)] = starting_uid #trace 노드 정보에도 id보존 #이게 현재 필요한건지 고민해보자.
            starting_uid = starting_uid + 1
        if str(obj) in history_node_ids:
            pass
        else:
            cur_node_ids[str(obj)] = starting_uid
            history_node_ids[str(obj)] = starting_uid
            starting_uid = starting_uid + 1
        #신규생성되는 links
        # links.append({'source': node_ids[sub], 'target': node_ids[obj], 'type': pred, 'sent': sentence})
        #신규 생성 link; 여기서 cur_node_ids가 아닌 node_ids를 사용하는 이유는, 클릭된 노드는 신규 생성이 아닌, 기존 노드이기때문
        cur_links.append(
            {'source': history_node_ids[sub], 'target': history_node_ids[obj], 'type': pred, 'sent': sentence})
        # if {'source': history_node_ids[sub], 'target': history_node_ids[obj], 'type': pred, 'sent': sentence} not in history_links:
        #     cur_links.append(
        #         {'source': history_node_ids[sub], 'target': history_node_ids[obj], 'type': pred, 'sent': sentence})

    # dup_links = dict()
    # for i in range(0, len(cur_links)):
    #     for j in range(i+1, len(cur_links)):
    #         if cur_links[i]['source'] == cur_links[j]['source'] and cur_links[i]['target'] == cur_links[j]['target']:
    #             dup_links[(cur_links[i]['source'], cur_links[i]['target'])] = cur_links[j]['type']
    #
    #             , cur_links[j]['sent']])
    #
    # print(dup_links)
    # 발급된 노드의 name/id 정보를 기반으로, 현 질의 처리를 통해 생성된 node 정보 수집
    for name, id in cur_node_ids.items():
        cur_nodes.append({'id': id, 'name': name})

    print("전 쿼리에서 보존된 nodes / edges")
    print(history_nodes)
    print(history_links)
    print("이번 쿼리에서 생성된 nodes / edges")
    print(cur_nodes)

    for link in cur_links:
        print("'source': {}, 'target': {}, 'type': {}".format(link['source'], link['target'], link['type']))

    filtered_nodes = list()
    filtered_links = list()
    filtered_nodes_ids = list()

    if filter == "":
        # 보존 시작
        for node in cur_nodes:
            history_nodes.append(node)
        for link in cur_links:
            history_links.append(link)
        with open('trace.json', 'w') as f:
            json.dump({'nodes': history_nodes, 'links': history_links}, f, indent=4, )
        with open('graph.json', 'w') as f:
            json.dump({'nodes': cur_nodes, 'links': cur_links}, f, indent=4, )
    else:

        for node in cur_nodes:
            if filter in node['name']:
                filtered_nodes.append(node)
        for fnode in filtered_nodes:
            filtered_nodes_ids.append(fnode['id'])
        for link in cur_links:
            if link['source'] in filtered_nodes_ids or link['target'] in filtered_nodes_ids:
                filtered_links.append(link)

        for node in filtered_nodes:
            history_nodes.append(node)
        for link in filtered_links:
            history_links.append(link)
        with open('trace.json', 'w') as f:
            json.dump({'nodes': history_nodes, 'links': history_links}, f, indent=4, )
        with open('graph.json', 'w') as f:
            json.dump({'nodes': filtered_nodes, 'links': filtered_links}, f, indent=4, )


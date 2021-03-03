from flask import Flask, request, render_template, send_file
import io
import entity_query,predicate_query, draw_graph
import webbrowser

app = Flask(__name__)
@app.route('/')
def index():
    return render_template(("index.html"))

@app.route('/method', methods=['POST'])

def method():
    ikeyword = request.form["i_keyword"]
    results = entity_query.getQueryResult(ikeyword)
    return render_template("output.html", spo=results)

@app.route('/entsearch/<entity>', methods=['GET'])
def entsearch(entity)->'html':
    results = entity_query.getQueryResult(entity)
    return render_template("output.html", spo=results)

@app.route('/predsearch/<pred>', methods=['GET'])
def predsearch(pred)->'html':
    results = predicate_query.getQueryResult(pred)
    return render_template("output.html", spo=results)

@app.route('/graphvis/<item>', methods=['GET'])
def drawgraph(item):
    draw_graph.draw(item)
    return render_template("graph.html")

@app.route('/graph/<filename>', methods = ['GET'])
def serv_file(filename):
    with open(filename, 'r') as f:
        return f.read()
    #graph.html파일 내에서 d3.json("/graph/graph.json", function (error, graph)를 처리할때 위 단락코드를 실행해서 json파일을 가져오게 된다.

@app.route('/newgraph/<filename>', methods = ['GET'])
def get_json(filename):
    filter = filename[filename.find("**")+2:]
    print(filter)
    limiter = filename[filename.find("::")+2:filename.find("**")]
    entity = filename[:filename.find("::")]
    draw_graph.new_draw(entity, limiter, filter)
    with open('graph.json', 'r') as f:
        return f.read()
    #도전

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    # app.run(debug=True)

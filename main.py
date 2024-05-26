import json
import random
import os
import networkx as nx
from io import BytesIO
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, request, render_template, redirect, url_for, session
import graph as g
app = Flask(__name__)

app.secret_key = os.urandom(24)


def getSessionGraph():
    return nx.adjacency_graph(session['graph'])


def setSessionGraph(graph):
    session['graph'] = nx.adjacency_data(graph)


def updateSessionGraph(update = lambda _: None, **kw):
    graph = getSessionGraph()
    update(graph,**kw)
    setSessionGraph(graph)


@app.before_request
def before_request():
    # store empty graph
    if 'graph' not in session:
        session['graph'] = nx.adjacency_data(nx.Graph())


@app.route("/")
def graphInterfaceView():

    graph = getSessionGraph()

    # draw graph
    nx.draw_networkx(graph,font_color='white', pos=nx.circular_layout(graph))

    # base64 encode graph image 
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    plt.close()

    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue()).decode('ascii')


    return (
        render_template(
        'index.html',
        image_base64 = figdata_png,
        matrix = str(nx.to_numpy_array(graph)).replace('.',',').replace('\n',','),
        graph = graph,
        data = json.dumps(nx.node_link_data(graph))
    ))

# add and remove node
@app.route("/addnode")
def addnode():

    updateSessionGraph(g.add)

    return redirect(url_for('graphInterfaceView'))

@app.route("/removenode")
def removenode():

    updateSessionGraph(g.remove, node=int(request.args.get('label')))

    return redirect(url_for('graphInterfaceView'))

# add and remove edge 
@app.route("/addedge")
def addedge():
    updateSessionGraph(lambda graph: graph.add_edge(request.args.get('label1'),request.args.get('label2')))

    return redirect(url_for('graphInterfaceView'))

@app.route("/toggleedge")
def toggleedge():
    updateSessionGraph(g.toggle,edge=[int(n) for n in request.args.get('label').split('_')])

    return redirect(url_for('graphInterfaceView'))

# complement graph
@app.route("/complement")
def complementgraph():

    graph = getSessionGraph()
    setSessionGraph(nx.complement(graph))

    return redirect(url_for('graphInterfaceView'))

# complement edges for single node
@app.route("/complementnode")
def complementnode():
    updateSessionGraph(g.complement,node=int(request.args.get('label')))

    return redirect(url_for('graphInterfaceView'))

# clear edges 
@app.route("/clearedges")
def clearedges():

    updateSessionGraph(lambda graph: graph.remove_edges_from(graph.edges()))

    return redirect(url_for('graphInterfaceView'))

# clear graph
@app.route("/clear")
def cleargraph():

    updateSessionGraph(lambda graph: graph.clear())

    return redirect(url_for('graphInterfaceView'))

@app.route("/dijkstra")
def dijkstra_algorithm():
    try:
        graph = getSessionGraph()
        s = int(request.args.get('source'))
        t = int(request.args.get('target'))
        dijkstra_path = nx.dijkstra_path(G=graph, source=s, target=t)
        print(dijkstra_path)
        path_length = nx.dijkstra_path_length(G=graph, source=s, target=t)
        # draw graph
        nx.draw_networkx(graph, font_color='white', pos=nx.circular_layout(graph))

        path_edges = list(zip(dijkstra_path, dijkstra_path[1:]))
        nx.draw_networkx_nodes(G=graph, pos=nx.circular_layout(graph), nodelist=dijkstra_path, node_color='black')
        nx.draw_networkx_edges(G=graph, pos=nx.circular_layout(graph), edgelist=path_edges, edge_color='r', width=2.5)

        # base64 encode graph image
        figfile = BytesIO()
        plt.savefig(figfile, format='png')
        plt.close()

        figfile.seek(0)
        figdata_png = base64.b64encode(figfile.getvalue()).decode('ascii')

        dijkstra_path_response = ""
        for node in dijkstra_path[:len(dijkstra_path)-1]:
            dijkstra_path_response += str(node) + " => "
        dijkstra_path_response += str(dijkstra_path[len(dijkstra_path)-1])

        return (
            render_template(
                'index.html',
                image_base64=figdata_png,
                matrix=str(nx.to_numpy_array(graph)).replace('.', ',').replace('\n', ','),
                graph=graph,
                dijkstra_path=json.dumps(dijkstra_path_response)
            ))
    except:
        return redirect(url_for('graphInterfaceView'))


if __name__ == '__main__':
  app.run(host='0.0.0.0', port='5000')

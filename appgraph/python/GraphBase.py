#Need to have pydot installed on the system
import pygraphviz as pgv
import os
import sys
from PyQt4 import QtGui as qtg
from PyQt4 import QtCore as qtc
import pickle
import copy
import time 
#http://kmkeen.com/python-trees/2009-05-30-11-05-40-138.html
from collections import deque
import operator

#BUGS:
#Can't Wander without first updating

class Node(object):
    def __init__(self, name):
        self.name = str(name)
        self.num_connections = 0
        self.connected_to = []

    def addConnection(self, connector):
        self.num_connections = self.num_connections + 1
        self.connected_to.append(connector)

    def removeConnection(self, connector):
       if connector in self.connected_to:
            del self.connected_to[self.connected_to.index(connector)]
       else:
            print `connector` + " is not connected to node " + `self`

    def Details(self):
        return str({"NodeName": self.name,
                    "ConnectedTo": self.connected_to,
                    "NumConnections": self.num_connections})
 
    def __eq__(self, other):
        #Want to be able to compare equality between string and node name
        if type(self) == type(other):
            return (self.name == other.name)
        else:
            return self.name == str(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return str(self.name)

    def __str__(self):
        return self.__repr__()

    def __len__(self):
        return 1

class Edge(object):
    def __init__(self, source, dest, weight=None, function=operator.add, is_directed=False):
        self.directed = is_directed
        self.color = None
        self.weight_function = function
        if weight == None or weight == "":
            self.nodes = [Node(source), Node(dest)]
            self.weight = None
        else:
            try:
               [float(x) for x in weight]
            except ValueError:
               print "Must be convertable to float!"
            self.nodes = [Node(source), Node(dest)]
            self.weight = map(float, weight)

    def __eq__(self, other):
        if len(self.nodes) == 2:
            return len(self.nodes) == len([True for i in self.nodes if i in other.nodes])
        else:
            return len(self.nodes[:-1]) == len([True for i in self.nodes[:-1] if i in other.nodes[:-1]]) and self.nodes[-1] == other.nodes[-1]
   
    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        if self.directed:
            return "[" + str(self.nodes[0]) + " -> " + str(self.nodes[1])+"]"
        else:
            return str(self.nodes)

    def __str__(self):
        return str(self.nodes)

    def __len__(self):
        return len(self.nodes)

    def setFunction(self, func):
        try:
            self.weight_function = func
        except ValueError:
            "Function definition requires either 1 argument to be applied between each or len(weights)-1 arguments"

    def getWeight(self):
        print self.weight
        print self.weight_function
        return reduce(self.weight_function, self.weight)

class Graph(object):
    def __init__(self, edges=None, nodes=None, is_directed=False, is_strict=False):
        self.nodes = []
        self.edges = []
        self.is_directed = is_directed
        self.is_strict = is_strict
        if nodes != None:
            [self.addNode(x) for x in nodes]
        if edges != None:
            [self.addEdge(x) for x in edges]

    def __str__(self):
        return str(self.__getstate__())

    def __getstate__(self):
        return {"nodes": self.nodes,
                "edges": self.edges,
                "is_directed": self.is_directed,
                "is_strict": self.is_strict}

    def __setstate__(self, state):
           self.nodes = state["nodes"]
           self.edges = state["edges"]
           self.is_directed = state["is_directed"]
           self.is_strict = state["is_strict"]  
            
    def clearAll(self):
        self.clearEdges()
        self.clearNodes()

    def clearEdges(self):
        del self.edges[:]

    def clearNodes(self):
        del self.nodes[:]

    def addEdge(self, source, dest, weight=None, function=operator.add, is_directed=False):
        if weight != None:
           self.edges.append(Edge(source, dest, weight=weight, function=function))
        else:
            self.edges.append(Edge(source, dest, function=function))
        self.addNode(source, connection=dest)
        self.addNode(dest, connection=source)

    def getEdges(self):
        return self.edges

    def addNode(self, node, connection=None):
        primary_node = Node(node)
        if primary_node not in self.nodes:
            self.nodes.append(primary_node)
        if connection is not None:
            connection_node = Node(connection)
            self.nodes[self.nodes.index(primary_node)].addConnection(connection_node)
            
    def getNodes(self):
        return self.nodes

    def plot(self, fname="graph.png"):
        _g = pgv.AGraph(directed=self.is_directed, strict=self.is_strict)
        for i in self.edges:
            _g.add_edge(i.nodes[0], i.nodes[1])
        _g.layout(prog="dot")
        _g.draw(fname)

class DjikstraWanderer(object):
    def __init__(self, graph, start, end):
        self.graph = copy.deepcopy(graph)
        self.unsolved = copy.deepcopy(self.graph.nodes)
        self.distances = {}
        self.available = []
        self.path = []
        self.start = start
        self.end = end
        for k in self.unsolved:
            #None is infinite distance
            self.distances[k] = None
            self.available.append(k)
        self.setDistance(start, 0, prev=start)
        self.removeAvailable(start)
        
    def removeAvailable(self, node):
        for n, existing_node in enumerate(self.available):
            if existing_node == node:
                return self.available.pop(n)
                
    def setDistance(self, node, distance, prev=None):
        for n, existing_node in enumerate(self.distances):
            if existing_node == node:
                self.distances[existing_node] = distance
                break
            
    def getDistance(self, node):
       for n, existing_node in enumerate(self.distances):
            if existing_node == node:
                return self.distances[existing_node]
  
    def minDistance(self):
        #TODO FIX THIS HACKERY
        min_val = 1000000
        min_node = 1000000
        for n in self.available:
            if self.getDistance(n) == 0 or self.getDistance(n) == None:
                continue
            elif self.getDistance(n) < min_val:
                min_val = self.getDistance(n)
                min_node = n
        return (min_node, min_val)
               
    def getConnected(self, node):
        for n, existing_node in enumerate(self.distances):
            if existing_node == node:
                return existing_node.connected_to

    def matchEdge(self, start, stop):
        for n, existing_edge in enumerate(self.graph.edges):
            if existing_edge.nodes[0] == start and existing_edge.nodes[1] == stop:
               return existing_edge.getWeight()

    def step(self, current):
        connected = self.getConnected(current)
        for c in connected:
            dist = self.matchEdge(current, c)
            if self.getDistance(c) == None or dist < self.getDistance(c):
                self.setDistance(c, dist, prev=current)
        
        [min_node, min_val] = self.minDistance()
        self.removeAvailable(min_node)
        return (min_node, min_val)
                    
    def run(self):
        at = self.start
        while True:
            [next, weight] = self.step(at)
            if self.matchEdge(at, next) == weight:
                self.path.append(at)
            at = next
            if next == self.end:
                self.path.append(at)
                print self.path
                break
        print "Djikstra complete"

class BruteWanderer(object):
    def __init__(self, graph, num):
        self.tree = {}
        self.graph = copy.deepcopy(graph)
        self.edges = copy.deepcopy(self.graph.edges)
        self.num = num
        self.walked = []
        for k in graph.nodes:
            self.tree[str(k)] = k.connected_to
        print "Wander Complete!"   

    def run(self):
        self.walk(self.graph.nodes[self.num])

    def walk(self, start, directed=False):
        if len(self.edges) == 0:
            print "Path found!"
            print "Path is :"
            print self.walked
            return None

        possibles = self.tree[str(start)]
        for x in possibles:
            e = Edge(start, x)
            if e in self.edges:
                self.walked.append(e)
                del self.edges[self.edges.index(e)]
                print self.walked
                return self.walk(x) 
 
class MainView(qtg.QWidget):
    def __init__(self):
        super(MainView, self).__init__()
        self.graph = Graph()
        self.graph_host = qtg.QLabel() 
        self.graph_pixmap = qtg.QPixmap(self.createGraph(self.graph)).scaledToHeight(self.height())
        self.table = qtg.QTableWidget()
        self.save_fname = "graph.pickle"
        self.op_boxes = []
        self.weight_boxes = []
        try:
            f = open(self.save_fname, "rb")
            self.graph = pickle.load(f)
            self.graph_pixmap = qtg.QPixmap(self.createGraph(self.graph))
            self.graph_host.setPixmap(self.graph_pixmap)
            #Empty list so that I can reuse the initTable function
            self.initTable([])
            self.fillTable()
            print "Loaded previous graph from " + self.save_fname
        except IOError:
            print "No previous graph found in " + `self.save_fname`
        self.initUI()
  
    def createGraph(self, graph): 
        fname = "graph.png" 
        graph.plot(fname)  
        return fname   

    def initGraph(self, widgets):
        widgets.append(self.graph_host)
 
    def fillTable(self):
        for i,j in zip(self.graph.getEdges(), range(self.table.rowCount())):
            for n in range(self.table.columnCount()):
                if n < 2:
                    self.table.setItem(j, n, qtg.QTableWidgetItem(str(i.nodes[n])))
                else:
                    self.table.setItem(j, n, qtg.QTableWidgetItem(str(i.weight[n-2])))
                
    def initTable(self, widgets):
        self.table.setRowCount(100)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Source",
                                              "Destination",
                                              "Distance",
                                              "Safety",
                                              "Speed",
                                              "Facilities"])
        widgets.append(self.table)

    def getTableData(self, click):
        #Clear all nodes and edges
        self.graph.clearAll()

        #Match any cells with text in them
        table_items = self.table.findItems(".+", qtc.Qt.MatchRegExp)

        #Get the set of column membership, so that the len()
        #indicates the number of items
        num_columns = int(self.table.columnCount()) 
        table_items = [{"row":x.row(), "name":str(x.text())} 
                       for x in table_items]
        #Sort into list of [source1, dest1, weights..., source2, dest2, weights...]
        table_items = [x["name"] for x in 
                       sorted(table_items, key=lambda x: x["row"])]

        #Split sorted list into list of tuples (source, dest, weight)        
        table_items = map(None, *([iter(table_items)]*num_columns))

        #Remove any tuples without source, dest, and weight
        table_items = [filter(None, x) for x in table_items]
        table_items = filter(lambda x: len(x) == num_columns, table_items)

        #Get max of each weight column using strides
        #2: is weight values for each path
        weights = [map(float, x[2:]) for x in table_items]
        table_items = [x[:2] for x in table_items]

        #Combine each column's values together into a tuple, then take the max
        maxes = map(max, zip(*weights))
        
        #Normalize by using the value computed from maxes
        norm_weights = []
        for w in weights:
            norm = []
            for n,m in enumerate(maxes):
                norm.append(w[n]/m)
            norm_weights.append(norm)

        #Now do the weighting
        final_weights = []
        for w in norm_weights:
            final = []
            for n,v in enumerate(self.getWeights(None)):
                final.append(v*w[n])
            final_weights.append(final)         
       
        f = operator.add

        #Add edges to graph
        [self.graph.addEdge(x[0][0], x[0][1], weight=x[1], function=f) for x in zip(table_items, final_weights)]
        self.fillTable()

        #Plot new edges
        self.graph_pixmap = qtg.QPixmap(self.createGraph(self.graph))
        self.graph_host.setPixmap(self.graph_pixmap)

    def getOps(self, click):
        if click != None:
           print "Button call for getOps"
           return

        opmap = {"+": operator.add,
                 "x": operator.mul,
                 "^": operator.pow}
        ops = []
        for i in self.op_boxes:
            ops.append(opmap[str(i.currentText())])
        return ops

    def getWeights(self, click):
        if click != None:
           print "Button call for getWeights"
           return 

        weights = []
        for n,b in enumerate(self.weight_boxes):
            try:
                weights.append(float(b.text()))
            except ValueError:
                print "No entry found for box",n,"! Using 1 instead"
                weights.append(1.)
        return weights     

    def updateGraph(self, click):
        self.getOps(click)
        self.getWeights(click)

    def initUpdate(self, widgets):
        button = qtg.QPushButton("Update")
        button.clicked[bool].connect(self.getTableData)
        button.clicked[bool].connect(self.updateGraph)
        widgets.append(button)

    def wanderGraph(self, click):
        print "Wander!" 
        d = DjikstraWanderer(copy.deepcopy(self.graph), 1, 6)
        d.run()
        del d
       
        #for i in range(len(self.graph.nodes)):
        #    w = BruteWanderer(copy.deepcopy(self.graph), i)
        #    w.run()
        #    del w

    def initWander(self, widgets):
        button = qtg.QPushButton("Wander")
        button.clicked[bool].connect(self.wanderGraph)
        widgets.append(button)

    def saveTableData(self, click):
        f = open(self.save_fname, "wb")
        pickle.dump(self.graph, f) 
        f.close()

    def initSave(self, widgets):
        button = qtg.QPushButton("Save")
        button.clicked[bool].connect(self.saveTableData)
        widgets.append(button) 
    
    def clearTableData(self, click):
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                self.table.setItem(i, j, qtg.QTableWidgetItem())
                    
    def initClear(self, widgets):
        button = qtg.QPushButton("Clear")
        button.clicked[bool].connect(self.clearTableData)
        button.clicked[bool].connect(self.getTableData)
        widgets.append(button)

    def debugClass(self, click):
        print [x.Details() for x in self.graph.getNodes()]

    def initWeightEntry(self, widgets):
        form = qtg.QLineEdit()
        mask = "dddD.dd"
        form.setInputMask(mask)
        widgets.append(form)
        self.weight_boxes.append(form)
           
    def initOpBox(self, widgets):
        box = qtg.QComboBox()
        box.addItem("+")
        box.addItem("*")
        box.addItem("^")
        widgets.append(box)
        self.op_boxes.append(box)

    def initFormulaLine(self, widgets):
        label = qtg.QLabel("Formula for weight combination : ")
        weight_boxes = []
        op_boxes = []
        #-2 to remove source, dest
        for i in range(self.table.columnCount()-2):
            #Skip the ops box the first time
            if i != 0:
                self.initOpBox(op_boxes)
            self.initWeightEntry(weight_boxes)
        widgets.append(label)
        [[widgets.append(n) for n in x] for x in zip(weight_boxes, op_boxes)]
        
        #zip won't work for uneven counts 
        widgets.append(weight_boxes[-1])

    def initDebug(self, widgets):
        button = qtg.QPushButton("Debug")
        button.clicked[bool].connect(self.debugClass)
        widgets.append(button)

    def initUI(self):
        top_left_widgets = []
        self.initGraph(top_left_widgets)
        
        top_right_widgets = []
        self.initTable(top_right_widgets)

        middle_widgets = []
        self.initFormulaLine(middle_widgets)

        bottom_widgets = []
        self.initClear(bottom_widgets)
        self.initUpdate(bottom_widgets)
        #self.initDebug(bottom_widgets)
        self.initWander(bottom_widgets)
        self.initSave(bottom_widgets)

        hbox_top = qtg.QHBoxLayout()
        [hbox_top.addWidget(x) for x in top_left_widgets]
        [hbox_top.addWidget(x) for x in top_right_widgets]

        hbox_middle = qtg.QHBoxLayout()
        [hbox_middle.addWidget(x) for x in middle_widgets]
        hbox_middle.addStretch(1)

        hbox_bottom = qtg.QHBoxLayout()
        [hbox_bottom.addWidget(x) for x in bottom_widgets] 
        
        vbox = qtg.QVBoxLayout()
        vbox.addLayout(hbox_top)
        vbox.addLayout(hbox_middle)
        vbox.addLayout(hbox_bottom)
 
        self.setLayout(vbox)
        self.setWindowTitle("Graph Viewer v.01")
        self.show()

if __name__ == "__main__":
    app = qtg.QApplication(sys.argv)
    w = MainView()
    w.resize(1200, 600)
    sys.exit(app.exec_())

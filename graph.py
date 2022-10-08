
import string
import math

circle_radius = 20
minimum_distance_between_nodes = 5 * circle_radius

class Graph:
    def __init__(self):
        self.nodes = []
        self.edges = []
        
    def addNode(self, pos, color = 0):
        # for now adding nodes in alphabetical order. Enough for < 27 nodes (I guess we don't need more than that)        
        if (len(self.nodes) < len(string.ascii_uppercase)) and self.canAddNode(pos):
            name = string.ascii_uppercase[ len(self.nodes) ]
            
            # prevent duplicate node names
            if self.nameInGraph(name):
                for i in range(0, len(self.nodes)):
                    name = string.ascii_uppercase[ i ]
                    if not self.nameInGraph(name):
                        break
            
            node = Node(self, name, pos, color)
            self.nodes.append(node)
            return node
            
    def deleteNode(self, node):
        self.nodes.remove(node)
      
        edgesToRemove = node.edges()
        for edge in edgesToRemove:
            for e in self.edges:
                if e.undirectedSame(edge):
                    self.edges.remove(e)
                    break
               
    def addEdge(self, node1, node2):
        existing = next((x for x in self.edges if ((x.target == node1 and x.source == node2) or (x.target == node2 and x.source == node1))), None)
        
        if existing == None:
            edge = Edge(self, node1, node1.degree() + 1, node2, node2.degree() + 1)
            self.edges.append(edge)
            return edge
        
    # node can be added if the position does not collide with existing nodes (actually we have a bit space between the nodes to make the graph more clear!)
    def canAddNode(self, pos):
        for node in self.nodes:
            xd = pow(node.pos[0] - pos[0], 2)
            yd = pow(node.pos[1] - pos[1], 2)
            d = math.sqrt(xd + yd)
            if d < minimum_distance_between_nodes:
                return False
        
        return True
        
    def nameInGraph(self, name):
        item = next((x for x in self.nodes if x.name == name), None)
        return (item != None)
        
    def nodeInPos(self, pos):
        for node in self.nodes:
            xInside = ((node.pos[0] - circle_radius) <= pos[0]) and (pos[0] <= (node.pos[0] + circle_radius))
            yInside = ((node.pos[1] - circle_radius) <= pos[1]) and (pos[1] <= (node.pos[1] + circle_radius))
            if xInside and yInside:
                return node
                
        return None
        
    def colorsInGraph(self):
        return set(map(lambda x: x.color, self.nodes))
        
        
class Node:
    def __init__(self, graph, name, pos, color = 0):
        self.graph = graph
        self.name = name
        self.pos = pos
        self.color = color
        
    def degree(self):
        return len(self.edges())
     
    # note: this does not necessarily return pointer to the original edge
    def edges(self):
        edges = []
        for edge in self.graph.edges:
            if edge.source == self:
                edges.append( edge )
            elif edge.target == self:
                edges.append( edge.flipped() )
        return edges
        
    def adjacentNodes(self):
        return list(map(lambda x: x.target if (x.source == self) else x.source, self.edges()))
        
    def getAdjacentByPortNumber(self, port):
        for edge in self.edges():
            if edge.sourcePort == port:
                return (edge.target, edge.targetPort)
        return None
        
       
class Edge:
    def __init__(self, graph, node1, node1Port, node2, node2Port):
        self.graph = graph
        self.source = node1
        self.sourcePort = node1Port
        self.target = node2
        self.targetPort = node2Port
        
    def flipped(self):
        return Edge(self.graph, self.target, self.targetPort, self.source, self.sourcePort) 
        
    def undirectedSame(self, edge):
        sourceMatch = (self.source == edge.source) and (self.sourcePort == edge.sourcePort) and (self.target == edge.target) and (self.targetPort == edge.targetPort)
        targetMatch = (self.target == edge.source) and (self.targetPort == edge.sourcePort) and (self.source == edge.target) and (self.sourcePort == edge.targetPort)
                      
        return (sourceMatch or targetMatch) and (self.graph == edge.graph)

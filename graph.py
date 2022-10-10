
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
        nodesToCheckPortNumbering = set()
        for edge in edgesToRemove:
            for e in self.edges:
                if e.sameAs(edge):
                    anotherNode = edge.nodes() - set([node])
                    
                    if len(nodesToCheckPortNumbering) == 0:
                        nodesToCheckPortNumbering = anotherNode
                    else:
                        nodesToCheckPortNumbering.update( anotherNode )
                    
                    self.edges.remove(e)
                    break
         
        # decrease the port numbers of those nodes which had the removed edge
        for node in list(nodesToCheckPortNumbering):
            node.updatePortNumbering()
               
    def addEdge(self, node1, node2):
        existing = next((x for x in self.edges if set(x.nodes()) == set([node1, node2])), None)
        
        if existing == None:
            edge = UndirectedEdge(self, node1, node1.degree() + 1, node2, node2.degree() + 1)
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
        
    def __str__(self):
        return self.name
        
    def degree(self):
        return len(self.edges())
     
    def edges(self):
        return list(filter(lambda a: self in a.nodes(), self.graph.edges))
        
    def edgeByPortNumber(self, port):
        for edge in self.edges():
            if edge.portNumberForNode(self) == port:
                return edge
        return None
        
    # returns tuple (node, port)
    def getAdjacentByPortNumber(self, port):
        edge = self.edgeByPortNumber(port)
        adj = edge.getAdjacentNode(self)
        adjport = edge.portNumberForNode(adj)
        return (adj, adjport)
        
    def numberOfPorts(self):
        return max(list(map(lambda a: a.portNumberForNode(self), self.edges() )), default = 0)
        
    def updatePortNumbering(self):
        if self.degree() < self.numberOfPorts():
            for i in range(1, self.degree() + 1):
                if not self.hasPortNumber(i):
                    edge = self.edgeByPortNumber(self.numberOfPorts())
                    edge.newPortNumberForNode(self, i)
                    return
        
    def hasPortNumber(self, port):
        exist = next((x for x in self.edges() if x.portNumberForNode(self) == port), None)
        return exist != None    
          
class UndirectedEdge:
    def __init__(self, graph, node1, node1Port, node2, node2Port):
        self.graph = graph
        self.nodesWithPorts = [(node1, node1Port), (node2, node2Port)]
        
    def node0WithPort(self):
        return self.nodesWithPorts[0]
    
    def node1WithPort(self):
        return self.nodesWithPorts[1]
        
    def getAdjacentNode(self, node):
        if node == self.node0WithPort()[0]:
            return self.node1WithPort()[0]
        else:
            return self.node0WithPort()[0]
        
    def portNumberForNode(self, node):
        if node == self.node0WithPort()[0]:
            return self.node0WithPort()[1]
        else:    
            return self.node1WithPort()[1]
            
    def newPortNumberForNode(self, node, port):
        if node == self.node0WithPort()[0]:
            self.nodesWithPorts[0] = (self.nodesWithPorts[0][0], port)
        else:
            self.nodesWithPorts[1] = (self.nodesWithPorts[1][0], port)
    
    def nodes(self):
        return set(map(lambda a: a[0], self.nodesWithPorts))
        
    def sameAs(self, edge):
        return set(self.nodes()) == set(edge.nodes())
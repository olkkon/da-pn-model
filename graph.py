
import string
import math

circle_radius = 20
minimum_distance_between_nodes = 5 * circle_radius

class Graph:
    def __init__(self, isVirtual = False):
        self.nodes = []
        self.edges = []
        self.virtual = isVirtual
        
    def addNode(self, pos = None, color = 0, addName = True):
        nodeName = 'N/A'
        if addName and (len(self.nodes) < len(string.ascii_uppercase)):
            # automatic naming is just alphabetically first 27 nodes
            # I guess we don't need more than that for now
            nodeName = string.ascii_uppercase[ len(self.nodes) ]
            
            # prevent duplicate node names
            if self.nameInGraph(nodeName):
                for i in range(0, len(self.nodes)):
                    nodeName = string.ascii_uppercase[ i ]
                    if not self.nameInGraph(nodeName):
                        break
            
        if self.canAddNode(pos):
            node = Node(self, nodeName, pos, color)
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
         
    # case sensitive match
    def nodeByName(self, name):
        return next((x for x in self.nodes if x.name == name), None)
               
    def addEdge(self, node1, node2, addPortNumbering = True):
        if not self.hasEdgeWithNodes(node1, node2):
            if addPortNumbering:
                edge = UndirectedEdge(self, node1, node1.degree() + 1, node2, node2.degree() + 1)
            else:
                edge = UndirectedEdge(self, node1, -1, node2, -1)
                
            self.edges.append(edge)
            return edge
            
    def hasEdgeWithNodes(self, node1, node2):
        return next((x for x in self.edges if set(x.nodes()) == set([node1, node2])), None) != None
        
    # node can be added if the position does not collide with existing nodes (actually we have a bit space between the nodes to make the graph more clear!)
    # OR if the graph is virtual (no UI)
    def canAddNode(self, pos): 
        if self.virtual:
            return True
    
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
        if self.virtual:
            return None
    
        for node in self.nodes:
            xInside = ((node.pos[0] - circle_radius) <= pos[0]) and (pos[0] <= (node.pos[0] + circle_radius))
            yInside = ((node.pos[1] - circle_radius) <= pos[1]) and (pos[1] <= (node.pos[1] + circle_radius))
            if xInside and yInside:
                return node
                
        return None
        
    def colorsInGraph(self):
        return set(map(lambda x: x.color, self.nodes))
        
        
class Node:
    def __init__(self, graph, name, pos = None, color = 0):
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
        return max(self.portNumbering(), default = 0)
    
    def portNumbering(self):
        return list(map(lambda a: a.portNumberForNode(self), self.edges() ))
              
    def updatePortNumbering(self):
        if self.graph.virtual:
            return
   
        if self.degree() < self.numberOfPorts():
            for i in range(1, self.degree() + 1):
                if not self.hasPortNumber(i):
                    edge = self.edgeByPortNumber(self.numberOfPorts())
                    edge.newPortNumberForNode(self, i)
                    return
        
    def hasPortNumber(self, port):
        return port in self.portNumbering()
          
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
        elif node == self.node1WithPort()[0]:
            return self.node0WithPort()[0]
        else:
            raise Exception('Node does not belong to edge')
        
    def portNumberForNode(self, node):
        if node == self.node0WithPort()[0]:
            return self.node0WithPort()[1]
        elif node == self.node1WithPort()[0]:    
            return self.node1WithPort()[1]
        else:
            raise Exception('Node does not belong to edge')
            
    def newPortNumberForNode(self, node, port):
        if node == self.node0WithPort()[0]:
            self.nodesWithPorts[0] = (self.nodesWithPorts[0][0], port)
        elif node == self.node1WithPort()[0]:
            self.nodesWithPorts[1] = (self.nodesWithPorts[1][0], port)
        else:
            raise Exception('Node does not belong to edge')
    
    def nodes(self):
        return set(map(lambda a: a[0], self.nodesWithPorts))
        
    def sameAs(self, edge):
        return set(self.nodes()) == set(edge.nodes())
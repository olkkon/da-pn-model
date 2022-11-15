
from distributedAlgorithm import *
from graph import *

# message encodings
PROPOSAL = 1
ACCEPT = 2
MATCHED = 3
        
class BipartiteMaximalMatching(DistributedAlgorithm):

    def input(self):
        colors = self.graph.colorsInGraph()
        return list(colors)

    # Things to check:
    # - Only two colors used
    # - Bipartiness
    def validateInput(self):
        twoColors = len(self.input()) == 2
        bipartiness = True
        
        for node in self.graph.nodes:
            for i in node.portNumbering():
                (adj, j) = node.getAdjacentByPortNumber(i)
                if node.color == adj.color:
                    bipartiness = False
                    
        return twoColors and bipartiness
        
    def states(self):
        return [self.WUR, self.BUR, self.MR, self.US, self.MS]
        
    def output(self):
        return [self.US, self.MS]
        
    def msg(self):
        return [PROPOSAL, ACCEPT, MATCHED]

    def init(self, name, input_, d):
        if input_ == min(self.input()):
            return self.WUR.copy(self)
        else:
            result = self.BUR.copy(self)
            result.M = set()
            result.X = set([i for i in range(1, d + 1)])
            return result
            
    def send(self, state, d):
        if state.equalTo(self.WUR):
            evenRound = (state.r % 2 == 0)
            k = math.floor(state.r / 2) + (state.r % 2)
            
            if evenRound:
                return ()
            elif (not evenRound) and (k <= d):
                return (PROPOSAL, int((state.r + 1) / 2))
            elif (not evenRound) and (k > d):
                return ()
        elif state.equalTo(self.BUR):
            if (state.r % 2 == 0) and (len(state.M) > 0):
                return (ACCEPT, min(state.M))
            else:
                return ()
        elif state.equalTo(self.MR):
            if (state.r % 2 != 0):
                return (MATCHED, ALLPORTS)
            else:
                return ()
        elif state.equalTo(self.US):
            return ()
        elif state.equalTo(self.MS):
            return ()
        
    def receive(self, nodeName, state, messages, d):
        if state.equalTo(self.WUR):
            acceptMessage = next((x for x in messages if x[0] == ACCEPT), None)
            k = math.floor(state.r / 2) + (state.r % 2)
            
            if (state.r % 2 != 0) and (k > d):
                return self.US.copy(self)
            elif (acceptMessage != None):
                result = self.MR.copy(self)
                result.r = state.r + 1
                result.i = acceptMessage[1]
                return result
            else:
                result = state.copy(self)
                result.r += 1
                return result
        elif state.equalTo(self.BUR):
            evenRound = (state.r % 2 == 0)
            
            if not evenRound:
                proposals_messages = list(filter(lambda x: x[0] == PROPOSAL, messages))
                proposals = set(map(lambda x: x[1], proposals_messages))
                matched_messages = list(filter(lambda x: x[0] == MATCHED, messages))
                matched = set(map(lambda x: x[1], matched_messages))
                
                result = state.copy(self)
                result.r += 1
                result.M.update(proposals)
                result.X = result.X - matched
                return result
            elif evenRound and (len(state.M) > 0):
                result = self.MS.copy(self)
                result.i = min(state.M)
                return result
            elif evenRound and (len(state.X) == 0):
                return self.US.copy(self)
            else:
                result = state.copy(self)
                result.r += 1
                return result
        elif state.equalTo(self.MR):
            if (state.r % 2 != 0):
                result = self.MS.copy(self)
                result.i = state.i
                return result
            else:
                result = state.copy(self)
                result.r += 1
                return result
        elif state.equalTo(self.US):
            return state.copy(self)
        elif state.equalTo(self.MS):
            return state.copy(self)
            
    def paramsByState(self, state):
        if state.equalTo(self.WUR):
            return [state.r]
        elif state.equalTo(self.BUR):
            return [state.r, state.M, state.X]
        elif state.equalTo(self.MR):
            return [state.r, state.i]
        elif state.equalTo(self.US):
            return []
        elif state.equalTo(self.MS):
            return [state.i]
        else:
            return []
            
    def initializeVirtual(self):
        pass
        
    def __init__(self, graph):
    
        # define the states for the problem
        self.WUR = State('WUR', 'White unmatched running')
        self.WUR.r = 1
        
        self.BUR = State('BUR', 'Black unmatched running')
        self.BUR.r = 1
        self.BUR.M = set()
        self.BUR.X = set()
        
        self.MR = State('MR', 'Matched running')
        self.MR.r = 1
        self.MR.i = -1
        
        self.US = State('US', 'Unmatched stopped')

        self.MS = State('MS', 'Matched stopped')
        self.MS.i = -1
        
        for state in self.states():
            state.params = lambda: self.paramsByState(state)
    
        DistributedAlgorithm.__init__(self, "Bipartite Maximal Matching", graph, False)

class MinimumVertexCover3Approximation(DistributedAlgorithm):

    # no additional input is needed for this algorithm
    def input(self):
        pass
        
    def validateInput(self):
        return True
        
    def states(self):
        return [self.BothRunning, self.V1Running, self.V2Running, self.BothStopped]
        
    # binary indicating whether node belongs to matching or not
    def output(self):
        return [self.BothStopped]
        
    def msg(self):
        pass

    def init(self, name, input_, d):
        v1 = self.virtualNodeByName(name, 1)
        v2 = self.virtualNodeByName(name, 2)
        
        if (v1 == None) or (v2 == None):
            raise Exception('init failed: virtual network structure is incomplete')
            
        result = self.BothRunning.copy(self)
        result.state1 = self.virtualProblem.init(v1.name, v1.color, v1.degree())
        result.state2 = self.virtualProblem.init(v2.name, v2.color, v2.degree())
        
        return result

    # simulation algorithm does not determine anything to send by itself. Instead,
    # sending is based on simulated algorithms doing the actual calculation. So we skip
    # this function and do the thing in runOneRoundSimulated
    def send(self, state, d):
        pass
        
    def receive(self, nodeName, state, messages, d):
    
        def bothStoppedState(algo, s1, s2):
            result = algo.BothStopped.copy(algo)
                
            if s1.equalTo(algo.virtualProblem.MS) or s2.equalTo(algo.virtualProblem.MS):
                result.output = 1
            else:
                result.output = 0
            
            return result
                    
        v1 = self.virtualNodeByName(nodeName, 1)
        v2 = self.virtualNodeByName(nodeName, 2)
        
        if (v1 == None) or (v2 == None):
            raise Exception('can not receive messages: virtual network structure is incomplete')
        
        v1_msg = {}
        v2_msg = {}
        
        for msg in messages:
            addOrAppend(v1_msg, v1, (msg[0][1], msg[1]))
            addOrAppend(v2_msg, v2, (msg[0][0], msg[1]))
                   
        v1_msg = list(filter(lambda a: a[0] != SIM_EMPTY_MESSAGE, v1_msg.items()))
        v2_msg = list(filter(lambda a: a[0] != SIM_EMPTY_MESSAGE, v2_msg.items()))
        
        self.virtualProblem.setNewStateBasedOnMessages(v1, v1_msg)
        v1_new = self.virtualProblem.afterRoundStates[v1]
    
        self.virtualProblem.setNewStateBasedOnMessages(v2, v2_msg)
        v2_new = self.virtualProblem.afterRoundStates[v2]        
           
        # change state
        if state.equalTo(self.BothRunning): 
            v1_stopped = stateInStoppingStates(v1_new, self.virtualProblem.output())
            v2_stopped = stateInStoppingStates(v2_new, self.virtualProblem.output())   
            
            if v1_stopped and v2_stopped:
                result = bothStoppedState(self, v1_new, v2_new)
            elif v1_stopped:
                result = self.V2Running.copy(self)
            elif v2_stopped:
                result = self.V1Running.copy(self)
            else:
                result = state.copy(self)
                
            result.state1 = v1_new
            result.state2 = v2_new
            return result          

        elif state.equalTo(self.V1Running):
            if stateInStoppingStates(v1_new, self.virtualProblem.output()):
                result = bothStoppedState(self, v1_new, v2_new)
            else:
                result = state.copy(self)

            result.state1 = v1_new
            result.state2 = v2_new
            return result 
                 
        elif state.equalTo(self.V2Running):
            if stateInStoppingStates(v2_new, self.virtualProblem.output()):
                result = bothStoppedState(self, v1_new, v2_new)
            else:
                result = state.copy(self)

            result.state1 = v1_new
            result.state2 = v2_new
            return result 
            
        elif state.equalTo(self.BothStopped):
            return state.copy(self)
 
    def paramsByState(self, state):
        if state.equalTo(self.BothRunning):
            return [state.state1, state.state2]
        elif state.equalTo(self.V1Running):
            return [state.state1, state.state2]
        elif state.equalTo(self.V2Running):
            return [state.state1, state.state2]
        elif state.equalTo(self.BothStopped):
            return [self.output]
        else:    
            return []
        
    def runOneRound(self):
        DistributedAlgorithm.runOneRoundSimulated(self)
        
    def initializeVirtual(self):
    
        # let us construct the virtual network
        self.virtualNetwork = Graph(True)
        self.virtualProblem = BipartiteMaximalMatching(self.virtualNetwork)
    
        # construct the virtual nodes
        for node in self.graph.nodes:
            v1 = self.virtualNetwork.addNode(addName = False, color = 1)
            v1.name = node.name + '_1'
            v2 = self.virtualNetwork.addNode(addName = False, color = 2)
            v2.name = node.name + '_2'
            
        # construct the virtual edges
        for node in self.graph.nodes:
            for i in node.portNumbering():
                (adj, j) = node.getAdjacentByPortNumber(i)
                
                u1 = self.virtualNodeByName(node.name, 1)
                u2 = self.virtualNodeByName(node.name, 2)
                v1 = self.virtualNodeByName(adj.name, 1)
                v2 = self.virtualNodeByName(adj.name, 2)
                
                if not self.virtualNetwork.hasEdgeWithNodes(u1, v2):
                    e1 = self.virtualNetwork.addEdge(u1, v2, addPortNumbering = False)
                    e1.newPortNumberForNode(u1, i)
                    e1.newPortNumberForNode(v2, j)
                
                if not self.virtualNetwork.hasEdgeWithNodes(u2, v1):
                    e2 = self.virtualNetwork.addEdge(u2, v1, addPortNumbering = False)
                    e2.newPortNumberForNode(u2, i)
                    e2.newPortNumberForNode(v1, j)
        
    def __init__(self, graph):
             
        # define the states for the problem
        self.BothRunning = State('BR', 'v1 running, v2 running')
        self.V1Running =   State('V1', 'v1 running, v2 stopped')
        self.V2Running =   State('V2', 'v1 stopped, v2 running')
        self.BothStopped = State('BS', 'v1 stopped, v2 stopped')
        self.BothStopped.output = -1
        
        for state in self.states():
            # BipartiteMaximalMatching states of nodes V1 and V2 in the virtual network
            # To be initialized while running the first round
            state.state1 = None 
            state.state2 = None
            state.params = lambda: self.paramsByState(state)
                
        DistributedAlgorithm.__init__(self, "Minimum Vertex Cover 3-approximation", graph, True)
        

from distributedAlgorithm import *

# message encodings
PROPOSAL = 1
ACCEPT = 2
MATCHED = 3
        
class BipartiteMaximalMatching(DistributedAlgorithm):

    # we assume proper 2-coloring so the input will consist of two different integers
    def input(self):
        colors = self.graph.colorsInGraph()
        assert(len(colors) == 2)
        return list(colors)
        
    def states(self):
        return [self.WUR, self.BUR, self.MR, self.US, self.MS]
        
    def output(self):
        return [self.US, self.MS]
        
    def msg(self):
        return [PROPOSAL, ACCEPT, MATCHED]

    def init(self, input_, d):
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
                return (MATCHED, self.ALLPORTS)
            else:
                return ()
        elif state.equalTo(self.US):
            return ()
        elif state.equalTo(self.MS):
            return ()
        
    def receive(self, state, messages, d):
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
        
    def __init__(self, graph):
    
        # define the states for the problem
        self.WUR = State('WUR', 'White unmatched running')
        self.WUR.r = 1
        self.WUR.params = lambda: self.paramsByState(self.WUR)
        
        self.BUR = State('BUR', 'Black unmatched running')
        self.BUR.r = 1
        self.BUR.M = set()
        self.BUR.X = set()
        self.BUR.params = lambda: self.paramsByState(self.BUR)
        
        self.MR = State('MR', 'Matched running')
        self.MR.r = 1
        self.MR.i = -1
        self.MR.params = lambda: self.paramsByState(self.MR)
        
        self.US = State('US', 'Unmatched stopped')

        self.MS = State('MS', 'Matched stopped')
        self.MS.i = -1
        self.MS.params = lambda: self.paramsByState(self.MS)
    
        DistributedAlgorithm.__init__(self, "Bipartite Maximal Matching", graph)

class MinimumVertexCover3Approximation(DistributedAlgorithm):

    def input(self):
        pass
        
    def states(self):
        pass
        
    def output(self):
        pass
        
    def msg(self):
        pass

    def init(self, input_, d):
        pass

    def send(self, state, d):
        pass
        
    def receive(self, state, messages, d):
        pass
        
    def paramsByState(self, state):
        pass
        
    def __init__(self, graph):
        DistributedAlgorithm.__init__(self, "Minimum Vertex Cover 3-approximation", graph)
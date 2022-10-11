
import pygame as pg
import sys, math
from pygame.locals import *

from graph import *
from algorithms import *
from UIcomponents import *

(width, height) = (1200, 600)

BUTTON_RIGHT = 3
BUTTON_LEFT = 1

# colors for node coloring. White is default and thus not counting in the coloring sense
GREEN = (153, 255, 51)
DARKGREEN = (0, 102, 51)
LIGHTRED = (255, 153, 153)
PURPLE = (255, 153, 255)
DARKPURPLE = (102, 0, 102)
BLUE = (0, 0, 255)
LIGHTBLUE = (153, 204, 255)
YELLOW = (255, 255, 51)
LIGHTYELLOW = (255, 255, 204)

COLOR_KEYS = [K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]
COLORS = [GREEN, DARKGREEN, LIGHTRED, PURPLE, DARKPURPLE, BLUE, LIGHTBLUE, YELLOW, LIGHTYELLOW]

playgroundBorderX = width - 500;

# early init to reduce surface passing
pg.init()
surface = pg.display.set_mode((width, height))

# init graph
graph = Graph()
node1 = graph.addNode((200, 100), 1)
node2 = graph.addNode((200, 200), 2)
node3 = graph.addNode((500, 200), 1)
node4 = graph.addNode((500, 100), 2)
graph.addEdge(node1, node2)
graph.addEdge(node2, node3)
graph.addEdge(node3, node4)
graph.addEdge(node4, node1)

running = True
running_algo = False
selected_node = None

problems = [BipartiteMaximalMatching(graph), MinimumVertexCover3Approximation(graph)]
buttons = []

algoList = DropDown(
    [COLOR_INACTIVE, COLOR_ACTIVE],
    [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
    playgroundBorderX + 30, 30, 200, 50, 
    pg.font.SysFont('Arial', 20), 
    "Select problem", list(map(lambda a: str(a), problems)))

def selectedProblem():
    if algoList.main == algoList.default:
        return None
    else:
        return problems[algoList.options.index(algoList.main)]

runButton = Button("Run", playgroundBorderX + 240, 30, 100, 50)
runButton.grayCondition = lambda: running_algo
buttons.append( runButton )

clearButton = Button("Clear", playgroundBorderX + 350, 30, 100, 50)
buttons.append( clearButton )

nextRoundButton = Button("Next round", playgroundBorderX + 150, 200, 150, 50)
nextRoundButton.grayCondition = lambda: not (running_algo and selectedProblem().running)
nextRoundButton.visible = False
buttons.append( nextRoundButton )

def run_algo():
    global running_algo
    
    problem = selectedProblem()
    if problem != None:
        running_algo = True
        problem.runOneRound()
    
def clearUI(emptyDropdown):
    global running_algo
    
    if running_algo:
        running_algo = False
        selectedProblem().reset()
    
    if emptyDropdown:
        algoList.setDefault()
    
def nextRound():
    if running_algo:
        selectedProblem().runOneRound()

buttons[0].action = run_algo
buttons[1].action = clearUI(True)
buttons[2].action = nextRound

def main():
    global running, running_algo, selected_node

    surface.fill(WHITE)
    pg.display.set_caption('Distributed Algorithms playground in PN model')
    
    updateScreen()
    pg.display.update()
        
    while running:
    
        # Event handling
        event_list = pg.event.get()
        for event in event_list:
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN and event.button == BUTTON_RIGHT:
                if positionInsidePlayground(event.pos) and not running_algo:
                    graph.addNode(event.pos)
            elif event.type == MOUSEBUTTONDOWN and event.button == BUTTON_LEFT:
                if positionInsidePlayground(event.pos):
                    selection = graph.nodeInPos(event.pos)
                    
                    # selection
                    if selected_node == None:
                        if selection != None:
                            selected_node = selection
                    else:
                        # unselect current selection
                        if selection == None:
                            selected_node = None
                        else:
                            # clicking on selected node itself is same as unselect
                            if selected_node == selection:
                                selected_node = None
                            # construct an edge
                            elif not running_algo:
                                graph.addEdge(selected_node, selection)
                                selected_node = None
                
                else:
                    for button in buttons:
                        if button.visible and button.containsPosition(event.pos) and not button.grayCondition():
                            button.execute()
                    
            elif event.type == KEYDOWN and not running_algo:
                if event.key == K_DELETE:
                    if selected_node != None:
                        graph.deleteNode(selected_node)
                        selected_node = None
                elif event.key in COLOR_KEYS:
                    if selected_node != None:
                        selected_node.color = COLOR_KEYS.index(event.key) + 1
                        selected_node = None
                        
            updateScreen()
            
        if running_algo:
            updateScreen()
            
        # update the dropdown
        selected_option = algoList.update(event_list)
        if selected_option >= 0:
            algoList.main = algoList.options[selected_option]
            clearUI(False)
            
        pg.display.update()
     
def drawHelpBox():
    pg.draw.line(surface, BLACK, (playgroundBorderX, 0), (playgroundBorderX, height))
    
    if running_algo:
        buttons[2].visible = True
        drawText(surface, 15, "Follow console for possible errors in the run", (playgroundBorderX + 30, 170), False)
        drawText(surface, 20, "Round: " + str(selectedProblem().counter), (playgroundBorderX + 30, 210), False)
        
        drawText(surface, 20, "Node", (playgroundBorderX + 30, 280), False)
        drawText(surface, 20, "State before", (playgroundBorderX + 100, 280), False)
        drawText(surface, 20, "State after", (playgroundBorderX + 300, 280), False)
        pg.draw.line(surface, BLACK, (playgroundBorderX + 20, 310), (playgroundBorderX + 450, 310))
        
        for index, node in enumerate(selectedProblem().beforeRoundStates.keys()):
            drawText(surface, 20, str(node), (playgroundBorderX + 30, 320 + index * 30), False) 
            drawText(surface, 20, str(selectedProblem().beforeRoundStates[node]), (playgroundBorderX + 100, 320 + index * 30), False)
            drawText(surface, 20, str(selectedProblem().afterRoundStates[node]), (playgroundBorderX + 300, 320 + index * 30), False)
        
    else:
        buttons[2].visible = False
    
    for button in buttons:
        if button.visible:
            button.draw(surface)
                
def updateScreen():
    surface.fill(WHITE)
    
    algoList.draw(surface)
    
    drawHelpBox()
    
    nodesToDraw = list(filter(lambda n: n != selected_node, graph.nodes))
    for node in nodesToDraw:
        drawNode(node)
        
    if selected_node != None:
        drawNode(selected_node, True)
        
    for edge in graph.edges:
        drawEdge(edge)
       
def drawNode(node, doHighlight = False):
    
    if node.color > 0:
        pg.draw.circle(surface, COLORS[ node.color - 1 ], node.pos, circle_radius)
    
    if doHighlight:
        pg.draw.circle(surface, RED, node.pos, circle_radius, 1)
    else:
        pg.draw.circle(surface, BLACK, node.pos, circle_radius, 1)
        
    drawText(surface, circle_radius, node.name, node.pos)

def drawEdge(edge):
    
    (x0, y0) = edge.node0WithPort()[0].pos
    (x1, y1) = edge.node1WithPort()[0].pos
    dx = x1 - x0
    dy = y1 - y0
    mag = math.hypot(dx, dy)
    
    dxMag = dx / mag
    dyMag = dy / mag
       
    pg.draw.line(surface, BLACK, (x0 + circle_radius * dxMag, y0 + circle_radius * dyMag), (x1 - circle_radius * dxMag, y1 - circle_radius * dyMag))
    
    portX = x0 + circle_radius * 2 * dxMag
    portY = y0 + circle_radius * 2 * dyMag
    
    drawText(surface, 15, str(edge.node0WithPort()[1]), (portX, portY), True, RED)
    
    portX = x1 - circle_radius * 2 * dxMag
    portY = y1 - circle_radius * 2 * dyMag
    
    drawText(surface, 15, str(edge.node1WithPort()[1]), (portX, portY), True, RED)
        
def positionInsidePlayground(pos):
    return pos[0] < playgroundBorderX
    
def exit_app():
    pg.quit()
    sys.exit()

if __name__ == '__main__':
    main()
    exit_app()
    
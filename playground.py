
import pygame, sys, math
from pygame.locals import *
from graph import *
from distributedAlgorithm import *

(width, height) = (1200, 600)

BUTTON_RIGHT = 3
BUTTON_LEFT = 1

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

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
selected_problem = BipartiteMaximalMatching("Bipartite Maximal Matching", graph)

# data structure for buttons in the UI
class Button:
    def __init__(self, name, left, top, width, height):
        self.name = name
        self.pos = ((left, top), (width, height))
        self.action = lambda: print('not assigned')

    def left(self):
        return self.pos[0][0]
        
    def top(self):
        return self.pos[0][1]
        
    def width(self):
        return self.pos[1][0]
        
    def height(self):
        return self.pos[1][1]

    def execute(self):
        self.action()

buttons = []
buttons.append( Button("Run the algorithm", playgroundBorderX + 30, 100, 250, 50) )
buttons.append( Button("Clear", playgroundBorderX + 300, 100, 100, 50) ) 

def run_algo():
    global running_algo
    running_algo = True
    selected_problem.run()
    
def clear():
    global running_algo
    running_algo = False
    selected_problem.reset()

buttons[0].action = run_algo
buttons[1].action = clear

def main():
    global running, running_algo, selected_node

    pygame.init()
    surface = pygame.display.set_mode((width, height))
    surface.fill(WHITE)
    pygame.display.set_caption('Distributed Algorithms playground in PN model')
    
    updateScreen(surface)
    pygame.display.update()
        
    while running:
    
        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN and event.button == BUTTON_RIGHT:
                if positionInsidePlayground(event.pos):
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
                            else:
                                graph.addEdge(selected_node, selection)
                                selected_node = None
                
                else:
                    for button in buttons:
                        if positionInsideButton(event.pos, button):
                            button.execute()
                    
            elif event.type == KEYDOWN:
                if event.key == K_DELETE:
                    if selected_node != None:
                        graph.deleteNode(selected_node)
                        selected_node = None
                elif event.key in COLOR_KEYS:
                    if selected_node != None:
                        selected_node.color = COLOR_KEYS.index(event.key) + 1
                        selected_node = None
                        
            updateScreen(surface)
            
        if running_algo:
            updateScreen(surface)
                        
        pygame.display.update()
     
def drawHelpBox(surface):
    pygame.draw.line(surface, BLACK, (playgroundBorderX, 0), (playgroundBorderX, height))
    drawText(surface, 20, "Selected problem: " + selected_problem.desc, (playgroundBorderX + 30, 30), False)
    
    for button in buttons:
        drawButton(surface, button.name, button)
        
    if running_algo:
        drawText(surface, 15, "Follow console for possible errors in the run", (playgroundBorderX + 30, 170), False)
        drawText(surface, 20, "Round: " + str(selected_problem.counter), (playgroundBorderX + 30, 300), False)
     
def updateScreen(surface):
    surface.fill(WHITE)
    
    drawHelpBox(surface)
    
    nodesToDraw = list(filter(lambda n: n != selected_node, graph.nodes))
    for node in nodesToDraw:
        drawNode(surface, node)
        
    if selected_node != None:
        drawNode(surface, selected_node, True)
        
    for edge in graph.edges:
        drawEdge(surface, edge)
       
def drawNode(surface, node, doHighlight = False):
    
    if node.color > 0:
        pygame.draw.circle(surface, COLORS[ node.color - 1 ], node.pos, circle_radius)
    
    if doHighlight:
        pygame.draw.circle(surface, RED, node.pos, circle_radius, 1)
    else:
        pygame.draw.circle(surface, BLACK, node.pos, circle_radius, 1)
        
    drawText(surface, circle_radius, node.name, node.pos)

def drawEdge(surface, edge):
    
    (x0, y0) = edge.node0WithPort()[0].pos
    (x1, y1) = edge.node1WithPort()[0].pos
    dx = x1 - x0
    dy = y1 - y0
    mag = math.hypot(dx, dy)
    
    dxMag = dx / mag
    dyMag = dy / mag
       
    pygame.draw.line(surface, BLACK, (x0 + circle_radius * dxMag, y0 + circle_radius * dyMag), (x1 - circle_radius * dxMag, y1 - circle_radius * dyMag))
    
    portX = x0 + circle_radius * 2 * dxMag
    portY = y0 + circle_radius * 2 * dyMag
    
    drawText(surface, 15, str(edge.node0WithPort()[1]), (portX, portY), True, RED)
    
    portX = x1 - circle_radius * 2 * dxMag
    portY = y1 - circle_radius * 2 * dyMag
    
    drawText(surface, 15, str(edge.node1WithPort()[1]), (portX, portY), True, RED)
    
def drawText(surface, fontSize, text, pos, center = True, color = BLACK):
    font = pygame.font.SysFont('Arial', fontSize)
    textSurf = font.render(text, True, color)
    
    if center:
        textRect = textSurf.get_rect(center = pos)
        surface.blit(textSurf, textRect)
    else:
        surface.blit(textSurf, pos)
        
def drawButton(surface, text, button):
    pygame.draw.rect(surface, BLACK, button.pos, 1)
    drawText(surface, 20, text, ((button.left() + button.width() / 2), (button.top() + button.height() / 2)))
        
def positionInsidePlayground(pos):
    return pos[0] < playgroundBorderX
    
def positionInsideButton(pos, button):
    return ((button.left() <= pos[0]) and (pos[0] <= button.left() + button.width()) and
            (button.top() <= pos[1]) and (pos[1] <= button.top() + button.height()))
    
def exit_app():
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
    exit_app()
    
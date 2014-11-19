#from astar import AStar, AStarNode
#from math import sqrt

#class AStarGrid(AStar):
#    def heuristic(self, node, start, end):
#        return sqrt((end.x - node.x)**2 + (end.y - node.y)**2)

#class AStarGridNode(AStarNode):
#    def __init__(self, x, y):
#        self.x, self.y = x, y
#        super(AStarGridNode, self).__init__()

#    def move_cost(self, other):
#        diagonal = abs(self.x - other.x) == 1 and abs(self.y - other.y) == 1
#        return 14 if diagonal else 10

import heapq

class AStar:
#class AStar(object):
#    def __init__(self, graphAstar):
#        self.graphAstar = graphAstar
        
    def heuristic(self, node, start, end):
        raise NotImplementedError
       
    # def search(self, start, end):
    def search(self, start, end):
        # self.g = 0
	#start.parent = None
	openset = set()
        closedset = set()
        current = start
	openHeap = []
        openset.add(current)
	openHeap.append((0,current))
        while openset:
	    # self.g = 0
            # current = min(openset, key=lambda o:o.gg + o.hh)
	    # current = sorted(openset, key=lambda inst:inst.H)[0]
	    # current = min(openset, key=lambda inst:inst.h_heu)
	    # current = heapq.heappop(openHeap)[1]
	    temp = heapq.heappop(openHeap)
	    current = temp[1]
            if current == end:
		print "come" 
                path = []
                while current.parent:
                    path.append(current)
                    current = current.parent
		    # QMessageBox.information( self.iface.mainWindow(),"Info", "come4" )
                path.append(current)
                return path[::-1]
            openset.remove(current)
            closedset.add(current)
	    #QMessageBox.information( self.iface.mainWindow(),"Info", "come2" )
	    print "come2"
            for neighbor in self.graphAstar[current]:
	    #for neighbor in self.graphAstar.neighbors(current):	
		print "come3"
                if neighbor in closedset:
                    continue
                if neighbor in openset:
                    new_g = current.gg + current.move_cost(neighbor)
                    if neighbor.gg > new_g:
                        neighbor.gg = new_g
                        neighbor.parent = current
                else:
                    neighbor.gg = current.gg + current.move_cost(neighbor)
                    neighbor.H = self.heuristic(neighbor, start, end)
                    neighbor.parent = current
                    openset.add(neighbor)
		    heapq.heappush(openHeap, (neighbor.H,neighbor))
		    #QMessageBox.information( self.iface.mainWindow(),"Info", "come3" )
		    print "come3"
        return None

#new
    #def aStar(self, graph, current, end):
    	#openList = set()
    	#closedList = set()

    	#def retracePath(c):
        	#def parentgen(c):
             		#while c:
                 		#yield c
                 		#c = c.parent
        	#result = [element for element in parentgen(c)]
        	#result.reverse()
        	#return result

    	#openList.add(current)
    	#while openList:
        	#current = sorted(openList, key=lambda inst:inst.H)[0]
        	#if current == end:
            		#return retracePath(current)
        	#openList.remove(current)
        	#closedList.add(current)
        	#for tile in graph[current]:
            		#if tile not in closedList:
                		#tile.H = (abs(end.x-tile.x)+abs(end.y-tile.y))*10 
                		#openList.add(tile)
                		#tile.parent = current
    	#return []
#new


#new2

#import heapq

    def astarSearch(self, graphAstar, current, end):
    	openSet = set()
    	openHeap = []
    	closedSet = set()

    	def retracePath(c):
        	path = [c]
        	while c.parent is not None:
            		c = c.parent
            		path.append(c)
        	path.reverse()
        	return path

    	openSet.add(current)
    	openHeap.append((0,current))
    	while openSet:
		print "come2"
        	current = heapq.heappop(openHeap)[1]
        	if current == end:
			print "come3"            		
			return retracePath(current)
        	openSet.remove(current)
        	closedSet.add(current)
        	for tile in graphAstar[current]:
			print "come4"
            		if tile not in closedSet:
                		tile.H = (abs(end.x-tile.x)+abs(end.y-tile.y))*10 
                		if tile not in openSet:
                    			openSet.add(tile)
                    			heapq.heappush(openHeap, (tile.H,tile))
                		tile.parent = current
    	return []


#new2











class AStarNode(object):
    def __init__(self):
        self.gg = 0
        self.H = 0
        self.parent = None
        
    def move_cost(self, other):
        raise NotImplementedError



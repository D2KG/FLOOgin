class Dijk:
  def __init__(self):
    self.nodes = set()
    #self.edges = defaultdict(list)
    self.edges = {}
    self.distances = {}

#  def add_node(self, value):
#    self.nodes.add(value)

#  def add_edge(self, from_node, to_node, distance):
#    self.edges[from_node].append(to_node)
#    self.edges[to_node].append(from_node)
#    self.distances[(from_node, to_node)] = distance


  def dijsktra(self, graph, initial):
    visited = {initial: 0}
    path = {}

    #self.nodes = set(graph.nodes)
    self.nodes = graph.nodes()

    while self.nodes: 
      min_node = None
      for node in self.nodes:
        if node in visited:
          if min_node is None:
            min_node = node
          elif visited[node] < visited[min_node]:
            min_node = node

      if min_node is None:
        break

      self.nodes.remove(min_node)
      current_weight = visited[min_node]

      for edge in graph.edges[min_node]:
        weight = current_weight + graph.distance[(min_node, edge)]
        if edge not in visited or weight < visited[edge]:
          visited[edge] = weight
          path[edge] = min_node

    return visited, path

#new

  def shortest_path(self, graph, initial_node, goal_node):
      distances, paths = self.dijsktra(graph, initial_node)
      route = [goal_node]

      while goal_node != initial_node:
          route.append(paths[goal_node])
          goal_node = paths[goal_node]

      route.reverse()
      return route


#new




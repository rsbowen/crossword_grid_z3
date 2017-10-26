from z3 import *

def GenerateReachability(width, height, solver, squares):
  #distance constraints for reachability
  distances = IntVector("distances", width*height)
  solver.add(distances[0] == 0)
  for row in xrange(height):
    for col in xrange(width):
      if(row==0 and col==0): continue
      index = row*width+col
      left_neighbor_index = index-1
      right_neighbor_index = index+1
      up_neighbor_index = index-width
      down_neighbor_index = index+width
      dist_constraints = []
      #every white square EXCEPT (0,0) must have some neighbor with a lower distance
      if(row != 0):
        dist_constraints.append(And(squares[up_neighbor_index], distances[index] == distances[up_neighbor_index]+1))
      if(row < height-1):
        dist_constraints.append(And(squares[down_neighbor_index], distances[index] == distances[down_neighbor_index]+1))
      if(col != 0):
        dist_constraints.append(And(squares[left_neighbor_index], distances[index] == distances[left_neighbor_index]+1))
      if(col < width-1):
        dist_constraints.append(And(squares[right_neighbor_index], distances[index] == distances[right_neighbor_index]+1))
      solver.add(Implies(squares[index], Or(dist_constraints)))
  return distances

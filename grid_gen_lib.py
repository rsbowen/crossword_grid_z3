from z3 import *


# prediate should take 5 arguments: me, left, right, up, down
def FullGridPredicate(name, width, height, solver, squares, pred):
  predicate = BoolVector(name, width*height)
  for row in xrange(height):
    for col in xrange(width):
      index = row*width+col
      left = False if col==0 else squares[index-1]
      right = False if col==width-1 else squares[index+1]
      up = False if row==0 else squares[index-width]
      down = False if row==height-1 else squares[index+width]
      solver.add(pred(predicate(index), left, right, up, down))
  return predicate

def HorizontalWordEndPredicate(width, height, solver, squares):
  # Horizontal Word End means this square is white and its right neighbor isn't.
  return FullGridPredicate("horizontal-word-end-predicate", width, height, solver, squares, lambda m, l, r, u, d: And(m, Not(r)))

def VerticalWordEndPredicate(width, height, solver, squares):
  # Vertical Word End means this square is white and its lower neighbor isn't.
  return FullGridPredicate("vertical-word-end-predicate", width, height, solver, squares, lambda m, l, r, u, d: And(m, Not(d)))

def HorizontalWordStartPredicate(width, height, solver, squares):
  # Horizontal Word start means this square is white and its left neighbor isn't.
  return FullGridPredicate("horizontal-word-end-predicate", width, height, solver, squares, lambda m, l, r, u, d: And(m, Not(l)))

def VerticalWordStartPredicate(width, height, solver, squares):
  # Vertical Word End means this square is white and its upper neighbor isn't.
  return FullGridPredicate("vertical-word-end-predicate", width, height, solver, squares, lambda m, l, r, u, d: And(m, Not(u)))

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

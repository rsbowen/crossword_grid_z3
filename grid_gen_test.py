from grid_gen_lib import *
from z3 import *

def EnforceGrid(solver, squares, grid_squares):
  for (square, grid_square) in zip(squares, grid_squares):
    solver.add(square == grid_square)

# Unit test for GenerateReachability. For now just a single positive and single negative test.


def ReachabilityPositiveTest():
  solver = Solver()
  squares = BoolVector("squares", 5*5)
  connected_grid = [True, True, False, True, True,
                    True, True, False, True, True,
		    False, True, True, True, False,
                    True, True, False, True, True,
                    True, True, False, True, True]
  EnforceGrid(solver, squares, connected_grid)
  GenerateReachability(5,5,solver, squares)
  if(solver.check() == unsat): print "Reachability positive test failed"

def ReachabilityNegativeTest():
  solver = Solver()
  squares = BoolVector("squares", 5*5)
  connected_grid = [True, True, False, True, True,
                    True, True, False, True, True,
		    False, False, False, False, False,
                    True, True, False, True, True,
                    True, True, False, True, True]
  EnforceGrid(solver, squares, connected_grid)
  GenerateReachability(5,5,solver, squares)
  if(solver.check() != unsat): print "Reachability negative test failed"

def HorizontalWordEndPredicateTest():
  solver = Solver()
  squares = BoolVector("squares", 5*5)
  grid = \
    [True, True, False, True, True,
    True, True, False, True, True,
    False, True, True, True, False,
    True, True, False, True, True,
    True, True, False, True, True]
  expected = \
    [False, True, False, False, True,
    False, True, False, False, True,
    False, False, False, True, False,
    False, True, False, False, True,
    False, True, False, False, True]
  horiz_wordend = HorizontalWordEndPredicate(width,height,solver,squares)
  if(solver.check() == unsat): print "Horizontal word end: was unsat"
  model = solver.model()
  for (index , (horiz_square, expected)) in enumerate(zip(horiz_wordend, expected)):
    if(model[horiz_square] != expected): print "Horizontal word end: bad at index",index


if __name__ == '__main__':
  print "Running tests"
  ReachabilityPositiveTest()
  ReachabilityNegativeTest()
  print "Done."

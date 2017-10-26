from z3 import *
import time
from grid_gen_lib import *
width = 15  
height = 15

# TODO: width height row col doesn't make sense as an argument order
def Neighbors(width, height, row, col, squares):
  index = row*width+col
  neighbors = {}
  neighbors['l'] = False if col==0 else squares[index-1]
  neighbors['r'] = False if col==width-1 else squares[index+1]
  neighbors['u'] = False if row==0 else squares[index-width]
  neighbors['d'] = False if row==height-1 else squares[index+width]
  return neighbors


max_num_black_squares = 40
min_num_black_squares = 0

min_word_length = 3
max_word_length_vert = 9
max_word_length_horiz = 15 

squares = BoolVector('squares', width*height)
horizontal_word_lengths = IntVector('horizontal_word_lengths', width*height)
vertical_word_lengths = IntVector('vertical_word_lengths', width*height)

solver = Solver()

#top left square is always white
solver.add(squares[0] == True)

#todo: replace all counters like black_square_count with PBEQ, PBLT, etc.
for row in xrange(height):
  for col in xrange(width):
    #squares being black (=false) means their word_lengths are zero
    index = row*width + col
    neighbors = Neighbors(width, height, row, col, squares)
    h_word_start = And(squares[index], Not(neighbors['l']))
    h_word_end = And(squares[index], Not(neighbors['r']))
    v_word_start = And(squares[index], Not(neighbors['u']))
    v_word_end = And(squares[index], Not(neighbors['d']))

    solver.add(Implies(Not(squares[index]), horizontal_word_lengths[index] == 0))
    solver.add(Implies(Not(squares[index]), vertical_word_lengths[index] == 0))
    # word starts have word length 1
    solver.add(Implies(v_word_start, vertical_word_lengths[index] == 1))
    solver.add(Implies(h_word_start, horizontal_word_lengths[index] == 1))
    
    # other squares are one longer than their neighbor
    if(row > 0): solver.add(Implies(And(squares[index], Not(v_word_start)),
                       vertical_word_lengths[index] == vertical_word_lengths[index-width] + 1))
    if(col > 0): solver.add(Implies(And(squares[index], Not(h_word_start)),
                       horizontal_word_lengths[index] == horizontal_word_lengths[index-1] + 1))

    # word lengths are bounded
    solver.add(Implies(h_word_end, horizontal_word_lengths[index] >= min_word_length))
    solver.add(Implies(h_word_end, horizontal_word_lengths[index] <= max_word_length_horiz))
    solver.add(Implies(v_word_end, vertical_word_lengths[index] >= min_word_length))
    solver.add(Implies(v_word_end, vertical_word_lengths[index] <= max_word_length_vert))

black_square_pb_tuple =tuple( ( (Not(squares[index]), 1) for index in xrange(width*height)))
solver.add(PbGe(black_square_pb_tuple, min_num_black_squares))
solver.add(PbLe(black_square_pb_tuple, max_num_black_squares))

#symmetry constraints, TODO: this might be faster if we just kept half of the squares
for row in xrange(height):
  for col in xrange(width):
    index = row*width+col
    symm_index = (height-row-1)*width+(width-col-1)
    solver.add(Implies(squares[index],squares[symm_index]))
    solver.add(Implies(Not(squares[index]),Not(squares[symm_index])))

distances = GenerateReachability(width, height, solver, squares)


#TODO: from a software point of view all of the word size counters should probably be unified, there is lots of copy/paste!

def addHorizWordSizeConstraint(name, size, target):
  #set up counters
  word_size_counter = IntVector(name, width*height)
  solver.add(word_size_counter[0] == 0)
  for row in xrange(height):
    for col in xrange(width):
      index = row*width+col
      if(index==0): continue
      solver.add(Implies(Not(squares[index]), word_size_counter[index] == word_size_counter[index-1]))
      if(col == width-1): word_terminating = True
      else: word_terminating = And(squares[index], Not(squares[index+1]))
      # word-terminating 
      solver.add(Implies(And(word_terminating, horizontal_word_lengths[index] == size), word_size_counter[index] == word_size_counter[index-1] + 1))
      solver.add(Implies(And(word_terminating, horizontal_word_lengths[index] != size), word_size_counter[index] == word_size_counter[index-1]))
      # non-word-terminating squares just pass the counter value forward
      solver.add(Implies(Not(word_terminating), word_size_counter[index] == word_size_counter[index-1]))
  solver.add(word_size_counter[width*height - 1] == target)
  return word_size_counter

def addVertWordSizeConstraint(name, size, target):
  #set up counters
  word_size_counter = IntVector(name, width*height)
  solver.add(word_size_counter[0] == 0)
  for row in xrange(height):
    for col in xrange(width):
      index = row*width+col
      if(index==0): continue
      solver.add(Implies(Not(squares[index]), word_size_counter[index] == word_size_counter[index-1]))
      if(row == height-1): word_terminating = True
      else: word_terminating = And(squares[index], Not(squares[index+width]))
      # word-terminating 
      solver.add(Implies(And(word_terminating, vertical_word_lengths[index] == size), word_size_counter[index] == word_size_counter[index-1] + 1))
      solver.add(Implies(And(word_terminating, vertical_word_lengths[index] != size), word_size_counter[index] == word_size_counter[index-1]))
      # non-word-terminating squares just pass the counter value forward
      solver.add(Implies(Not(word_terminating), word_size_counter[index] == word_size_counter[index-1]))
  solver.add(word_size_counter[width*height - 1] == target)
  return word_size_counter

addHorizWordSizeConstraint("theme-clue-length-2", 15, 2)
addHorizWordSizeConstraint("theme-clue-length-3", 14, 0)
addHorizWordSizeConstraint("theme-clue-length-4", 13, 0)
addHorizWordSizeConstraint("theme-clue-length-5", 12, 0)
addHorizWordSizeConstraint("theme-clue-length-6", 11, 0)
addHorizWordSizeConstraint("theme-clue-length-7", 10, 0)
addHorizWordSizeConstraint("theme-clue-length-8", 9, 0)
addHorizWordSizeConstraint("theme-clue-length-9", 8, 0)

#No cheaters.
#The way cruciverb writes this is: "cheater" black squares (ones that do not affect the number of words in the puzzle...) are bad
#This is a simple-to-implement constraint: black squares should have at most 2 neighboring black squares
#Another possibility is to use a 'counter' like above and, instead of outright banning these, just make there be a few.
for row in xrange(height):
  for col in xrange(width):
    index = row*width+col
    left_neighbor_index = index-1
    right_neighbor_index = index+1
    up_neighbor_index = index-width
    down_neighbor_index = index+width
    up = False if row==0 else squares[up_neighbor_index]
    left = False if col==0 else squares[left_neighbor_index]
    down = False if row==height-1 else squares[down_neighbor_index]
    right = False if col==width-1 else squares[right_neighbor_index]
    solver.add(Implies(Not(squares[index]), Or(up, left)))
    solver.add(Implies(Not(squares[index]), Or(up, right)))
    solver.add(Implies(Not(squares[index]), Or(down, left)))
    solver.add(Implies(Not(squares[index]), Or(down, right)))

# helpful to add constraints to encourage the solver to make traditional-looking blocks by fixing the top and left.
top_blocks = [True]*5 + [False] + [True]*4 + [False] + [True]*5
left_blocks = [True]*4 + [False] + [True]*5 + [False] + [True]*5

for col in xrange(width):
  solver.add(squares[col] == top_blocks[col])
for row in xrange(height):
  solver.add(squares[row*width] == left_blocks[row])


def ComputeAndPrintBoard():
  print "Solving"
  start = time.time()
  print solver.check()
  print "Solved, time was ", time.time()-start
  m = solver.model()
  board = []
  for row in xrange(height):
    for col in xrange(width):
      index = row*width + col
      if(m[squares[index]]): board.append(" ")
      else: board.append("#")
    board.append("|\n")
  print "".join(board)

def AnotherBoard():
  m=solver.model()
  new_soln_constraints = []
  for row in xrange(height):
    for col in xrange(width):
      index = row*width+col
      new_soln_constraints.append(squares[index] != m[squares[index]])
  solver.add(Or(new_soln_constraints))
  ComputeAndPrintBoard()
      
  
ComputeAndPrintBoard()

from z3 import *
import time
width = 15  
height = 15

max_num_black_squares = 40 
min_num_black_squares = 0

min_word_length = 3
max_word_length = 8

squares = BoolVector('squares', width*height)
horizontal_word_lengths = IntVector('horizontal_word_lengths', width*height)
vertical_word_lengths = IntVector('vertical_word_lengths', width*height)
black_square_count = IntVector('black_square_count', width*height)

solver = Solver()

#top left square is always white
solver.add(squares[0] == True)

#set up counters
solver.add(black_square_count[0] == 0)

for row in xrange(height):
  for col in xrange(width):
    #squares being black (=false) means their word_lengths are zero
    index = row*width + col
    left_neighbor_index = index-1
    right_neighbor_index = index+1
    up_neighbor_index = index-width
    down_neighbor_index = index+width
    solver.add(Implies(Not(squares[index]), horizontal_word_lengths[index] == 0))
    solver.add(Implies(Not(squares[index]), vertical_word_lengths[index] == 0))
    #white squares on the left edge have horizontal_word_length equal to 1
    if(col == 0):
      solver.add(Implies(squares[index], horizontal_word_lengths[index]==1))
    #white squares not on the left edge have horizontal_word_length equal to 1+their left neighbor
    else:
      solver.add(Implies(squares[index], horizontal_word_lengths[index] == horizontal_word_lengths[left_neighbor_index] + 1))
    #white squares on the right edge have horizontal_word_lengths at least min_word_length
    if(col == width-1):
      solver.add(Implies(squares[index], horizontal_word_lengths[index] >= min_word_length))
      solver.add(Implies(squares[index], horizontal_word_lengths[index] <= max_word_length))
    #white squares whose right neighbor is black also have horizontal_word_lengths at least min_word_length
    else:
      solver.add(Implies(And(squares[index], Not(squares[right_neighbor_index])), horizontal_word_lengths[index] >= min_word_length))
      solver.add(Implies(And(squares[index], Not(squares[right_neighbor_index])), horizontal_word_lengths[index] <= max_word_length))

    if(row == 0):
      #white squares on the top edge have vertical_word_length equal to 1
      solver.add(Implies(squares[index], vertical_word_lengths[index]==1))
    else:
      #other white squares have veritcal word length one greater than the one above
      solver.add(Implies(squares[index], vertical_word_lengths[index] == vertical_word_lengths[up_neighbor_index] + 1))
    #word-terminal white squares (on the bottom edge, or below neighbor is black)
    if(row == height-1):
      solver.add(Implies(squares[index], vertical_word_lengths[index] >= min_word_length))
      solver.add(Implies(squares[index], vertical_word_lengths[index] <= max_word_length))
    #white squares whose below neighbor is black also have vertical_word_lengths at least min_word_length
    else:
      solver.add(Implies(And(squares[index], Not(squares[down_neighbor_index])), vertical_word_lengths[index] >= min_word_length))
      solver.add(Implies(And(squares[index], Not(squares[down_neighbor_index])), vertical_word_lengths[index] <= max_word_length))

    #keep a running count of the number of black squares
    if(index > 0):
      solver.add(Implies(Not(squares[index]), black_square_count[index] == black_square_count[index-1]+1))
      solver.add(Implies(squares[index], black_square_count[index] == black_square_count[index-1]))

solver.add(black_square_count[width*height - 1] <= max_num_black_squares)
solver.add(black_square_count[width*height - 1] >= min_num_black_squares)

#symmetry constraints, TODO: this might be faster if we just kept half of the squares
for row in xrange(height):
  for col in xrange(width):
    index = row*width+col
    symm_index = (height-row-1)*width+(width-col-1)
    solver.add(Implies(squares[index],squares[symm_index]))
    solver.add(Implies(Not(squares[index]),Not(squares[symm_index])))

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

wsc = addHorizWordSizeConstraint("theme-clue-length-8", 8, 4)
addVertWordSizeConstraint("theme-clue-length-8-v", 8, 0)

#TODO: this is a not-quite-right thing whose job is to keep the black squares from 'clumping' or being 'cheaters'
#The way cruciverb writes this is: "cheater" black squares (ones that do not affect the number of words in the puzzle...) are bad
#This is a simple-to-implement constraint: black squares should have at most 2 neighboring black squares
#Another possibility is to use a 'counter' like above and, instead of outright banning these, instead allow just a few.
for row in xrange(height):
  for col in xrange(width):
    index = row*width+col
    left_neighbor_index = index-1
    right_neighbor_index = index+1
    up_neighbor_index = index-width
    down_neighbor_index = index+width
    neighbor_constraints = [];
    neighbors = [];
    if(row != 0): neighbors.append(up_neighbor_index)
    if(col != 0): neighbors.append(left_neighbor_index)
    if(row != height-1): neighbors.append(down_neighbor_index)
    if(col != width-1): neighbors.append(right_neighbor_index)
    #must be some pair where both are white
    for n1 in range(len(neighbors)):
      for n2 in range(n1+1, len(neighbors)):
        neighbor_constraints.append(And(squares[neighbors[n1]], squares[neighbors[n2]]))
    solver.add(Implies(Not(squares[index]), Or(neighbor_constraints)))

# helpful to add constraints to encourage the solver to make traditional-looking blocks by fixing the top and left.
#this is the 4-5-4 configuration
top_blocks = [True, True, True, True, False, True, True, True, True, True, False, True, True, True, True]
left_blocks = [True, True, True, True, False, True, True, True, True, True, False, True, True, True, True]

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
  print m[black_square_count[width*height-1]]

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
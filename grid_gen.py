# TODO: this is specific to my setup, shouldn't be so.
import __builtin__
__builtin__.Z3_LIB_DIRS = ['../z3/install/lib/']

from z3 import *
import time
from grid_gen_lib import *

class GridGenerator:
  def Neighbors(self, row, col):
    index = row*self.width+col
    neighbors = {}
    neighbors['l'] = False if col==0 else self.squares[index-1]
    neighbors['r'] = False if col==self.width-1 else self.squares[index+1]
    neighbors['u'] = False if row==0 else self.squares[index-self.width]
    neighbors['d'] = False if row==self.height-1 else self.squares[index+self.width]
    return neighbors

  def __init__(self, width, height, max_num_black_squares, min_num_black_squares, min_word_length, max_word_length_vert, max_word_length_horiz, themes):
    #todo: add some sanity checks, like themes are shorter than max horizontal length
    self.width = width
    self.height = height
    self.squares = BoolVector('self.squares', self.width*self.height)
    horizontal_word_lengths = IntVector('horizontal_word_lengths', self.width*self.height)
    vertical_word_lengths = IntVector('vertical_word_lengths', self.width*self.height)
    
    self.solver = Solver()
    
    #top left square is always white
    self.solver.add(self.squares[0] == True)
    
    #todo: replace all counters like black_square_count with PBEQ, PBLT, etc.
    for row in xrange(self.height):
      for col in xrange(self.width):
        #self.squares being black (=false) means their word_lengths are zero
        index = row*self.width + col
        neighbors = self.Neighbors(row, col)
        h_word_start = And(self.squares[index], Not(neighbors['l']))
        h_word_end = And(self.squares[index], Not(neighbors['r']))
        v_word_start = And(self.squares[index], Not(neighbors['u']))
        v_word_end = And(self.squares[index], Not(neighbors['d']))
    
        self.solver.add(Implies(Not(self.squares[index]), horizontal_word_lengths[index] == 0))
        self.solver.add(Implies(Not(self.squares[index]), vertical_word_lengths[index] == 0))
        # word starts have word length 1
        self.solver.add(Implies(v_word_start, vertical_word_lengths[index] == 1))
        self.solver.add(Implies(h_word_start, horizontal_word_lengths[index] == 1))
        
        # other self.squares are one longer than their neighbor
        if(row > 0): self.solver.add(Implies(And(self.squares[index], Not(v_word_start)),
                           vertical_word_lengths[index] == vertical_word_lengths[index-self.width] + 1))
        if(col > 0): self.solver.add(Implies(And(self.squares[index], Not(h_word_start)),
                           horizontal_word_lengths[index] == horizontal_word_lengths[index-1] + 1))
    
        # word lengths are bounded
        self.solver.add(Implies(h_word_end, horizontal_word_lengths[index] >= min_word_length))
        self.solver.add(Implies(h_word_end, horizontal_word_lengths[index] <= max_word_length_horiz))
        self.solver.add(Implies(v_word_end, vertical_word_lengths[index] >= min_word_length))
        self.solver.add(Implies(v_word_end, vertical_word_lengths[index] <= max_word_length_vert))
    
    black_square_pb_tuple =tuple( ( (Not(self.squares[index]), 1) for index in xrange(self.width*self.height)))
    self.solver.add(PbGe(black_square_pb_tuple, min_num_black_squares))
    self.solver.add(PbLe(black_square_pb_tuple, max_num_black_squares))
    
    #symmetry constraints, TODO: this might be faster if we just kept half of the self.squares
    for row in xrange(self.height):
      for col in xrange(self.width):
        index = row*self.width+col
        symm_index = (self.height-row-1)*self.width+(self.width-col-1)
        self.solver.add(Implies(self.squares[index],self.squares[symm_index]))
        self.solver.add(Implies(Not(self.squares[index]),Not(self.squares[symm_index])))
    
    distances = GenerateReachability(self.width, self.height, self.solver, self.squares)
    
    #TODO: from a software point of view all of the word size counters should probably be unified, there is lots of copy/paste!
    
    def addHorizWordSizeConstraint(name, size, target):
      #set up counters
      word_size_counter = IntVector(name, self.width*self.height)
      self.solver.add(word_size_counter[0] == 0)
      for row in xrange(self.height):
        for col in xrange(self.width):
          index = row*self.width+col
          if(index==0): continue
          self.solver.add(Implies(Not(self.squares[index]), word_size_counter[index] == word_size_counter[index-1]))
          if(col == self.width-1): word_terminating = True
          else: word_terminating = And(self.squares[index], Not(self.squares[index+1]))
          # word-terminating 
          self.solver.add(Implies(And(word_terminating, horizontal_word_lengths[index] == size), word_size_counter[index] == word_size_counter[index-1] + 1))
          self.solver.add(Implies(And(word_terminating, horizontal_word_lengths[index] != size), word_size_counter[index] == word_size_counter[index-1]))
          # non-word-terminating self.squares just pass the counter value forward
          self.solver.add(Implies(Not(word_terminating), word_size_counter[index] == word_size_counter[index-1]))
      self.solver.add(word_size_counter[self.width*self.height - 1] == target)
      return word_size_counter
    
    def addVertWordSizeConstraint(name, size, target):
      #set up counters
      word_size_counter = IntVector(name, self.width*self.height)
      self.solver.add(word_size_counter[0] == 0)
      for row in xrange(self.height):
        for col in xrange(self.width):
          index = row*self.width+col
          if(index==0): continue
          self.solver.add(Implies(Not(self.squares[index]), word_size_counter[index] == word_size_counter[index-1]))
          if(row == self.height-1): word_terminating = True
          else: word_terminating = And(self.squares[index], Not(self.squares[index+self.width]))
          # word-terminating 
          self.solver.add(Implies(And(word_terminating, vertical_word_lengths[index] == size), word_size_counter[index] == word_size_counter[index-1] + 1))
          self.solver.add(Implies(And(word_terminating, vertical_word_lengths[index] != size), word_size_counter[index] == word_size_counter[index-1]))
          # non-word-terminating self.squares just pass the counter value forward
          self.solver.add(Implies(Not(word_terminating), word_size_counter[index] == word_size_counter[index-1]))
      self.solver.add(word_size_counter[self.width*self.height - 1] == target)
      return word_size_counter
    
    for (length, num) in themes:
      addHorizWordSizeConstraint(("theme-clue-length-%d")%length ,  length, num)
    
    #No cheaters.
    #The way cruciverb writes this is: "cheater" black self.squares (ones that do not affect the number of words in the puzzle...) are bad
    #This is a simple-to-implement constraint: black self.squares should have at most 2 neighboring black self.squares
    #Another possibility is to use a 'counter' like above and, instead of outright banning these, just make there be a few.
    for row in xrange(self.height):
      for col in xrange(self.width):
        index = row*self.width+col
        left_neighbor_index = index-1
        right_neighbor_index = index+1
        up_neighbor_index = index-self.width
        down_neighbor_index = index+self.width
        up = False if row==0 else self.squares[up_neighbor_index]
        left = False if col==0 else self.squares[left_neighbor_index]
        down = False if row==self.height-1 else self.squares[down_neighbor_index]
        right = False if col==self.width-1 else self.squares[right_neighbor_index]
        self.solver.add(Implies(Not(self.squares[index]), Or(up, left)))
        self.solver.add(Implies(Not(self.squares[index]), Or(up, right)))
        self.solver.add(Implies(Not(self.squares[index]), Or(down, left)))
        self.solver.add(Implies(Not(self.squares[index]), Or(down, right)))
    
    # todo: add this to the inputs to this function
    """
    # helpful to add constraints to encourage the solver to make traditional-looking blocks by fixing the top and left.
    top_blocks = [True]*5 + [False] + [True]*4 + [False] + [True]*5
    left_blocks = [True]*3 + [False] + [True]*3 + [False] + [True]*3 + [False] + [True]*3
    
    for col in xrange(self.width):
      solver.add(self.squares[col] == top_blocks[col])
    for row in xrange(self.height):
      solver.add(self.squares[row*self.width] == left_blocks[row])
    """
  
  
  def Board(self):
    if self.solver.check() != sat: return ""
    self.model = self.solver.model()
    board = []
    for row in xrange(self.height):
      for col in xrange(self.width):
        index = row*self.width + col
        if(self.model[self.squares[index]]): board.append(unichr(0x2219))
        else: board.append(unichr(0x2588))
      board.append("\n")
    return "".join(board)
  
  def Another(self):
    new_soln_constraints = []
    for row in xrange(self.height):
      for col in xrange(self.width):
        index = row*self.width+col
        new_soln_constraints.append(self.squares[index] != self.model[self.squares[index]])
    self.solver.add(Or(new_soln_constraints))

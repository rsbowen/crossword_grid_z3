import __builtin__
__builtin__.Z3_LIB_DIRS = ['../z3/install/lib/']

from z3 import *
import time

width = 15;
height = 15;

def wordify(w):
  return "".join([c for c in w.upper() if ord(c) >= ord('A') and ord(c) <= ord('Z')]) 
# returns a giant disjunct of conjuncts)
def IsValidWord(word_variables, words_by_length):
  filtered_words = words_by_length[len(word_variables)]
  word_predicates = []
  for w in filtered_words:
    letter_predicates = [(variable == ord(letter)-ord('A')) for (variable, letter) in zip(word_variables, w)]
    word_predicates.append(And(letter_predicates))
  big_disjunct = Or(word_predicates)
  return big_disjunct

class GridFiller:
  def __init__(self, dpath, grid, themes):
    lines = file(dpath).readlines()
    words = [wordify(line) for line in lines]
    print(("%d words")%len(words))
    print(("word 1000 is %s")%(words[1000]))

    words_by_length = {}
    for word_length in range(1,1+max(width,height)):
      print ("Filtering words of length %d"%word_length)
      words_by_length[word_length] = [w for w in words if len(w) == word_length]
  
    # create an IntVector for each. First, need an index array.
    next_idx = 0
    self.indices = [[-1 for c in range(width)] for r in range(height)]
    for (rowindex, row) in enumerate(grid):
      for (colindex, cell) in enumerate(row):
        if cell == '#': continue
        self.indices[rowindex][colindex] = next_idx
        next_idx += 1
    
    
    self.solver = Solver()
    self.variables = IntVector('letters', next_idx)
    for i in range(next_idx):
      # there are 26 letters.
      self.solver.add(0 <= self.variables[i])
      self.solver.add(self.variables[i] < 26)
    
    horizontal_word_vars_by_length = {}
    for i in range(1, max(width,height)+1):
      horizontal_word_vars_by_length[i] = []
    
    for row in range(height):
      for col in range(width):
        if(grid[row][col] == '#'): continue
        # find horizontal words
        if col == 0 or grid[row][col-1] == '#':
          word_variables = [];
          stop_col = col #stop_col will be the first col NOT in the word
          while stop_col < width and grid[row][stop_col] != '#':
            word_variables.append(self.variables[self.indices[row][stop_col]])
            stop_col += 1
          print(("horizontal word start at (%d, %d) with last col %d"%(row, col, stop_col)))
          horizontal_word_vars_by_length[len(word_variables)].append(word_variables)
          self.solver.add(IsValidWord(word_variables, words_by_length))
        # find vertical words
        if row == 0 or grid[row-1][col] == '#':
          word_variables = [];
          stop_row = row #stop_row will be the first row NOT in the word
          while stop_row < height and grid[stop_row][col] != '#':
            word_variables.append(self.variables[self.indices[stop_row][col]])
            stop_row += 1
          print(("vertical word start at (%d, %d) with last row %d"%(row, col, stop_row)))
          self.solver.add(IsValidWord(word_variables, words_by_length))
  
    for t in themes:
      word_constraints = []
      for w in horizontal_word_vars_by_length[len(t)]:
        word_constraints.append(And([variable == ord(letter)-ord('A') for (variable,letter) in zip(w,t)]))
      self.solver.add(Or(word_constraints))
  

  def Board(self):
    print "Solving constraints..."
    if self.solver.check() != sat:
      return ""
    self.model = self.solver.model()
    
    # construct the board as a string
    filled_grid = [['#' for c in range(width)] for r in range(height)]

    for row in range(height):
      for col in range(width):
        if self.indices[row][col] == -1 : continue
        filled_grid[row][col] = chr(ord('A') + self.model[self.variables[self.indices[row][col]]].as_long())
    
    return "\n".join(["".join(fillrow) for fillrow in filled_grid])

  def Another(self):
    new_grid_disjunct = []
    for v in self.variables:
      new_grid_disjunct.append(v != self.model[v])
    self.solver.add(Or(new_grid_disjunct))

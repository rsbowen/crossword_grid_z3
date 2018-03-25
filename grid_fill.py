
import __builtin__
__builtin__.Z3_LIB_DIRS = ['../z3/install/lib/']

from z3 import *
import time


width = 15;
height = 15;

def wordify(w):
  return "".join([c for c in w.upper() if ord(c) >= ord('A') and ord(c) <= ord('Z')])

dpath = "/Users/richard/qxw/qxw-20140331/UKACD18plus.txt"
lines = file(dpath).readlines()
words = [wordify(line) for line in lines]
print(("%d words")%len(words))
print(("word 1000 is %s")%(words[1000]))

words_by_length = {}
for word_length in range(1,1+max(width,height)):
  print ("Filtering words of length %d"%word_length)
  words_by_length[word_length] = [w for w in words if len(w) == word_length]

grid = [
[' ',' ',' ',' ','#',' ',' ',' ',' ',' ','#',' ',' ',' ',' '],
[' ',' ',' ',' ','#',' ',' ',' ',' ',' ','#',' ',' ',' ',' '],
[' ',' ',' ',' ','#',' ',' ',' ',' ',' ','#',' ',' ',' ',' '],
['#','#','#',' ',' ',' ',' ','#',' ',' ',' ',' ','#','#','#'],
[' ',' ',' ',' ',' ','#',' ',' ',' ','#',' ',' ',' ',' ',' '],
[' ',' ',' ','#',' ',' ',' ',' ',' ',' ',' ','#',' ',' ',' '],
[' ',' ',' ',' ',' ',' ','#',' ',' ',' ','#',' ',' ',' ',' '],
['#','#','#',' ',' ',' ','#','#','#',' ',' ',' ','#','#','#'],
[' ',' ',' ',' ','#',' ',' ',' ','#',' ',' ',' ',' ',' ',' '], 
[' ',' ',' ','#',' ',' ',' ',' ',' ',' ',' ','#',' ',' ',' '],
[' ',' ',' ',' ',' ','#',' ',' ',' ','#',' ',' ',' ',' ',' '],
['#','#','#',' ',' ',' ',' ','#',' ',' ',' ',' ','#','#','#'],
[' ',' ',' ',' ','#',' ',' ',' ',' ',' ','#',' ',' ',' ',' '],
[' ',' ',' ',' ','#',' ',' ',' ',' ',' ','#',' ',' ',' ',' '],
[' ',' ',' ',' ','#',' ',' ',' ',' ',' ','#',' ',' ',' ',' ']]

# create an IntVector for each. First, need an index array.
next_idx = 0
indices = [[-1 for c in range(width)] for r in range(height)]
for (rowindex, row) in enumerate(grid):
  for (colindex, cell) in enumerate(row):
    if cell == '#': continue
    indices[rowindex][colindex] = next_idx
    next_idx += 1

# returns a giant disjunct of conjuncts)
def IsValidWord(word_variables):
  filtered_words = words_by_length[len(word_variables)]
  word_predicates = []
  for w in filtered_words:
    letter_predicates = [(variable == ord(letter)-ord('A')) for (variable, letter) in zip(word_variables, w)]
    word_predicates.append(And(letter_predicates))
  big_disjunct = Or(word_predicates)
  #print big_disjunct
  return big_disjunct

solver = Solver()
variables = IntVector('letters', next_idx)
for i in range(next_idx):
  # there are 26 letters.
  solver.add(0 <= variables[i])
  solver.add(variables[i] < 26)

for row in range(height):
  for col in range(width):
    if(grid[row][col] == '#'): continue
    # find horizontal words
    if col == 0 or grid[row][col-1] == '#':
      word_variables = [];
      stop_col = col #stop_col will be the first col NOT in the word
      while stop_col < width and grid[row][stop_col] != '#':
        word_variables.append(variables[indices[row][stop_col]])
        stop_col += 1
      print(("horizontal word start at (%d, %d) with last col %d"%(row, col, stop_col)))
      solver.add(IsValidWord(word_variables))
    # find vertical words
    if row == 0 or grid[row-1][col] == '#':
      word_variables = [];
      stop_row = row #stop_row will be the first row NOT in the word
      while stop_row < height and grid[stop_row][col] != '#':
        word_variables.append(variables[indices[stop_row][col]])
        stop_row += 1
      print(("vertical word start at (%d, %d) with last row %d"%(row, col, stop_row)))
      solver.add(IsValidWord(word_variables))

print "Solving constraints..."
print solver.check()

# print the board.
# todo: check on the satisfiability before trying to print
filled_grid = [['#' for c in range(width)] for r in range(height)]

m=solver.model()
for row in range(height):
  for col in range(width):
    if indices[row][col] == -1 : continue
    filled_grid[row][col] = chr(ord('A') + m[variables[indices[row][col]]].as_long())

for fillrow in filled_grid:
  print("".join(fillrow))

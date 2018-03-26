from grid_fill import GridFiller 

dpath = "/Users/richard/qxw/qxw-20140331/UKACD18plus.txt"
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

themes = ["CORSAIR","SAIL"]

F = GridFiller(dpath, grid, themes)
s = F.Board()
while s is not None:
  print s
  F.Another()
  s = F.Board()

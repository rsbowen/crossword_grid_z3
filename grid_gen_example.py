from grid_gen import GridGenerator

width = 15  
height = 15

max_num_black_squares = 40
min_num_black_squares = 0
  
min_word_length = 3
max_word_length_vert = 6
max_word_length_horiz = 9
  
G = GridGenerator(width, height, max_num_black_squares, min_num_black_squares, min_word_length, max_word_length_vert, max_word_length_horiz, [(7,2),(8,2),(9,2)])

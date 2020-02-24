class MazeError(Exception):
  def __init__(self,message):
    super().__init__(message)

class Maze:
  def __init__(self, filename):
    self.name = filename.split('.')[0]
    self.wall_grid = self.parse(filename)
    self.row_count = len(self.wall_grid) - 1
    self.col_count = len(self.wall_grid[0]) - 1
    self.cell_grid = [[' ' for c in range(self.col_count)] for r in range(self.row_count)]
    self.n_inaccessible_pts = 0
    self.n_accessible_areas = 0
    self.n_cont_cds = 0
    self.n_oneway_paths = 0
    self.traverse_maze()

  def parse(self, filename):
    maze_code = open(filename) 
    content = maze_code.readlines()
    grid = []
    for line in content:
      line = ''.join(line.split())
      if not line:
        continue
      if any(c not in {'0','1','2','3'} for c in line):
        raise MazeError('Incorrect input.')
      code_line = [int(c) for c in line]
      grid.append(code_line)
    if len(grid) < 2 or len(grid) > 41:
      raise MazeError('Incorrect input.')
    c = len(grid[0])
    if c < 2 or c > 31 or any(len(r) != c for r in grid[1:]):
      raise MazeError('Incorrect input.')
    maze_code.close()
    self.validate(grid)
    return grid

  def validate(self, grid):
    if any(r[-1] in {1,3} for r in grid)\
      or any(c in {2,3} for c in grid[-1]):
      raise MazeError('Input does not represent a maze.')

  def analyse(self):
    self.view_result(len(self.gates), self.count_cont_walls(), self.n_inaccessible_pts,\
                    self.n_accessible_areas, self.n_cont_cds, self.n_oneway_paths)

  def traverse_maze(self):
    def visit_all_from(cell):
      c = enter_from(cell)
      stack, paths, visited_cells, diff_gates = [c], [], {cell, c}, {cell}
      while stack:
        if stack[-1] in self.gates:
          g = stack.pop()
          visited_cells.add(g)
          diff_gates.add(g)
          paths.append(stack.copy())
        else:
          p = move(stack[-1],visited_cells)
          if not p:
            stack.pop()
          else:
            visited_cells.add(p)
            stack.append(p)
      visited_cells -= diff_gates
      diff_gates.discard(cell)
      return diff_gates, visited_cells, paths
    
    def enter_from(cell):
      if cell[0] == -1:
        return (0,cell[1])
      elif cell[0] == self.row_count:
        return (self.row_count-1,cell[1])
      elif cell[1] == -1:
        return (cell[0],0)
      elif cell[1] == self.col_count:
        return (cell[0],self.col_count-1)
        
    def move(pos,visited):
      x, y = pos[0], pos[1]
      if not self.horizontal_walls[x][y] and (x-1, y) not in visited:
        return (x-1, y)
      if not self.vertical_walls[x][y] and (x, y-1) not in visited:
        return (x, y-1)
      if not self.horizontal_walls[x+1][y] and (x+1, y) not in visited:
        return (x+1, y)
      if not self.vertical_walls[x][y+1] and (x, y+1) not in visited:
        return (x, y+1)
      return 0

    def complete_search(set_path, set_cds):
      verified_cds, found_path = set(), False
      while set_cds:
        p, vp = 0, 0
        for c in set_cds:
          vp = move(c, set_cds)
          if vp: # a cell connected the verified paths
            p = c
            break
        stack, visited, flag_connected_cds = [p], {p, vp}, True
        while stack:
          p = stack[-1]
          q = move(p, visited)
          if not q:
            stack.pop()
          elif q in set_path:
            set_path |= set(stack)
            set_cds -= set(stack)
            flag_connected_cds = False
            found_path = True
            break
          else:
            stack.append(q)
            visited.add(q)
        if flag_connected_cds:
          self.n_cont_cds += 1
          visited.discard(vp)
          set_cds -= visited
          verified_cds |= visited
      return verified_cds, found_path
    # form walls
    self.vertical_walls = [[self.wall_grid[r][c] in {2,3} for c in range(self.col_count+1)]\
                           for r in range(self.row_count)]
    self.horizontal_walls = [[self.wall_grid[r][c] in {1,3} for c in range(self.col_count)]\
                             for r in range(self.row_count+1)]
    # detecting gates
    upper_gates = set(filter(lambda i:not self.horizontal_walls[0][i],range(self.col_count)))
    lower_gates = set(filter(lambda i:not self.horizontal_walls[-1][i],range(self.col_count)))
    left_gates = set(filter(lambda i:not self.vertical_walls[i][0],range(self.row_count)))
    right_gates = set(filter(lambda i:not self.vertical_walls[i][-1],range(self.row_count)))
    
    self.gates = {(-1,i) for i in upper_gates}\
                  .union({(self.row_count,i) for i in lower_gates})\
                  .union({(i,-1) for i in left_gates})\
                  .union({(i,self.col_count) for i in right_gates})
    unvisited_gates = self.gates.copy()
    # explore maze
    while unvisited_gates:
      start_cell = unvisited_gates.pop()
      connected_gates, cells, set_of_paths = visit_all_from(start_cell)
      self.n_accessible_areas += 1
      if not connected_gates:
        self.n_cont_cds += 1
        for c in cells:
          self.cell_grid[c[0]][c[1]] = 'x'
      else:
        unvisited_gates -= connected_gates
        non_cds = set()
        for p in set_of_paths:
          non_cds |= set(p)
        cell_cds = cells - non_cds
        cell_cds, hidden_path_flag = complete_search(non_cds, cell_cds)
        if len(set_of_paths) == 1 and not hidden_path_flag:
          self.n_oneway_paths += 1
          for c in non_cds:
            self.cell_grid[c[0]][c[1]] = '-'
        else:
          for c in non_cds:
            self.cell_grid[c[0]][c[1]] = '.'
        for c in cell_cds:
          self.cell_grid[c[0]][c[1]] = 'x'
    self.n_inaccessible_pts = sum(sum(c==' ' for c in r) for r in self.cell_grid)
    
  def count_cont_walls(self):
    res, visited = 0, set()
    for i in range(self.row_count+1):
      for j in range(self.col_count+1):
        if (i,j) not in visited and self.wall_grid[i][j]:
          res += 1
          stack = [(i,j)]
          visited.add((i,j))
          while stack:
            node = stack[-1]
            c = self.wall_grid[node[0]][node[1]]
            if c in {1,3} and (node[0],node[1]+1) not in visited: 
              stack.append((node[0],node[1]+1)) # right
              visited.add((node[0],node[1]+1))
            elif c in {2,3} and (node[0]+1,node[1]) not in visited:
              stack.append((node[0]+1,node[1])) # down
              visited.add((node[0]+1,node[1]))
            elif node[1]>0 and (node[0],node[1]-1) not in visited and\
             (self.wall_grid[node[0]][node[1]-1]==1 or self.wall_grid[node[0]][node[1]-1]==3):
             stack.append((node[0],node[1]-1)) # left
             visited.add((node[0],node[1]-1))
            elif node[0]>0 and (node[0]-1,node[1]) not in visited and\
             (self.wall_grid[node[0]-1][node[1]]==2 or self.wall_grid[node[0]-1][node[1]]==3):
             stack.append((node[0]-1,node[1])) # up
             visited.add((node[0]-1,node[1]))
            else:
              stack.pop()
    return res
  

  def view_result(self, n1, n2, n3, n4, n5, n6):
    if not n1:
      print('The maze has no gate.')
    elif n1 == 1:
      print('The maze has a single gate.')
    else:
      print('The maze has', n1, 'gates.')
    if not n2:
      print('The maze has no wall.')
    elif n2 == 1:
      print('The maze has walls that are all connected.')
    else:
      print('The maze has', n2, 'sets of walls that are all connected.')
    if not n3:
      print('The maze has no inaccessible inner point.')
    elif n3 == 1:
      print('The maze has a unique inaccessible inner point.')
    else:
      print('The maze has', n3, 'inaccessible inner points.')
    if not n4:
      print('The maze has no accessible area.')
    elif n4 == 1:
      print('The maze has a unique accessible area.')
    else:
      print('The maze has', n4, 'accessible areas.')
    if not n5:
      print('The maze has no accessible cul-de-sac.')
    elif n5 == 1:
      print('The maze has accessible cul-de-sacs that are all connected.')
    else:
      print('The maze has', n5, 'sets of accessible cul-de-sacs that are all connected.')
    if not n6:
      print('The maze has no entry-exit path with no intersection not to cul-de-sacs.')
    elif n6 == 1:
      print('The maze has a unique entry-exit path with no intersection not to cul-de-sacs.')
    else:
      print('The maze has', n6, 'entry-exit paths with no intersection not to cul-de-sacs.')

  def display(self):
    f= open(self.name + ".tex","w",newline='\n')
    f.write('\\documentclass[10pt]{article}\n')
    f.write('\\usepackage{tikz}\n')
    f.write('\\usetikzlibrary{shapes.misc}\n')
    f.write('\\usepackage[margin=0cm]{geometry}\n')
    f.write('\\pagestyle{empty}\n')
    f.write('\\tikzstyle{every node}=[cross out, draw, red]\n\n')
    f.write('\\begin{document}\n\n')
    f.write('\\vspace*{\\fill}\n')
    f.write('\\begin{center}\n')
    f.write('\\begin{tikzpicture}[x=0.5cm, y=-0.5cm, ultra thick, blue]\n')
    f.write('% Walls\n')
    for r in range(self.row_count+1):
      s = 0
      while True:
        while s < self.col_count and not self.horizontal_walls[r][s]:
          s += 1
        if s >= self.col_count:
          break
        t = s + 1
        while t < self.col_count and self.horizontal_walls[r][t]:
          t += 1
        f.write('    \\draw (' + str(s) + ',' + str(r) +') -- ('+ str(t) + ',' + str(r) +');\n')
        s = t+1

    for c in range(self.col_count+1):
      s = 0
      while True:
        while s < self.row_count and not self.vertical_walls[s][c]:
          s += 1
        if s >= self.row_count:
          break
        t = s + 1
        while t < self.row_count and self.vertical_walls[t][c]:
          t += 1
        f.write('    \\draw (' + str(c) + ',' + str(s) +') -- ('+ str(c) + ',' + str(t) +');\n')
        s = t+1
    f.write('% Pillars\n')
    for r in range(self.row_count+1):
      for c in range(self.col_count+1):
        if not self.wall_grid[r][c] and (r==0 or not self.vertical_walls[r-1][c])\
        and (c==0 or not self.horizontal_walls[r][c-1]):
          f.write('    \\fill[green] (' + str(c) + ',' + str(r) +') circle(0.2);\n')
    f.write('% Inner points in accessible cul-de-sacs\n')
    for r in range(self.row_count):
      for c in range(self.col_count):
        if self.cell_grid[r][c] == 'x':
          f.write('    \\node at (' + str(c+0.5) + ',' + str(r+0.5) +') {};\n')
    f.write('% Entry-exit paths without intersections\n')
    for r in range(self.row_count):
      s = 0
      while True:
        while s < self.col_count and self.cell_grid[r][s] != '-':
          s += 1
        if s >= self.col_count:
          break
        t = s
        while t+1 < self.col_count and self.cell_grid[r][t+1] == '-'\
              and not self.vertical_walls[r][t+1]:
          t += 1
        if (r, s-1) in self.gates:
          s = s - 1
        if (r, t+1) in self.gates:
          t = t + 1
        if s < t:
          f.write('    \\draw[dashed, yellow] (' + str(s+0.5) + ',' + str(r+0.5)\
                  +') -- ('+ str(t+0.5) + ',' + str(r+0.5) +');\n')
        s = t + 1
    for c in range(self.col_count):
      s = 0
      while True:
        while s < self.row_count and self.cell_grid[s][c] != '-':
          s += 1
        if s >= self.row_count:
          break
        t = s
        while t+1 < self.row_count and self.cell_grid[t+1][c] == '-'\
              and not self.horizontal_walls[t+1][c]:
          t += 1
        if (s-1, c) in self.gates:
          s = s - 1
        if (t+1, c) in self.gates:
          t = t + 1
        if s < t:
          f.write('    \\draw[dashed, yellow] (' + str(c+0.5) + ',' + str(s+0.5)\
                  +') -- ('+ str(c+0.5) + ',' + str(t+0.5) +');\n')
        s = t+1
    f.write('\\end{tikzpicture}\n')
    f.write('\\end{center}\n')
    f.write('\\vspace*{\\fill}\n\n')
    f.write('\\end{document}\n')
    f.close()
    
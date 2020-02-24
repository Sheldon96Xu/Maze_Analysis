# Brief
+ Analyse the various characteristics of a maze, represented by a particular coding of its basic constituents into numbers stored in a file whose contents is read, and display those characteristics. 
+ Output some Latex code in a file, from which a pictorial representation of the maze can be produced.

# Input Maze Encoding
The representation of the maze is based on a coding with the four digits 0, 1, 2 and 3 such that
+ 0 codes points that are connected to neither their right nor below neighbours.
+ 1 codes points that are connected to their right neighbours but not to their below ones.
+ 2 codes points that are connected to their below neighbours but not to their right ones.
+ 3 codes points that are connected to both their right and below neighbours.

# Keywords Definitions
+ A point that is connected to none of their left, right, above and below neighbours represents a pillar.
+ A gate is any pair of consecutive points on one of the four sides of the maze that are not connected. 
+ An inaccessible inner point is an inner point that cannot be reached from any gate. 
+ An accessible area is a maximal set of inner points that can all be accessed from the same gate (so the number of accessible inner points is at most equal to the number of gates).
+ A set of accessible cul-de-sacs that are all connected is a maximal set S of connected inner points that can all be accessed from the same gate g and such that for all points p in S, if p has been accessed from g for the first time, then either p is in a dead end or moving on without ever getting back leads into a dead end.
+ An entry-exit path with no intersections not to cul-de-sacs is a maximal set S of connected inner points that go from a gate to another (necessarily different) gate and such that for all points p in S, there is only one way to move on from p without getting back and without entering a cul-de-sac.

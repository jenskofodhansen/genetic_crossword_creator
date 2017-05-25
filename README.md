# genetic_crossword_creator
An attempt to create crossword puzzles using an genetic algortihm

This is just a small hobby project, which for me has the purpose of:
- Learning some Python, namely:
  - Learning about data structures (list, sets, tuples)
  - Learning about data transformation (map, filter, reduce)
- See if it was possible to use genetic algorithms for finding crosswords
- Learning about Python profiling and optimizations

The project can easily be cloned and executed without additional dependencies (I use Python 3.4). I made it using a Danish dictionary (I downloaded and processed the Open Office dictionary, the format is simply one word per line). The allowed letters can be modified your language need.

The state of the project:
At the time being, small crosswords can be generated (around 4x5 characters). There are several optimizations that can be implemented. The bottleneck at the momement is the speed of picking chromosomes by fitness.

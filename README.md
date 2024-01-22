# Pygame Projects
These are some of my projects I made in 2023 using python and the pygame library.

When running, please ensure you are in the relevant project directory, and not the Pygame-Projects root directory.

## Conway's Game of Life
A cellular automana that generates beautiful patterns based on a simple set of rules.
### Optimisation
In order to optimise each iteration of the algorithm, I didn't use a grid of cells, which would have a $n^2$ performance decrease as the grid got larger. Instead, I used a set which stored cell positions, which not only reduced the number of iterations of the formula, but decreased the lookup time for cells.

This allowed for a relatively smooth performance with large numbers of cells even in python, which is a relatively slow language when it comes to iteration.
### Controls
* R to switch between edit and play modes
* Space + drag to move camera
* Scroll wheel to zoom
* Left click to place cells, right click to delete
* Right arrow to step once
* Backspace to delete all cells

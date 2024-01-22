# Pygame Projects
These are some of my projects I made in 2023 using python and the pygame library.

When running, please ensure you are in the relevant project directory, and not the Pygame-Projects root directory.

## Conway's Game of Life
A cellular autonama that generates beautiful patterns based on a simple set of rules.

![image](https://github.com/TheOneThatFlys/Pygame-Projects/assets/110343508/eafb3c00-0048-4f56-ae2d-94b8b0f9d67d)
![image](https://github.com/TheOneThatFlys/Pygame-Projects/assets/110343508/4456baf0-7b52-4696-ba77-d2fd137e5d58)

### Optimisation
This version uses a set of cell positions instead of a 2d array of cells in order decrease cell lookup time and complexity, which also means the grid is an infinite size.

This allowed for a relatively smooth performance with large numbers of cells even in python, which is a relatively slow language when it comes to iteration.
### Controls
* R to switch between edit and play modes
* Space + drag to move camera
* Scroll wheel to zoom
* Left click to place cells, right click to delete
* Right arrow to step once
* Backspace to delete all cells
* F3 for debug info

## Chess
A game of chess, with UI based on chess.com. You play as white and black makes random moves.

Also supports saving a game state (CTRL-S) and loading a game state (CTRL-L).

![image](https://github.com/TheOneThatFlys/Pygame-Projects/assets/110343508/9e9721dc-f755-4099-800a-d5c7e13b4698)

## Roguelike
Not fully completed. Play as a wizard with a gun and shoot infinitely respawning skeletons.

<img src='https://github.com/TheOneThatFlys/Pygame-Projects/assets/110343508/05064c0f-0bd0-4515-aa89-b90e1e618517' width='500'>
<img src='https://github.com/TheOneThatFlys/Pygame-Projects/assets/110343508/7e4bba90-fb71-4e83-92e8-95fdb240a40b' width='500'>

### Controls
* WASD to move
* Mouse to shoot
* 1 and 2 to swap weapons

## Wave Function Collapse
A visualisation of a wave function collapse algorithm generating a circuit board.

Practical applications may be a sudoku solver, or dungeon map generation.

![image](https://github.com/TheOneThatFlys/Pygame-Projects/assets/110343508/a54262ed-1766-47cf-9f07-a971d540e666)

## Grass Cutting Incremental
An incremental style game about cutting grass. Buy upgrades and automations, with offline progress.

![image](https://github.com/TheOneThatFlys/Pygame-Projects/assets/110343508/ad72635d-7316-4de3-b405-2d91f28710bb)





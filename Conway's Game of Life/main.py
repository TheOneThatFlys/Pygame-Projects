import pygame
pygame.init()

FPS = 60
TICK_SPEED = 1

Cell = tuple[int, int]

# totally not stolen
def bresenham(x0, y0, x1, y1):
    dx = x1 - x0
    dy = y1 - y0

    xsign = 1 if dx > 0 else -1
    ysign = 1 if dy > 0 else -1

    dx = abs(dx)
    dy = abs(dy)

    if dx > dy:
        xx, xy, yx, yy = xsign, 0, 0, ysign
    else:
        dx, dy = dy, dx
        xx, xy, yx, yy = 0, ysign, xsign, 0

    D = 2*dy - dx
    y = 0

    for x in range(dx + 1):
        yield x0 + x*xx + y*yx, y0 + x*xy + y*yy
        if D >= 0:
            y += 1
            D -= 2*dx
        D += 2*dy

def get_adjacent_cells(cell: Cell) -> list[Cell]:
    return [(cell[0]+i,cell[1]+j) for i in (-1,0,1) for j in (-1,0,1) if i != 0 or j != 0]

def count_neighbours(cell: Cell, cells: set[Cell]):
    neighbours = 0
    # loop through each index of adjacent cells
    for maybe_cell in get_adjacent_cells(cell):
        # if cell exists
        if maybe_cell in cells:
            neighbours += 1
    return neighbours

class Game():
    def __init__(self, surface):
        self.render_surface = surface
        self.running = False
        self.active_cells: set[Cell] = set()
        self.cell_size = 16
        self.timer = 0

        self.last_pos = None

        self.cam_pos = [0, 0]

        self.init_stress_test()

    def init_stress_test(self, n = 200):
        for i in range(n):
            for j in range(n):
                self.active_cells.add((i, j))

    def count_neighbours(self, cell: Cell) -> int:
        neighbours = 0
        # loop through each index of adjacent cells
        for maybe_cell in self.get_adjacent_cells(cell):
            # if cell exists
            if maybe_cell in self.active_cells:
                neighbours += 1
        return neighbours

    def get_adjacent_cells(self, cell: Cell) -> list[Cell]:
        # magic: https://stackoverflow.com/questions/2373306/pythonic-and-efficient-way-of-finding-adjacent-cells-in-grid
        return [(cell[0]+i,cell[1]+j) for i in (-1,0,1) for j in (-1,0,1) if i != 0 or j != 0]

    def tick(self):
        cells_copy = set()

        neighbours = 0
        checked_neighbours = set()
        for cell in self.active_cells:
            checked_neighbours.add(cell)
            neighbours = self.count_neighbours(cell)

            if neighbours == 2 or neighbours == 3:
                cells_copy.add(cell)

            # if one of neighbours has 3 neighbours, create new
            # check each neighbour
            for neighbour_cell in self.get_adjacent_cells(cell):

                if neighbour_cell in checked_neighbours or neighbour_cell in self.active_cells: continue
                checked_neighbours.add(neighbour_cell)

                if self.count_neighbours(neighbour_cell) == 3:
                    cells_copy.add(neighbour_cell)

        self.active_cells = cells_copy

    def scale_pos_to_index(self, pos) -> tuple[int, int]:
        hx, hy = self.render_surface.get_width() / 2, self.render_surface.get_height() / 2
        # scale position to coordinate system
        index = (
            ((pos[0] - hx) // self.cell_size + int(self.cam_pos[0])),
            ((pos[1] - hy) // self.cell_size + int(self.cam_pos[1]))
        )

        return index

    def get_input(self):
        buttons = pygame.mouse.get_pressed()
        mouse_pos_relative = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()
        mvm = pygame.mouse.get_rel()
        # editor mode
        if not self.running:
            index = self.scale_pos_to_index(mouse_pos_relative)

            is_cell_there = index in self.active_cells
            if buttons[0] and not keys[pygame.K_SPACE]:
                if self.last_pos:
                    for point in bresenham(int(index[0]), int(index[1]), int(self.last_pos[0]), int(self.last_pos[1])):
                        self.active_cells.add(point)
                else:
                    self.active_cells.add(index)
                self.last_pos = index

            elif buttons[2] and is_cell_there:
                self.active_cells.remove(index)

            # if not clicking or moving cam
            if not buttons[0] or keys[pygame.K_SPACE]:
                self.last_pos = None

            # can still move if space
            if buttons[0] and keys[pygame.K_SPACE]:
                self.cam_pos[0] -= mvm[0] / self.cell_size
                self.cam_pos[1] -= mvm[1] / self.cell_size

        # view mode
        else:
            if buttons[0]:
                self.cam_pos[0] -= mvm[0] / self.cell_size
                self.cam_pos[1] -= mvm[1] / self.cell_size

    def on_keydown(self, key):
        if key == pygame.K_r:
            self.running = not self.running
        if key == pygame.K_RIGHT:
            self.tick()
        if key == pygame.K_d:
            self.cam_pos[0] += 1

    def on_mousewheel(self, event):
        mouse_pos = pygame.mouse.get_pos()
        prev_index = self.scale_pos_to_index(mouse_pos)

        self.cell_size += event.y
        if self.cell_size > 32:
            self.cell_size = 32
        if self.cell_size < 1:
            self.cell_size = 1

        new_index = self.scale_pos_to_index(mouse_pos)

        self.cam_pos = [
            self.cam_pos[0] - (new_index[0] - prev_index[0]),
            self.cam_pos[1] - (new_index[1] - prev_index[1])
        ]

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            self.on_keydown(event.key)
        elif event.type == pygame.MOUSEWHEEL:
            self.on_mousewheel(event)

    def update(self):
        if self.running:
            self.timer += 1
            if self.timer >= TICK_SPEED:
                self.tick()
                self.timer = 0

        self.get_input()

    def render(self, surface):
        hx = surface.get_width() / 2
        hy = surface.get_height() / 2

        for x, y in self.active_cells:
            pygame.draw.rect(
                surface,
                (255, 255, 255),
                [(x - int(self.cam_pos[0])) * self.cell_size + hx,
                 (y - int(self.cam_pos[1])) * self.cell_size + hy,
                 self.cell_size, self.cell_size])

class Debug():
    def __init__(self, surface, font, pos, padding):
        self.surface = surface
        self.font = font
        self.pos = pos
        self.padding = padding

        self.enabled = False

    def render(self, texts: list[str]):
        if not self.enabled: return
        surfs = []
        for text in texts:
            s = self.font.render(text, False, (255, 255, 255))
            surfs.append(s)

        last_bottom = self.pos[1]
        for s in surfs:
            r = s.get_rect(left = self.pos[0], top = last_bottom + self.padding)
            self.surface.blit(s, r)
            last_bottom = r.bottom

    def toggle(self):
        self.enabled = not self.enabled

def main():
    window = pygame.display.set_mode((16 * 24, 16 * 24))
    pygame.display.set_caption("LIFE")
    clock = pygame.time.Clock()

    g = Game(window)
    d = Debug(window, pygame.font.Font(None, 16), (5, 5), 5)

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F3:
                    d.toggle()

            g.handle_event(event)

        g.update()

        window.fill((0, 0, 0))
        g.render(window)
        d.render([
            f"FPS: {str(round(clock.get_fps(), 1))}",
            f"COUNT: {str(len(g.active_cells))}",
            f"POS: {str(round(g.cam_pos[0]))}, {str(round(g.cam_pos[1]))}",
        ])
        pygame.display.update()

    pygame.quit()

main()
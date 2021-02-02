import pygame
import math
from queue import PriorityQueue


pygame.display.set_caption("Pathfinding Algorithm")
largeur = 800
WIN = pygame.display.set_mode((largeur, largeur))


# définission les couleurs qu'on pourra utiliser par la suite
gris = (128, 128, 128)
jaune = (255, 255, 0)
TURQUOISE = (64, 224, 208)
noir = (0, 0, 0)
blanc = (255, 255, 255)
bleu = (0, 255, 0)
violet = (128, 0, 128)
vert = (0, 255, 0)
ORANGE = (255, 165, 0)
rouge = (255, 0, 0)
# définissons une classe qui contient les méthodes essentielles


class Spot:
    def __init__(self, rangée, colonne, largeur, total_rangées):
        self.rangée = rangée
        self.colonne = colonne
        self.x = rangée * largeur
        self.y = colonne * largeur
        self.couleur = blanc
        self.voisins = []
        self.largeur = largeur
        self.total_rangées = total_rangées

    def is_open(self):
        return self.couleur == vert

    def is_barrier(self):
        return self.couleur == noir

    def get_pos(self):
        return self.rangée, self.colonne

    def is_start(self):
        return self.couleur == ORANGE

    def is_end(self):
        return self.couleur == TURQUOISE

    def is_closed(self):
        return self.couleur == rouge

    def make_start(self):
        self.couleur = ORANGE

    def make_closed(self):
        self.couleur = rouge

    def make_open(self):
        self.couleur = vert

    def make_barrier(self):
        self.couleur = noir

    def reset(self):
        self.couleur = blanc

    def make_end(self):
        self.couleur = TURQUOISE

    def make_path(self):
        self.couleur = violet

    def draw(self, win):
        pygame.draw.rect(
            win, self.couleur, (self.x, self.y, self.largeur, self.largeur)
        )

    def update_voisins(self, grille):
        self.voisins = []
        if (
            self.rangée < self.total_rangées - 1
            and not grille[self.rangée + 1][self.colonne].is_barrier()
        ):  # DOWN
            self.voisins.append(grille[self.rangée + 1][self.colonne])

        if (
            self.rangée > 0 and not grille[self.rangée - 1][self.colonne].is_barrier()
        ):  # UP
            self.voisins.append(grille[self.rangée - 1][self.colonne])

        if (
            self.colonne < self.total_rangées - 1
            and not grille[self.rangée][self.colonne + 1].is_barrier()
        ):  # RIGHT
            self.voisins.append(grille[self.rangée][self.colonne + 1])

        if (
            self.colonne > 0 and not grille[self.rangée][self.colonne - 1].is_barrier()
        ):  # LEFT
            self.voisins.append(grille[self.rangée][self.colonne - 1])

    def __lt__(self, other):
        return False


def h(position1, position2):
    x1, y1 = position1
    x2, y2 = position2
    return abs(x1 - x2) + abs(y1 - y2)


def algorithm(draw, grille, start, end):
    count = 0
    op_s = PriorityQueue()
    op_s.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for rangée in grille for spot in rangée}
    g_score[start] = 0
    f_score = {spot: float("inf") for rangée in grille for spot in rangée}
    f_score[start] = h(start.get_pos(), end.get_pos())

    op_s_hash = {start}

    while not op_s.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = op_s.get()[2]
        op_s_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.voisins:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in op_s_hash:
                    count += 1
                    op_s.put((f_score[neighbor], count, neighbor))
                    op_s_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False


def make_grille(rangées, largeur):
    grille = []
    gap = largeur // rangées
    for i in range(rangées):
        grille.append([])
        for j in range(rangées):
            spot = Spot(i, j, gap, rangées)
            grille[i].append(spot)

    return grille


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


def draw_grille(win, rangées, largeur):
    gap = largeur // rangées
    for i in range(rangées):
        pygame.draw.line(win, gris, (0, i * gap), (largeur, i * gap))
        for j in range(rangées):
            pygame.draw.line(win, gris, (j * gap, 0), (j * gap, largeur))


def draw(win, grille, rangées, largeur):
    win.fill(blanc)

    for rangée in grille:
        for spot in rangée:
            spot.draw(win)

    draw_grille(win, rangées, largeur)
    pygame.display.update()


def get_clicked_pos(pos, rangées, largeur):
    gap = largeur // rangées
    y, x = pos

    rangée = y // gap
    colonne = x // gap

    return rangée, colonne


def main(win, largeur):
    rangéeS = 50

    grille = make_grille(rangéeS, largeur)

    start = None
    end = None

    run = True
    while run:
        draw(win, grille, rangéeS, largeur)
        for event in pygame.event.get():

            if pygame.mouse.get_pressed()[0]:  # LEFT
                pos = pygame.mouse.get_pos()
                rangée, colonne = get_clicked_pos(pos, rangéeS, largeur)
                spot = grille[rangée][colonne]
                if not start and spot != end:
                    start = spot
                    start.make_start()

                elif not end and spot != start:
                    end = spot
                    end.make_end()

                elif spot != end and spot != start:
                    spot.make_barrier()

            if event.type == pygame.QUIT:
                run = False

            elif pygame.mouse.get_pressed()[2]:  # RIGHT
                pos = pygame.mouse.get_pos()
                rangée, colonne = get_clicked_pos(pos, rangéeS, largeur)
                spot = grille[rangée][colonne]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grille = make_grille(rangéeS, largeur)
                if event.key == pygame.K_SPACE and start and end:
                    for rangée in grille:
                        for spot in rangée:
                            spot.update_voisins(grille)

                    algorithm(
                        lambda: draw(win, grille, rangéeS, largeur), grille, start, end
                    )

    pygame.quit()


main(WIN, largeur)
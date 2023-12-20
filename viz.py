import argparse
import pygame
import sys
import math

from scipy.spatial.transform import Rotation
import numpy as np

def status(screen, msg="", height=16):
    font_obj=pygame.font.Font('c:\\windows\\fonts\\Arial.ttf',height-2)
    text_obj=font_obj.render(msg,True,"white")
    textsz = text_obj.get_rect()
    screen.blit(text_obj, (1, screen.get_height()-height+1))

# Helper class for a sub-screen that encapsulates drawing the surface and the border around it
class Viewport:
    def __init__(self, w, h, x, y, border=1):
        self.w = w-(border*2)
        self.h = h-(border*2)
        self.x = x
        self.y = y
        self.border = border

        self.surface = pygame.Surface((w,h))

    def surface(self):
        return self.surface


    def get_width(self):
        return self.w

    def get_height(self):
        return self.h

    def blit(self, surf):
        surf.blit(self.surface, (self.x+self.border,self.y+self.border))
        pygame.draw.rect(surf, "white", (self.x,self.y,self.w,self.h), self.border)

class obj3:
    def __init__(self, points=[], edges=[]):
        self.dim = 3
        self.reset_points = points
        self.reset_edges = edges
        self.reset()

    def reset(self):
        self.points = self.reset_points
        self.edges = self.reset_edges

    def rotate(self, a=0, b=0, c=0, degrees=True):
        if degrees:
            a = a*(math.pi/180)
            b = b*(math.pi/180)
            c = c*(math.pi/180)

        rotation_x = [[1, 0, 0],
                      [0, math.cos(a), -math.sin(a)],
                      [0, math.sin(a), math.cos(a)]]

        rotation_y = [[math.cos(b), 0, -math.sin(b)],
                      [0, 1, 0],
                      [math.sin(b), 0, math.cos(b)]]

        rotation_z = [[math.cos(c), -math.sin(c), 0],
                      [math.sin(c), math.cos(c), 0],
                      [0, 0 ,1]]

        self.points = (self.points * (np.matrix(rotation_x) * np.matrix(rotation_y) * np.matrix(rotation_z))).tolist()

    def translate(self, x=0, y=0, z=0):
        self.points = [[point[0]+x, point[1]+y, point[2]+z] for point in self.points]

    def project(self, surface, x, y, dimx, dimy, dimz=None, dist=500):
        #todo: throw error if dim[xyz] >= self.dim
        if dimz is None:
            for edge in self.edges:
                pygame.draw.line(surface, edge[0],
                    (x + self.points[edge[1]][dimx], y + self.points[edge[1]][dimy]),
                    (x + self.points[edge[2]][dimx], y + self.points[edge[2]][dimy])
                    )
        else:
            for edge in self.edges:
                A = self.points[edge[1]]
                B = self.points[edge[2]]
                dA = dist/(dist+A[dimz])
                dB = dist/(dist+B[dimz])
                # pygame.draw.line(surface, edge[0],
                #     (x + (A[dimx] * ((dist+A[dimz])/A[dimz])), y + (A[dimy] * ((dist+A[dimz])/A[dimz]))),
                #     (x + (B[dimx] * ((dist+B[dimz])/B[dimz])), y + (B[dimy] * ((dist+B[dimz])/B[dimz])))
                #     )
                pygame.draw.line(surface, edge[0],
                    (x + (A[dimx] * dA), y + (A[dimy] * dA)),
                    (x + (B[dimx] * dB), y + (B[dimy] * dB))
                    )

class Cube(obj3):
    def __init__(self, d=1):
        self.dim = 3 #3d shape

        self.d = d
        points = [
            [ d,  d, -d],
            [-d,  d, -d],
            [-d, -d, -d],
            [ d, -d, -d],
            [ d,  d,  d],
            [-d,  d,  d],
            [-d, -d,  d],
            [ d, -d,  d],
            ]
        edges = [
            ["red",   0, 1],
            ["white", 1, 2],
            ["white", 2, 3],
            ["white", 3, 0],
            ["white", 4, 5],
            ["white", 5, 6],
            ["white", 6, 7],
            ["white", 7, 4],
            ["white", 0, 4],
            ["white", 1, 5],
            ["white", 2, 6],
            ["white", 3, 7],
        ]

        super().__init__(points, edges)
'''
class Obj4D:
    def __init__(self, d=1):
        self.dim = 4

        self.d = d
        self.points = [] # TODO

    def from_cube(self, cube: Cube):
        self.points = [pt.extend(0) for pt in cube.points]
        self.edges = cube.edges

    def project(self, surface, x, y, dimx, dimy):
        for edge in self.edges:
            pygame.draw.line(surface, edge[0],
                (x + self.points[edge[1]][dimx], y + self.points[edge[1]][dimy]),
                (x + self.points[edge[2]][dimx], y + self.points[edge[2]][dimy])
                )
'''

def main(args):
    # Start Pygame
    pygame.init()
    pygame.key.set_repeat(50)

    # Setup Screen
    if args.f:
        # Get screen size
        displayinfo = pygame.display.Info()
        size = width, height = displayinfo.current_w, displayinfo.current_h
        screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
    else:
        height = 600
        width = height * 16/9
        size = width, height
        screen = pygame.display.set_mode(size)

    # Initialize various engines
    clock = pygame.time.Clock()
    pygame.font.init()

    cube = Cube(100)

    rot = [0,0,0]
    trans = [0,0,0]
    ortho = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_w and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    trans[1] -= 5
                elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    trans[1] += 5
                elif event.key == pygame.K_a and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    trans[0] -= 5
                elif event.key == pygame.K_d and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    trans[0] += 5
                elif event.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    trans[2] -= 5
                elif event.key == pygame.K_e and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    trans[2] += 5
                elif event.key == pygame.K_w:
                    rot[0] += 5
                elif event.key == pygame.K_s:
                    rot[0] -= 5
                elif event.key == pygame.K_a:
                    rot[1] -= 5
                elif event.key == pygame.K_d:
                    rot[1] += 5
                elif event.key == pygame.K_q:
                    rot[2] -= 5
                elif event.key == pygame.K_e:
                    rot[2] += 5
                elif event.key == pygame.K_o:
                    ortho = not ortho

        # Start with a black screen
        screen.fill("black")

        # Set up a window for drawing
        W = Viewport(width-30, height-30, 15, 15)

        cube.reset()
        cube.rotate(*rot)
        cube.translate(*trans)
        if ortho:
            cube.project(W.surface, W.get_width()/2, W.get_height()/2, 0, 1)
        else:
            cube.project(W.surface, W.get_width()/2, W.get_height()/2, 0, 1, 2, 500)

        W.blit(screen)

        # Update the status bar
        status(screen, f"R{rot} T{trans} {'ortho' if ortho else 'perspective'}")

        # Draw!
        pygame.display.flip()

if __name__ == '__main__':
    # Parse the input arguments
    P = argparse.ArgumentParser(description="4dviz")
    P.add_argument('-f', action='store_true', help="Run fullscreen")
    args = P.parse_args()

    main(args)

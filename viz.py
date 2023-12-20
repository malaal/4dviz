import argparse
import pygame
import sys
import math
from stl import mesh
import numpy as np

FONT = 'c:\\windows\\fonts\\Arial.ttf'
def status(screen, msg="", height=16):
    font_obj=pygame.font.Font(FONT,height-2)
    text_obj=font_obj.render(msg,True,"white")
    textsz = text_obj.get_rect()
    screen.blit(text_obj, (1, screen.get_height()-height+1))

# Helper class for a sub-screen that encapsulates drawing the surface and the border around it
class Viewport:
    def __init__(self, w, h, x, y, border=1, label=""):
        self.w = w-(border*2)
        self.h = h-(border*2)
        self.x = x
        self.y = y
        self.border = border
        self.label = label

        self.surface = pygame.Surface((w,h))

    def surface(self):
        return self.surface

    def get_width(self):
        return self.w

    def get_height(self):
        return self.h

    def blit(self, surf):
        surf.blit(self.surface, (self.x+self.border,self.y+self.border))

        if self.label:
            font_obj=pygame.font.Font(FONT,15)
            text_obj=font_obj.render(self.label,True,"white")
            textsz = text_obj.get_rect()
            surf.blit(text_obj, (self.x + (self.w - textsz[2])/2, self.y + 5))

        pygame.draw.rect(surf, "white", (self.x,self.y,self.w,self.h), self.border)

class obj4:
    def __init__(self, points=[], edges=[]):
        self.dim = 4
        self.reset_points = points
        self.reset_edges = edges
        self.reset()

    def reset(self):
        self.points = self.reset_points
        self.edges = self.reset_edges

    @staticmethod
    def from_3d(obj):
        points = obj.points
        edges = obj.edges

        points = [point+[0] for point in points]

        return obj4(points, edges)

    def rotate(self, xy=0, xz=0, xw=0, yz=0, yw=0, zw=0, degrees=True):
        if degrees:
            xy = xy*(math.pi/180)
            xz = xz*(math.pi/180)
            xw = xw*(math.pi/180)
            yz = yz*(math.pi/180)
            yw = yw*(math.pi/180)
            zw = zw*(math.pi/180)

        rotation4d_xy= [
            [math.cos(xy), -math.sin(xy), 0, 0],
            [math.sin(xy), math.cos(xy), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]]
        rotation4d_xz = [
            [math.cos(xz), 0, -math.sin(xz), 0],
            [0, 1, 0, 0],
            [math.sin(xz), 0, math.cos(xz), 0],
            [0, 0, 0, 1]]
        rotation4d_xw = [
            [math.cos(xw), 0, 0, -math.sin(xw)],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [math.sin(xw), 0, 0, math.cos(xw)]]
        rotation4d_yz = [
            [1, 0, 0, 0],
            [0, math.cos(yz), -math.sin(yz), 0],
            [0, math.sin(yz), math.cos(yz), 0],
            [0, 0, 0, 1]]
        rotation4d_yw = [
            [1, 0, 0, 0],
            [0, math.cos(yw), 0, -math.sin(yw)],
            [0, 0, 1, 0],
            [0, math.sin(yw), 0, math.cos(yw)]]
        rotation4d_zw = [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, math.cos(zw), -math.sin(zw)],
            [0, 0, math.sin(zw), math.cos(zw)]]

        self.points = (self.points *
            np.matrix(rotation4d_xy) * np.matrix(rotation4d_xz) * np.matrix(rotation4d_xw) *
            np.matrix(rotation4d_yz) * np.matrix(rotation4d_yw) * np.matrix(rotation4d_zw)).tolist()

    def translate(self, x=0, y=0, z=0, w=0):
        self.points = [[point[0]+x, point[1]+y, point[2]+z, point[3]+w] for point in self.points]

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
                pygame.draw.line(surface, edge[0],
                    (x + (A[dimx] * dA), y + (A[dimy] * dA)),
                    (x + (B[dimx] * dB), y + (B[dimy] * dB))
                    )

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

class Hypercube(obj4):
    def __init__(self, d=1):
        self.d = d
        points = [
            [-d, -d,  d,  d],
            [ d, -d,  d,  d],
            [ d,  d,  d,  d],
            [-d,  d,  d,  d],
            [-d, -d, -d,  d],
            [ d, -d, -d,  d],
            [ d,  d, -d,  d],
            [-d,  d, -d,  d],
            [-d, -d,  d, -d],
            [ d, -d,  d, -d],
            [ d,  d,  d, -d],
            [-d,  d,  d, -d],
            [-d, -d, -d, -d],
            [ d, -d, -d, -d],
            [ d,  d, -d, -d],
            [-d,  d, -d, -d],
        ]
        edges = []
        for m in range(4):
            edges.append(["red", m, (m+1)%4])
            edges.append(["red", m+4, (m+1)%4 + 4])
            edges.append(["red", m, m+4])

        for m in range(4):
            edges.append(["white", 8+m, 8+(m+1)%4])
            edges.append(["white", 8+m+4, 8+(m+1)%4 + 4])
            edges.append(["white", 8+m, 8+m+4])

        for m in range(8):
            edges.append(["white", m, m+8])

        super().__init__(points, edges)

class Stata(obj3):
    def __init__(self):
        points, edges = self.load()
        super().__init__(points, edges)

    def load(self):
        points = []
        edges = []

        obj = mesh.Mesh.from_file("stata-reduced.stl")
        for pt in obj.points:
            idx = [len(points), len(points)+1, len(points)+2]
            points.append(pt[0:3].tolist())
            points.append(pt[3:6].tolist())
            points.append(pt[6:9].tolist())
            edges.append(["white", idx[0], idx[1]])
            edges.append(["white", idx[1], idx[2]])
            edges.append(["white", idx[2], idx[0]])
        return points, edges
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

    # stata = Stata()
    # cube = Cube(100)
    # rot = [0,0,0]
    # trans = [0,0,0]
    # ortho = False

    # cube=obj4.from_3d(Stata())
    # cube = obj4.from_3d(Cube(100))
    cube = Hypercube(100)
    rot = [0,0,0,0,0,0]
    trans = [0,0,0,0]
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
                elif event.key == pygame.K_r and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    trans[3] -= 5
                elif event.key == pygame.K_f and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    trans[3] -= 5
                elif event.key == pygame.K_q:
                    rot[0] += 5
                elif event.key == pygame.K_a:
                    rot[0] -= 5
                elif event.key == pygame.K_w:
                    rot[1] += 5
                elif event.key == pygame.K_s:
                    rot[1] -= 5
                elif event.key == pygame.K_e:
                    rot[2] += 5
                elif event.key == pygame.K_d:
                    rot[2] -= 5
                elif event.key == pygame.K_r:
                    rot[3] += 5
                elif event.key == pygame.K_f:
                    rot[3] -= 5
                elif event.key == pygame.K_t:
                    rot[4] += 5
                elif event.key == pygame.K_g:
                    rot[4] -= 5
                elif event.key == pygame.K_y:
                    rot[5] += 5
                elif event.key == pygame.K_h:
                    rot[5] -= 5
                elif event.key == pygame.K_o:
                    ortho = not ortho
                elif event.key == pygame.K_p:
                    trans = [0 for t in trans]
                    rot = [0 for r in rot]

        rot = [angle % 360 for angle in rot]

        # Start with a black screen
        screen.fill("black")

        # Set up a window for drawing
        W = Viewport((width-45)/2, height-30, 15, 15, label="XY")
        X = Viewport((width-45)/2, height-30, 30+((width-45)/2), 15, label="XZ")

        cube.reset()
        cube.rotate(*rot)
        cube.translate(*trans)
        if ortho:
            cube.project(W.surface, W.get_width()/2, W.get_height()/2, 0, 1)
            cube.project(X.surface, W.get_width()/2, W.get_height()/2, 0, 3)
        else:
            cube.project(W.surface, W.get_width()/2, W.get_height()/2, 0, 1, 2, 500)
            cube.project(X.surface, W.get_width()/2, W.get_height()/2, 1, 2, 3, 500)

        # stata.reset()
        # stata.rotate(*rot)
        # stata.translate(*trans)
        # if ortho:
        #  stata.project(W.surface, W.get_width()/2, W.get_height()/2, 0, 1)
        # else:
        #  stata.project(W.surface, W.get_width()/2, W.get_height()/2, 0, 1, 2, 500)

        W.blit(screen)
        X.blit(screen)

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

import math

import pygame
from pygame.locals import *
import numpy as np

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpMat import OpMat
from Robot import Robot
from Box import Box
from OpenGL.GLUT import *

# necesario para julia
import requests

URL_BASE = "http://localhost:8000"
r = requests.post(URL_BASE+ "/simulations", allow_redirects=False)
datos = r.json()
# datos se vuelve una lista con los datos de nuestros robots
print(datos)
LOCATION = datos["Location"]
# initialX = datos["agents"][0]["pos"][0]
# initialY = datos["agents"][0]["pos"][1]



pygame.init()
#opera es la matriz de todo el programa, una sola para todos los robots
opera = OpMat()
# t1 = Robot(opera)
# t2 = Robot(opera)
#Se crea la lista que contendra todos los robots
robots = []
boxes = []

for i in range(5):
    robots.append(Robot(opera))

for i in range(5,len(datos["agents"])):
    boxes.append(Box(opera))


box_render = Box(opera)

screen_width = 600
screen_height = 600

# Variables para dibujar los ejes del sistema
X_MIN = -500
X_MAX = 500
Y_MIN = -500
Y_MAX = 500

def Axis():
    glShadeModel(GL_FLAT)
    glLineWidth(3.0)
    # X axis in red
    glColor3f(1.0, 0.0, 0.0)
    glBegin(GL_LINES)
    glVertex2f(X_MIN, 0.0)
    glVertex2f(X_MAX, 0.0)
    glEnd()
    # Y axis in green
    glColor3f(0.0, 1.0, 0.0)
    glBegin(GL_LINES)
    glVertex2f(0.0, Y_MIN)
    glVertex2f(0.0, Y_MAX)
    glEnd()
    glLineWidth(1.0)

#Cauantas cajas hay al prnicipio
cantidad_de_cajas = len(datos["agents"]) - 6
#variables de control
deg = 1.57
deltaDeg = 0
degrot = 0
scale = 3
def display():
    global deg
    global deg1
    global degrot
    global delta_degrot
    glClear(GL_COLOR_BUFFER_BIT)
    Axis()
    response = requests.get(URL_BASE + LOCATION)
    opera.push()
    datos = response.json()
    # response = requests.get(URL_BASE + LOCATION)

    # Debugging step: print the raw response content
    # print(response.content)

    try:
        datos = response.json()
    except requests.exceptions.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return




    #empezaran viendo hacia la derecha porque su ruta sera
    # a la derecha
    opera.rotation(0)
    #se escalana a 5

    opera.scale(scale*5,scale*5)



    #todos las cajas, excepto el estante
    for i in range(5, len(datos["agents"]) - 1):
        #boxes es la lista con objetos box
        b = boxes[i-5]
        opera.push()
        #box julia es el agente de julia
        box_julia = datos["agents"][i]
        opera.translation((box_julia["pos"][1] - 1) * scale,(box_julia["pos"][0] - 1 ) * scale)
        b.render()
        opera.pop()


    for i in range(5):
        r = robots[i]
        #position[0] = x position[1] =y
        robot_julia = datos["agents"][i]
        opera.push()

        target_degree = robot_julia["looking_at"]

        r.setColor(1,1,1)
        if abs(target_degree - r.deg) > 0:
            r.girar(target_degree)

            while(abs(target_degree - r.deg) > 0):
                opera.push()
                r.render()
                opera.pop()

        opera.translation((robot_julia["pos"][1] - 1) * scale,(robot_julia["pos"][0] - 1 ) * scale)
        # if (robot_julia["found_box"] == True):
            # y_pos = 1

        # for j in range(1):
        #     #moverse en x
        #     if robot_julia["move"] == False:
        #         if robot_julia["direction"][1] == 1:
        #             print("Robot ", i, " esta viendo hacia la derecha")
        #             r.move_forward()
        #         else:
        #             print("Robot ", i, " esta viendo hacia la izquierda")
        #             r.move_backward()

        #     #moverse en y
        #     else:
        #         if robot_julia["direction"][0] == 1:
        #             print("Robot ", i, " esta subiendo")
        #         else:
        #             print("Robot ", i, " esta bajando")
        #         r.girar(90 * robot_julia["direction"][0])
        #         #algo pasa con el degree que no hace que se mueva lo mismo
        #         r.move_forward()
        #         r.girar(-90 * robot_julia["direction"][0])




        r.render()


        opera.pop()

    #Se busca el ultimo index porque el estante siempre es el ultimo
    ultimo_index = len(datos["agents"]) - 1

    pos_caja_x = 0
    print("Cantidad de cajas: ", datos["agents"][ultimo_index]["cantidad_cajas"])
    for i in range (datos["agents"][ultimo_index]["cantidad_cajas"]):
        if(i % 5 == 0 and i > 0):
            pos_caja_x += 3
        else:
            pos_caja_x += 0.3



        opera.push()
        opera.translation(pos_caja_x *scale,51*scale)
        box_render.render()
        opera.pop()

    if(datos["agents"][ultimo_index]["cantidad_cajas"] == cantidad_de_cajas):
        print("Se han recolectado todas las cajas")
        print("Se ha terminado la simulacion")
        print(datos["agents"][ultimo_index]["movimientos_robots"])
        exit(0)



    opera.pop()
    # deg = (deg + deltaDeg ) % 360
    # degrot = (degrot + deltaDeg) % 360

    # robots[0].opera.push()
    print(len(robots))




    #  robots = datos["agents"][0]
    # print("Robots position")
    # # print(robots["pos"][0])
    # print(robots["pos"][1])




def init():
    screen = pygame.display.set_mode(
        (screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL: ejes 2D")

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluOrtho2D(-100, 2500, -100, 2500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glClearColor(0, 0, 0, 0)
    # OPCIONES: GL_LINE, GL_POINT, GL_FILL
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glShadeModel(GL_FLAT)


def draw_point(x, y):
    glColor3f(1.0, 0.0, 0.0)  # Set the color to red
    glPointSize(5.0)  # Set the point size to 5.0
    glBegin(GL_POINTS)  # Start drawing points
    glVertex2f(x, y)  # Specify the position of the point
    glEnd()  # Done specifying points


# código principal ---------------------------------
init()




#Matrices para operaciones geometricas

A = np.identity(3) #matriz de modelado
T = np.identity(3) #matriz para la traslacion
R = np.identity(3) #matriz para rotacion
E = np.identity(3) #matriz de escalado


def Axis():
    glShadeModel(GL_FLAT)
    glLineWidth(3.0)
    # X axis in red
    glColor3f(1.0, 0.0, 0.0)
    glBegin(GL_LINES)
    glVertex2f(X_MIN, 0.0)
    glVertex2f(X_MAX, 0.0)
    glEnd()
    # Y axis in green
    glColor3f(0.0, 1.0, 0.0)
    glBegin(GL_LINES)
    glVertex2f(0.0, Y_MIN)
    glVertex2f(0.0, Y_MAX)
    glEnd()
    glLineWidth(1.0)




done = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                t1.move_forward()  # Mueve el carrito hacia adelante
            elif event.key == pygame.K_DOWN:
                t1.move_backward()  # Mueve el carrito hacia atrás
            elif event.key == pygame.K_LEFT:
                t1.girar(90)  # Gira 90 grados a la izquierda
            elif event.key == pygame.K_RIGHT:
                t1.girar(-90)  # Gira 90 grados a la derecha

    glClear(GL_COLOR_BUFFER_BIT)
    Axis()
    glPointParameterf(GL_POINT_SIZE_MAX, 100.0)
    display()
    pygame.display.flip()
    pygame.time.wait(100)

pygame.quit()

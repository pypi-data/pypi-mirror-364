import numpy as np
from copy import copy,deepcopy

#from pygdsdesign import GdsLibrary, PolygonSet, Rectangle, Round, substraction, offset,Text, CPW, MicroStrip, addition, MicroStrip_Polar
from pygdsdesign import (GdsLibrary, PolygonSet, Text, MicroStripPolar)

def spiral(u, args):

    r = args[1]*2.*args[2]*u + args[0]/2.
    theta = args[1]*2.*np.pi*u
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y


def dspiral_dt(u, args):

    r = args[1]*2.*args[2]*u
    theta = args[1]*2.*np.pi*u
    dx_dt = -args[1]*2.*np.pi * \
        np.sin(theta)*r + np.cos(theta)*args[1]*2.*args[2]
    dy_dt = args[1]*2.*np.pi*np.cos(theta)*r + np.sin(theta)*args[1]*2.*args[2]
    return dx_dt, dy_dt


def circle(t, args):
    x = args[0] * np.cos(t)
    y = args[0] * np.sin(t)
    return x, y

def dcircle_dt(t, args):
    dx_dt = - args[0] * np.sin(t)
    dy_dt = + args[0] * np.cos(t)
    return dx_dt, dy_dt


# Chip size of 5mm x 7mm
chip_dx = 595*2
chip_dy = 767*2

# The GDSII file is called a library, which contains multiple cells.
lib = GdsLibrary()

# Geometry must be placed in cells.
cell = lib.new_cell('TOP')


# Create empty polygon to which other polygon will be added
tot = PolygonSet()





# Add label on the top right of the chip
t = Text('Micro_Polar', 250)
dx_t, dy_t = t.get_size()
tot += t.translate(-dx_t+chip_dx, -dy_t-250)



# Center the design to the chip and the chip to the (0,0) of the cell


m=MicroStripPolar(2,np.pi/2.65)

m.add_taper(5, 3)
m.add_line(6)

u = np.linspace(0, 1, 10000)
inner_diameter = 10
nb_turn = 4
spiral_spacing = 3.
spiral_width = 2.
m.add_parametric_curve(spiral, dspiral_dt, u, args=(inner_diameter, nb_turn, spiral_spacing))

m.add_turn(6, -np.pi/4*2.5)
m.add_line(2)
m.add_line(2)
m.add_line(1)
m.add_turn(6, np.pi/4*2.5)
m.add_line(1)
m.add_turn(5, -np.pi)
m.add_line(2)
m.add_line(1)
m.add_turn(6, np.pi/4*2.5)
m.add_line(10)
m.add_turn(6, np.pi*2)
m.add_line(10)
m.add_turn(6, -np.pi/4*2.5)
m.add_line(10)
m.add_line(10)
m.add_turn(6, np.pi/2)
m.add_line(10)
m.add_line(10)
m.add_turn(60, -np.pi)
m.add_line(10)
m.add_turn(2, -np.pi/12)
m.add_line(10)
m.add_turn(6, np.pi/12)
m.add_line(10)
m.add_taper(5, 7)
m.add_line(10)
m.add_turn(3, -np.pi/12)
m.add_line(10)
m.add_turn(6, np.pi/12)
m.add_taper(5, 1)
m.add_turn(2, -np.pi/12)
m.add_line(10)
m.add_turn(6, np.pi/12)
m.add_line(10)
m.add_turn(6, np.pi/2)
m.add_parametric_curve(circle, dcircle_dt,np.linspace(-np.pi/4.36565, np.pi/3.512 , 100), args=[20],add_polygon=True)
m.add_line(10)
m.add_turn(6, np.pi/12)
m.add_line(10)
m.add_parametric_curve(circle, dcircle_dt,np.linspace(-np.pi/4.36565, np.pi/2 , 100), args=[20],add_polygon=True)
m.add_parametric_curve(circle, dcircle_dt,np.linspace(-np.pi/5, np.pi/4 , 100), args=[20],add_polygon=True)
m.add_line(10)
tot+=m




cell.add(tot)
# Save GDS file
lib.write_gds('microstrip_polar.gds')
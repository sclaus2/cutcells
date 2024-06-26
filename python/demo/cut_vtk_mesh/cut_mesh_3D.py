import cutcells
import numpy as np
import pyvista as pv

def level_set(x):
  r = 0.6
  c = np.array([0,0,0])
  value = 0
  for i in range(0,3):
    value = value  + (x[i]-c[i])**2
  value = np.sqrt(value)-r
  return value

def create_box_mesh(x0,y0,z0,x1,y1,z1,Nx,Ny,Nz):
  x = np.linspace(x0, x1, num=Nx)
  y = np.linspace(y0,y1, num=Ny)
  z = np.linspace(z0,z1, num=Nz)
  #produce grid of points by tensor product
  xx, yy, zz = np.meshgrid(x, y, z)
  points = np.c_[xx.reshape(-1), yy.reshape(-1), zz.reshape(-1)]
  poly_points = pv.PolyData(points)
  poly_mesh = poly_points.delaunay_3d()
  grid = pv.UnstructuredGrid(poly_mesh)

  return grid

def mark_cells(mesh):
  cells = mesh.cells
  points = mesh.points
  ls_values = np.zeros(len(points))
  inside_cells = np.empty(0, dtype=int)
  intersected_cells = np.empty(0, dtype=int)

  id = 0

  for i in range(mesh.n_cells):
    num_points = cells[id]
    id = id + 1

    for j in range(num_points):
       point = points[cells[id]]
       ls_values[j] = level_set(point)
       id = id + 1

    domain_str = cutcells.classify_cell_domain(ls_values)
    if domain_str=="inside":
      inside_cells=np.append(inside_cells,i)

    if domain_str=="intersected":
      intersected_cells=np.append(intersected_cells,i)

  return inside_cells, intersected_cells

def create_cut_mesh(mesh,inner_mesh, intersected_cells):
  cell_type = cutcells.CellType.tetrahedron
  triangulate = True
  gdim = 3

  cut_cells = []

  for cell_id in intersected_cells:
    c = mesh.get_cell(cell_id)
    vertex_coordinates = c.points.flatten()
    points = c.points
    j = 0
    ls_values = np.zeros(len(points))
    for point in points:
      ls_values[j] = level_set(point)
      j = j+1
    cut_cell_int = cutcells.cut(cell_type, vertex_coordinates,  gdim, ls_values, "phi<0", triangulate)
    cut_cells.append(cut_cell_int)

  cut_mesh = cutcells.create_cut_mesh(cut_cells)
  grid_cell = pv.UnstructuredGrid(cut_mesh.connectivity, cut_mesh.types, cut_mesh.vertex_coords)
  inner_mesh = inner_mesh.merge(grid_cell)

  return inner_mesh


N = 10
grid = create_box_mesh(-1,-1,-1, 1,1,1, N,N,N)

inside_cells, intersected_cells = mark_cells(grid)

extract = grid.extract_cells(inside_cells)

mesh = create_cut_mesh(grid,extract,intersected_cells)

mesh.plot(cpos="xy", show_edges=True)
pl = pv.Plotter()
pl.add_mesh(grid, show_edges=True, style = 'wireframe')
pl.add_mesh(mesh, show_edges=True)
pl.camera_position = 'xy'
pl.show()
pl.screenshot('mesh3D.png') 




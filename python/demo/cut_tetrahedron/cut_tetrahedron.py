import cutcells
import numpy as np
import pyvista as pv

ls_values = np.array([0.1,-0.1,-0.2, 0.4])
vertex_coordinates = np.array([1.,1.,1., 1.,-1., -1., -1, 1., -1., -1., -1, 1])

cell_type = cutcells.CellType.tetrahedron
triangulate = True
gdim = 3

cut_cell_int = cutcells.cut(cell_type, vertex_coordinates,  gdim, ls_values, "phi<0", triangulate)
print(cut_cell_int.str())
cut_cell_int.write_vtk("interior.vtu")

cut_cell_ext = cutcells.cut(cell_type, vertex_coordinates,  gdim, ls_values, "phi>0", triangulate)
print(cut_cell_ext.str())
cut_cell_ext.write_vtk("exterior.vtu")

cut_cell = cutcells.cut(cell_type, vertex_coordinates,  gdim, ls_values, "phi=0", triangulate)
print(cut_cell.str())
cut_cell.write_vtk("interface.vtu")

pv.start_xvfb()

grid_int = pv.UnstructuredGrid(cut_cell_int.connectivity, cut_cell_int.types, cut_cell_int.vertex_coords)
grid_ext = pv.UnstructuredGrid(cut_cell_ext.connectivity, cut_cell_ext.types, cut_cell_ext.vertex_coords)

split_cells_int = grid_int.explode()
split_cells_ext = grid_ext.explode()
#split_cells.plot(show_edges=True, ssao=True)

split_cells_int = split_cells_int.translate((0,0, -0.4), inplace=False)

plotter = pv.Plotter(off_screen=True)
plotter.set_background('white', top='white')
#plotter.enable_ssao()
plotter.add_mesh(split_cells_int, color="blue",show_edges=True, opacity=0.5)
plotter.add_mesh(split_cells_ext, color="red",show_edges=True, opacity=0.5)
plotter.show(screenshot='cut_tetra.png')

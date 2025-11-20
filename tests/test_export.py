import os
import numpy as np
import pytest
import trimesh

from src.export import (
    export_stl,
    export_obj,
    export_surface_stl,
    export_ply_point_cloud
)

# -------------------------------------------------------
#   MOCKS mínimos para simular Solid y ParametricSurface
# -------------------------------------------------------

class MockSolid:
    """Un sólido falso que obliga a mesh_from_solid a producir una malla sencilla."""
    def __init__(self):
        pass

class MockSurface:
    """Una superficie paramétrica simple: plano z = 0."""
    def __call__(self, u, v):
        return np.array([u, v, 0.0])


# -------------------------------------------------------
#   Parches a mesh_from_solid y mesh_from_surface
# -------------------------------------------------------

@pytest.fixture(autouse=True)
def patch_mesh_functions(monkeypatch):
    """Reemplaza mesh_from_solid y mesh_from_surface por versiones controladas."""

    def fake_mesh_from_solid(solid, resolution=10):
        # Regresa un triángulo simple
        vertices = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [0, 1, 0]
        ])
        faces = np.array([[0, 1, 2]])
        return trimesh.Trimesh(vertices=vertices, faces=faces)

    def fake_mesh_from_surface(surface, u_range, v_range, u_steps, v_steps):
        # Regresa un cuadrito plano
        vertices = np.array([
            [0, 0, 0], [1, 0, 0],
            [1, 1, 0], [0, 1, 0]
        ])
        faces = np.array([[0, 1, 2], [0, 2, 3]])
        return trimesh.Trimesh(vertices=vertices, faces=faces)

    monkeypatch.setattr("src.export.mesh_from_solid", fake_mesh_from_solid)
    monkeypatch.setattr("src.export.mesh_from_surface", fake_mesh_from_surface)


# -------------------------------------------------------
#   TESTS DE EXPORTACIÓN
# -------------------------------------------------------

def test_export_stl(tmp_path):
    file = tmp_path / "test_model.stl"
    export_stl(MockSolid(), str(file), resolution=10, ascii=False)
    assert file.exists()


def test_export_stl_ascii(tmp_path):
    file = tmp_path / "test_model_ascii.stl"
    export_stl(MockSolid(), str(file), ascii=True)
    assert file.exists()


def test_export_obj(tmp_path):
    file = tmp_path / "test_model.obj"
    export_obj(MockSolid(), str(file), resolution=10)
    assert file.exists()


def test_export_obj_with_color(tmp_path):
    file = tmp_path / "test_model_color.obj"
    export_obj(MockSolid(), str(file), color=(255, 0, 0))
    assert file.exists()


def test_export_surface_stl(tmp_path):
    file = tmp_path / "surface_test.stl"
    surf = MockSurface()
    export_surface_stl(surf, str(file), ascii=False)
    assert file.exists()


def test_export_ply_point_cloud(tmp_path):
    file = tmp_path / "cloud.ply"

    # Crear 3 puntos de prueba
    class V3:
        def __init__(self, x, y, z):
            self.x = x
            self.y = y
            self.z = z

    points = [V3(0,0,0), V3(1,0,0), V3(0,1,0)]
    colors = [(255,0,0), (0,255,0), (0,0,255)]

    export_ply_point_cloud(points, str(file), colors=colors, ascii=False)
    assert file.exists()


def test_export_ply_without_colors(tmp_path):
    file = tmp_path / "cloud_no_color.ply"

    class V3:
        def __init__(self, x, y, z):
            self.x = x
            self.y = y
            self.z = z

    points = [V3(0,0,0), V3(1,0,0)]
    export_ply_point_cloud(points, str(file))
    assert file.exists()
import pytest
import numpy as np
import trimesh
from dataclasses import dataclass
from typing import Callable, Tuple

# --- MOCKS / STUBS (Para aislar el test) ---

@dataclass(frozen=True)
class MockVector3:
    x: float
    y: float
    z: float

@dataclass(frozen=True)
class MockSolid:
    contains: Callable[[MockVector3], bool]
    bounds: Tuple[MockVector3, MockVector3]

# --- IMPORTACIÓN DEL CÓDIGO A PROBAR ---
# Nota: Aquí ya NO importamos 'Solid' desde .csg porque usamos el MockSolid de arriba.
# Solo importamos las funciones que vamos a testear desde src.mesh
from src.mesh import mesh_from_solid, mesh_from_surface

# --- FIXTURES ---

@pytest.fixture
def unit_cube_solid():
    """Crea un sólido que representa un cubo de 1x1x1 centrado en el origen."""
    def contains(p):
        return -0.5 <= p.x <= 0.5 and -0.5 <= p.y <= 0.5 and -0.5 <= p.z <= 0.5
    
    bounds = (MockVector3(-0.6, -0.6, -0.6), MockVector3(0.6, 0.6, 0.6))
    return MockSolid(contains, bounds)

@pytest.fixture
def empty_solid():
    """Crea un sólido que no contiene nada (vacío)."""
    def contains(p):
        return False
    bounds = (MockVector3(0, 0, 0), MockVector3(1, 1, 1))
    return MockSolid(contains, bounds)

@pytest.fixture
def simple_plane_surface():
    """Una superficie paramétrica simple (un plano XY)."""
    def surface_fn(u, v):
        return MockVector3(u * 10, v * 10, 0.0)
    return surface_fn

# --- TEST CASES ---

def test_mesh_from_solid_generates_geometry(unit_cube_solid):
    mesh = mesh_from_solid(unit_cube_solid, resolution=10)
    assert isinstance(mesh, trimesh.Trimesh)
    assert not mesh.is_empty
    assert mesh.is_watertight

def test_mesh_from_solid_handles_empty_space(empty_solid):
    mesh = mesh_from_solid(empty_solid, resolution=10)
    assert isinstance(mesh, trimesh.Trimesh)
    assert mesh.is_empty
    assert len(mesh.vertices) == 0

def test_mesh_from_solid_invalid_bounds():
    bounds = (MockVector3(0,0,0), MockVector3(0,0,0))
    bad_solid = MockSolid(lambda p: True, bounds)
    mesh = mesh_from_solid(bad_solid, resolution=10)
    assert mesh.is_empty

def test_mesh_from_solid_resolution_impact(unit_cube_solid):
    mesh_low = mesh_from_solid(unit_cube_solid, resolution=5)
    mesh_high = mesh_from_solid(unit_cube_solid, resolution=15)
    assert len(mesh_high.vertices) > len(mesh_low.vertices)

def test_mesh_from_surface_generates_grid(simple_plane_surface):
    u_steps, v_steps = 5, 5
    mesh = mesh_from_surface(simple_plane_surface, u_steps=u_steps, v_steps=v_steps)
    assert not mesh.is_empty
    expected_vertices = u_steps * v_steps
    assert len(mesh.vertices) == expected_vertices

def test_mesh_from_surface_bounds():
    def flat_surface(u, v):
        return MockVector3(u, v, 0)
    mesh = mesh_from_surface(flat_surface, u_steps=2, v_steps=2)
    bbox = mesh.bounding_box.bounds
    np.testing.assert_array_almost_equal(bbox[0], [0,0,0])
    np.testing.assert_array_almost_equal(bbox[1], [1,1,0])
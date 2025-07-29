"""

Copyright (C) 2025 Murilo Marques Marinho (www.murilomarinho.info)
LGPLv3 License
"""
from __future__ import annotations
import dqrobotics._dqrobotics
from dqrobotics._dqrobotics import DQ
from dqrobotics._dqrobotics._robot_modeling import DQ_Kinematics
from dqrobotics._dqrobotics._utils import DQ_Geometry
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import Ad
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import Adsharp
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import C4
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import C8
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import D
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import Im
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import P
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import Q4
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import Q8
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import Re
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import conj
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import cross
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import crossmatrix4
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import dec_mult
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import dot
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import exp
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import generalized_jacobian
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import haminus4
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import haminus8
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import hamiplus4
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import hamiplus8
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import inv
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import is_line
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import is_plane
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import is_pure
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import is_pure_quaternion
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import is_quaternion
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import is_real
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import is_real_number
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import is_unit
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import log
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import norm
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import normalize
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import pinv
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import pow
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import rotation
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import rotation_angle
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import rotation_axis
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import sharp
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import tplus
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import translation
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import vec3
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import vec4
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import vec6
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libcpp_abi1 import vec8
from dqrobotics import robot_modeling
import numpy as np
__all__ = ['Ad', 'Adsharp', 'C4', 'C8', 'D', 'DQ', 'DQ_Geometry', 'DQ_Kinematics', 'DQ_threshold', 'E_', 'Im', 'P', 'Q4', 'Q8', 'Re', 'conj', 'cross', 'crossmatrix4', 'dec_mult', 'dot', 'exp', 'generalized_jacobian', 'haminus4', 'haminus8', 'hamiplus4', 'hamiplus8', 'i_', 'inv', 'is_line', 'is_plane', 'is_pure', 'is_pure_quaternion', 'is_quaternion', 'is_real', 'is_real_number', 'is_unit', 'j_', 'k_', 'log', 'needle_entry_error', 'needle_jacobian', 'norm', 'normalize', 'np', 'pinv', 'pow', 'robot_modeling', 'rotation', 'rotation_angle', 'rotation_axis', 'sharp', 'tplus', 'translation', 'vec3', 'vec4', 'vec6', 'vec8']
def needle_entry_error(x_needle: dqrobotics._dqrobotics.DQ, p_vessel: dqrobotics._dqrobotics.DQ, needle_radius: float):
    """
    
    First idea, "needle" Jacobian. It is defined as J = [Jr Jpi]^T
    x_needle: The pose of the centre of the needle
    p_vessel: The position of the entry point in the vessel
    needle_radius: The radius of the needle
    """
def needle_jacobian(Jx_needle, x_needle: dqrobotics._dqrobotics.DQ, p_vessel: dqrobotics._dqrobotics.DQ):
    """
    
    First idea, "needle" Jacobian. It is defined as J = [Jr Jpi]^T
    x: The pose of the centre of the needle
    Jx: The analytical Jacobian of the pose of the centre of the needle
    p_vessel: The position of the entry point in the vessel
    """
DQ_threshold: float = 1e-12
E_: dqrobotics._dqrobotics.DQ  # value = E*(1)
i_: dqrobotics._dqrobotics.DQ  # value = 1i
j_: dqrobotics._dqrobotics.DQ  # value = 1j
k_: dqrobotics._dqrobotics.DQ  # value = 1k

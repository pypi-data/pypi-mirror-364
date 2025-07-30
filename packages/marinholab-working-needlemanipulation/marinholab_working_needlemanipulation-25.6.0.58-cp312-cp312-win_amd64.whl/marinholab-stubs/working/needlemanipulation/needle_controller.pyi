"""

Copyright (C) 2025 Murilo Marques Marinho (www.murilomarinho.info)
LGPLv3 License
"""
from __future__ import annotations
import dqrobotics._dqrobotics
from dqrobotics._dqrobotics import DQ
import dqrobotics._dqrobotics._robot_modeling
from dqrobotics._dqrobotics._robot_modeling import DQ_SerialManipulator
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import Ad
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import Adsharp
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import C4
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import C8
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import D
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import Im
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import P
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import Q4
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import Q8
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import Re
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import conj
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import cross
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import crossmatrix4
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import dec_mult
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import dot
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import exp
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import generalized_jacobian
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import haminus4
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import haminus8
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import hamiplus4
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import hamiplus8
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import inv
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import is_line
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import is_plane
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import is_pure
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import is_pure_quaternion
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import is_quaternion
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import is_real
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import is_real_number
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import is_unit
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import log
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import norm
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import normalize
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import pinv
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import pow
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import rotation
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import rotation_angle
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import rotation_axis
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import sharp
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import tplus
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import translation
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import vec3
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import vec4
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import vec6
from dqrobotics._dqrobotics.pybind11_detail_function_record_v1_system_libstdcpp_gxx_abi_1xxx_use_cxx11_abi_1 import vec8
from dqrobotics import robot_modeling
from dqrobotics import solvers
from dqrobotics import utils
from marinholab.working.needlemanipulation._impl import needle_jacobian
from marinholab.working.needlemanipulation._impl import needle_w
import marinholab.working.needlemanipulation.icra2019_controller
from marinholab.working.needlemanipulation.icra2019_controller import ICRA19TaskSpaceController
import numpy as np
import numpy
__all__ = ['Ad', 'Adsharp', 'C4', 'C8', 'D', 'DQ', 'DQ_SerialManipulator', 'DQ_threshold', 'E_', 'ICRA19TaskSpaceController', 'Im', 'NeedleController', 'P', 'Q4', 'Q8', 'Re', 'conj', 'cross', 'crossmatrix4', 'dec_mult', 'dot', 'exp', 'generalized_jacobian', 'haminus4', 'haminus8', 'hamiplus4', 'hamiplus8', 'i_', 'inv', 'is_line', 'is_plane', 'is_pure', 'is_pure_quaternion', 'is_quaternion', 'is_real', 'is_real_number', 'is_unit', 'j_', 'k_', 'log', 'needle_jacobian', 'needle_w', 'norm', 'normalize', 'np', 'pinv', 'pow', 'robot_modeling', 'rotation', 'rotation_angle', 'rotation_axis', 'sharp', 'solvers', 'tplus', 'translation', 'utils', 'vec3', 'vec4', 'vec6', 'vec8']
class NeedleController(marinholab.working.needlemanipulation.icra2019_controller.ICRA19TaskSpaceController):
    def __init__(self, kinematics: dqrobotics._dqrobotics._robot_modeling.DQ_SerialManipulator, gain: float, damping: float, alpha: float, rcm_constraints: list[tuple[dqrobotics._dqrobotics.DQ, float, int]], relative_needle_pose: dqrobotics._dqrobotics.DQ, vessel_positions: list[dqrobotics._dqrobotics.DQ], needle_radius: float, vfi_gain: float = 2.0, **kwargs):
        ...
    def compute_setpoint_control_signal(self, q, xd) -> numpy.array:
        """
        
                Get the control signal for the next step as the result of the constrained optimization.
                Joint limits are currently not considered.
                :param q: The current joint positions.
                :param xd: The desired pose.
                :return: The desired joint positions that should be sent to the robot.
                
        """
DQ_threshold: float = 1e-12
E_: dqrobotics._dqrobotics.DQ  # value = E*(1)
i_: dqrobotics._dqrobotics.DQ  # value = 1i
j_: dqrobotics._dqrobotics.DQ  # value = 1j
k_: dqrobotics._dqrobotics.DQ  # value = 1k

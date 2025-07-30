"""

Copyright (C) 2020-25 Murilo Marques Marinho (www.murilomarinho.info)
LGPLv3 License
"""
from __future__ import annotations
import dqrobotics._dqrobotics
from dqrobotics._dqrobotics import DQ
import dqrobotics._dqrobotics._robot_modeling
from dqrobotics._dqrobotics._robot_modeling import DQ_Kinematics
from dqrobotics._dqrobotics._robot_modeling import DQ_SerialManipulator
from dqrobotics._dqrobotics._utils import DQ_Geometry
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
from dqrobotics.solvers._dq_quadprog_solver import DQ_QuadprogSolver
from dqrobotics import utils
import math as math
import numpy as np
import numpy
from termcolor.termcolor import cprint
__all__ = ['Ad', 'Adsharp', 'C4', 'C8', 'D', 'DQ', 'DQ_Geometry', 'DQ_Kinematics', 'DQ_QuadprogSolver', 'DQ_SerialManipulator', 'DQ_threshold', 'E_', 'ICRA19TaskSpaceController', 'Im', 'P', 'Q4', 'Q8', 'Re', 'conj', 'cprint', 'cross', 'crossmatrix4', 'dec_mult', 'dot', 'exp', 'generalized_jacobian', 'haminus4', 'haminus8', 'hamiplus4', 'hamiplus8', 'i_', 'inv', 'is_line', 'is_plane', 'is_pure', 'is_pure_quaternion', 'is_quaternion', 'is_real', 'is_real_number', 'is_unit', 'j_', 'k_', 'log', 'math', 'norm', 'normalize', 'np', 'pinv', 'pow', 'robot_modeling', 'rotation', 'rotation_angle', 'rotation_axis', 'sharp', 'tplus', 'translation', 'utils', 'vec3', 'vec4', 'vec6', 'vec8']
class ICRA19TaskSpaceController:
    """
    
        An implementation of the task-space controller described in:
         "A Unified Framework for the Teleoperation of Surgical Robots in Constrained Workspaces".
         Marinho, M. M; et al.
         In 2019 IEEE International Conference on Robotics and Automation (ICRA), pages 2721–2727, May 2019. IEEE
         http://doi.org/10.1109/ICRA.2019.8794363
        
    """
    @staticmethod
    def _get_rotation_error(x, xd):
        ...
    @staticmethod
    def get_rcm_constraint(Jx: numpy.array, x: dqrobotics._dqrobotics.DQ, primitive: dqrobotics._dqrobotics.DQ, p: dqrobotics._dqrobotics.DQ, d_safe: float, eta_d: float) -> (numpy.array, numpy.array):
        """
        
                This static method computes the Remote Centre of Motion (RCM) constraint
                for the end-effector represented by x and its Jacobian Jx. It calculates the
                inequality matrix and vector that ensure the minimum safe squared distance (d_safe) between a line
                and a point is maintained during motion.
        
                :param Jx: The pose Jacobian of the robot.
                :param x: The current pose of the end-effector, compatible with Jx.
                :param primitive: The primitive in the end-effector in which the line is spanned. For instance i_, j_, or k_.
                :param p: The centre of the RCM constraint, represented as a pure quaternion.
                :param d_safe: The safe distance (float) to maintain between the line and the
                    point, squared internally in the calculation.
                :param eta_d: VFI gain.
                :return: A tuple containing:
                    - W (np.array): The inequality constraint matrix derived from the line-to-point
                      distance Jacobian.
                    - w (np.array): The inequality constraint vector determined by the distance
                      error and safety distance.
                
        """
    def __init__(self, kinematics: dqrobotics._dqrobotics._robot_modeling.DQ_SerialManipulator, gain: float, damping: float, alpha: float, rcm_constraints: list[tuple[dqrobotics._dqrobotics.DQ, float, int]], vfi_gain: float = 2.0, **kwargs):
        """
        
                Initialize the controller.
                :param kinematics: A suitable DQ_SerialManipulator object.
                :param gain: A positive float. Controller proportional gain.
                :param damping: A positive float. Damping factor.
                :param alpha: A float between 0 and 1. Soft priority between translation and rotation.
                :param rcm_constraints: A list of tuples (p, r, ith), where p is the position of the constraint as a pure quaternion
                r is the radius of the constraint, and ith is the index of the joint this constraint relates to.
                
        """
    def _get_optimization_parameters(self, q, xd):
        ...
    def compute_setpoint_control_signal(self, q, xd) -> numpy.array:
        """
        
                Get the control signal for the next step as the result of the constrained optimization.
                Joint limits are currently not considered.
                :param q: The current joint positions.
                :param xd: The desired pose.
                :return: The desired joint positions that should be sent to the robot.
                
        """
    def get_last_error(self) -> numpy.array:
        ...
    def get_last_robot_pose(self) -> dqrobotics._dqrobotics.DQ:
        """
        
                Retrieves the last recorded position of the robot.
        
                This method returns the most recently recorded pose of the end-effector of the robot.
        
                :return: The last recorded x-axis position of the robot.
                :rtype: DQ
                
        """
DQ_threshold: float = 1e-12
E_: dqrobotics._dqrobotics.DQ  # value = E*(1)
i_: dqrobotics._dqrobotics.DQ  # value = 1i
j_: dqrobotics._dqrobotics.DQ  # value = 1j
k_: dqrobotics._dqrobotics.DQ  # value = 1k

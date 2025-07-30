"""

        marinholab.working.needlemanipulation
        -------------------------------------

        .. currentmodule:: needlemanipulation

        .. autosummary::
           :toctree: _generate

           M3_SerialManipulatorSimulatorFriendly
    
"""
from __future__ import annotations
import collections.abc
import dqrobotics._dqrobotics
import dqrobotics._dqrobotics._robot_modeling
import numpy
import numpy.typing
import typing
__all__ = ['M3_SerialManipulatorSimulatorFriendly']
class M3_SerialManipulatorSimulatorFriendly(dqrobotics._dqrobotics._robot_modeling.DQ_SerialManipulator):
    class ActuationType:
        """
        Members:
        
          RZ : Revolution about the z-axis
        
          RY : Revolution about the y-axis
        
          RX : Revolution about the x-axis
        
          TZ : Translation along the z-axis
        
          TY : Translation along the y-axis
        
          TX : Translation along the x-axis
        """
        RX: typing.ClassVar[M3_SerialManipulatorSimulatorFriendly.ActuationType]  # value = <ActuationType.RX: 2>
        RY: typing.ClassVar[M3_SerialManipulatorSimulatorFriendly.ActuationType]  # value = <ActuationType.RY: 1>
        RZ: typing.ClassVar[M3_SerialManipulatorSimulatorFriendly.ActuationType]  # value = <ActuationType.RZ: 0>
        TX: typing.ClassVar[M3_SerialManipulatorSimulatorFriendly.ActuationType]  # value = <ActuationType.TX: 5>
        TY: typing.ClassVar[M3_SerialManipulatorSimulatorFriendly.ActuationType]  # value = <ActuationType.TY: 4>
        TZ: typing.ClassVar[M3_SerialManipulatorSimulatorFriendly.ActuationType]  # value = <ActuationType.TZ: 3>
        __members__: typing.ClassVar[dict[str, M3_SerialManipulatorSimulatorFriendly.ActuationType]]  # value = {'RZ': <ActuationType.RZ: 0>, 'RY': <ActuationType.RY: 1>, 'RX': <ActuationType.RX: 2>, 'TZ': <ActuationType.TZ: 3>, 'TY': <ActuationType.TY: 4>, 'TX': <ActuationType.TX: 5>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: typing.SupportsInt) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: typing.SupportsInt) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    RX: typing.ClassVar[M3_SerialManipulatorSimulatorFriendly.ActuationType]  # value = <ActuationType.RX: 2>
    RY: typing.ClassVar[M3_SerialManipulatorSimulatorFriendly.ActuationType]  # value = <ActuationType.RY: 1>
    RZ: typing.ClassVar[M3_SerialManipulatorSimulatorFriendly.ActuationType]  # value = <ActuationType.RZ: 0>
    TX: typing.ClassVar[M3_SerialManipulatorSimulatorFriendly.ActuationType]  # value = <ActuationType.TX: 5>
    TY: typing.ClassVar[M3_SerialManipulatorSimulatorFriendly.ActuationType]  # value = <ActuationType.TY: 4>
    TZ: typing.ClassVar[M3_SerialManipulatorSimulatorFriendly.ActuationType]  # value = <ActuationType.TZ: 3>
    def __init__(self, offset_before: collections.abc.Sequence[dqrobotics._dqrobotics.DQ], offset_after: collections.abc.Sequence[dqrobotics._dqrobotics.DQ], actuation_types: collections.abc.Sequence[...]) -> None:
        """
                The M3_SerialManipulatorSimulatorFriendly constructor.
        
                :param offset_before: A list of DQ representing the offset of each joint transformation before actuation.
                :type offset_before: List[DQ]
                :param offset_after: A list of DQ representing the offset of each joint transformation after actuation.
                :type offset_after: List[DQ]
                :param actuation_types: A list of M3_SerialManipulatorSimulatorFriendly.ActuationType denoting the actuation
                                        type and axis of each joint.
                :type actuation_types: List[M3_SerialManipulatorSimulatorFriendly.ActuationType]
                :rtype: M3_SerialManipulatorSimulatorFriendly
        """
    def raw_fkm(self, arg0: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 1]"], arg1: typing.SupportsInt) -> dqrobotics._dqrobotics.DQ:
        """
        Retrieves the raw FKM.
        """
    def raw_pose_jacobian(self, arg0: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 1]"], arg1: typing.SupportsInt) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[m, n]"]:
        """
        Retrieves the raw pose Jacobian.
        """
    def raw_pose_jacobian_derivative(self, arg0: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 1]"], arg1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[m, 1]"], arg2: typing.SupportsInt) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[m, n]"]:
        """
        Retrieves the raw pose Jacobian derivative.
        """
__version__: str = 'dev'

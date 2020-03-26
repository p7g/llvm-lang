from typing import Callable, TypeVar

T_Prev_Context = TypeVar('T_Prev_Context', contravariant=True)
T_Next_Context = TypeVar('T_Next_Context', covariant=True)

Pass = Callable[[T_Prev_Context], T_Next_Context]

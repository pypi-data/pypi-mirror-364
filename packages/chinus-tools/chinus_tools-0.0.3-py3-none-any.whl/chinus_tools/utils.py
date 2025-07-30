from typing import (
    get_origin,
    Literal,
    get_args,
)

__all__ = ['Enum']


class NoReassign(type):
    """
    수정 불가능한 Enum 메타 클래스
    Literal 타입인 변수는 list타입으로 리턴
    """

    def __setattr__(cls, k, v):
        raise AttributeError(f"Enum의 속성은 재할당할 수 없습니다.")

    def __getattribute__(self, item):
        """
        Literal 타입인 변수는 list타입으로 리턴
        """
        attr = object.__getattribute__(self, item)
        if get_origin(attr) is Literal:
            return list(get_args(attr))

        return attr


class Enum(metaclass=NoReassign):
    pass
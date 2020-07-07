from typing import NewType, Dict, Any, Callable, Iterable, Union, IO, AnyStr
from pathlib import Path

ValueObject = NewType("ValueObject", Dict[str, Any])
CmpFunc = NewType("CmpFunc", Callable[[Any, Iterable], bool])

FileDictStringLike = Union[str, Path, IO[AnyStr], Dict[str, any]]

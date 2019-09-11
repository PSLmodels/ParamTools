from typing import NewType, Dict, Any, Callable, Iterable

ValueObject = NewType("ValueObject", Dict[str, Any])
CmpFunc = NewType("CmpFunc", Callable[[Any, Iterable], bool])

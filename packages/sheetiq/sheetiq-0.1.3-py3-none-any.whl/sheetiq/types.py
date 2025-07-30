from typing import TypedDict, List, Literal, Union
class SheetIQParam(TypedDict):
    token: str


class SheetIQGetSheet(TypedDict, total=False):
    id: str
    range: str
    key: bool


class SheetIQUpdateSheet(TypedDict):
    id: str
    range: str
    type: Literal["append", "update"]
    data: List[List[Union[str, int, float]]]
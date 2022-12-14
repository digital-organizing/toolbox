from typing import Any, Dict


class Result:

    def to_dict(self) -> Dict[str, Any]:
        return {}


class Closed(Result):
    pass

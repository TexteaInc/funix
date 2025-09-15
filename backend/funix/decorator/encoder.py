from json import JSONEncoder
from datetime import datetime


class FunixJsonEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if hasattr(o, "__class__"):
            clz = o.__class__
            if hasattr(clz, "__base__"):
                base = clz.__base__
                # Check pydantic
                try:
                    from pydantic import BaseModel

                    if issubclass(base, BaseModel):
                        return o.model_dump(mode="json")
                except ImportError:
                    return super().default(o)
        return super().default(o)

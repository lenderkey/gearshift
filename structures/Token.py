import dataclasses
import datetime

@dataclasses.dataclass
class Token:
    token: str
    path: str
    email: str
    state: str = "A"
    data: str = "{}"
    added: datetime.datetime = None
    seen: datetime.datetime = None
    expires: datetime.datetime = None

    @classmethod
    def make(cls, **kwargs: dict):
        """
        Prefer this to the constructor. It will only pass known args.
        """
        obj = cls(**{k: kwargs[k] for k in kwargs if k in cls.__match_args__})
        obj.extras = {k: kwargs[k] for k in kwargs if k not in cls.__match_args__}

        return obj

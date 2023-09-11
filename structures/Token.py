import dataclasses
import datetime

import helpers

@dataclasses.dataclass
class Token:
    token_id: str
    path: str
    email: str
    id: int = 0
    state: str = "A"
    data: str = "{}"
    added: datetime.datetime = None
    seen: datetime.datetime = None
    expires: datetime.datetime = None

    @classmethod
    def make(cls, **kwargs: dict) -> "Token":
        """
        Prefer this to the constructor. It will only pass known args.
        """
        obj = cls(**{k: kwargs[k] for k in kwargs if k in cls.__match_args__})
        obj.cleanup()

        return obj

    def cleanup(self) -> None:
        ## total hack
        for key in [ "added", "seen", "expires" ]:
            value = getattr(self, key)
            if isinstance(value, str):
                setattr(self, key, helpers.to_datetime(value))

    def clone(self) -> "Token":
        return Token.make(**self.to_dict())

    def to_dict(self) -> dict:
        import helpers

        d = dataclasses.asdict(self)
        d["added"] = helpers.format_datetime(self.added)
        d["seen"] = helpers.format_datetime(self.seen)
        d["expires"] = helpers.format_datetime(self.expires)

        return d

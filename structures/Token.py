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
        obj.cleanup()

        return obj

    def cleanup(self):
        ## total hack
        for key in [ "added", "seen", "expires" ]:
            value = getattr(self, key)
            if isinstance(value, str):
                try:
                    value = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
                except ValueError:
                    value = datetime.datetime.fromisoformat(value)
                    
                setattr(self, key, value)

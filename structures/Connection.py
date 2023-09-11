import dataclasses
import datetime

@dataclasses.dataclass
class Connection:
    """
    This records information about the current connection,
    e.g. for recording who sent a request over HTTP
    """
    ip: str = None
    headers: dict = dataclasses.field(default_factory=dict)

    @classmethod
    def make(cls, **kwargs: dict):
        """
        Prefer this to the constructor. It will only pass known args.
        """
        obj = cls(**{k: kwargs[k] for k in kwargs if k in cls.__match_args__})

        return obj

    @classmethod
    def from_request(cls, request):
        """
        """
        return cls.make(
            ip=request.client.host,
            headers=dict(request.headers),
        )
    
    def to_dict(self) -> dict:
        return dataclasses.asdict(self)
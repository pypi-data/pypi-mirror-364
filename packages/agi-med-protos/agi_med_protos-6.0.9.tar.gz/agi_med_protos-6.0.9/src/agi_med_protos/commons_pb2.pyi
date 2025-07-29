from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OuterContextItem(_message.Message):
    __slots__ = ("Sex", "Age", "UserId", "SessionId", "ClientId", "TrackId", "EntrypointKey", "LanguageCode")
    SEX_FIELD_NUMBER: _ClassVar[int]
    AGE_FIELD_NUMBER: _ClassVar[int]
    USERID_FIELD_NUMBER: _ClassVar[int]
    SESSIONID_FIELD_NUMBER: _ClassVar[int]
    CLIENTID_FIELD_NUMBER: _ClassVar[int]
    TRACKID_FIELD_NUMBER: _ClassVar[int]
    ENTRYPOINTKEY_FIELD_NUMBER: _ClassVar[int]
    LANGUAGECODE_FIELD_NUMBER: _ClassVar[int]
    Sex: bool
    Age: int
    UserId: str
    SessionId: str
    ClientId: str
    TrackId: str
    EntrypointKey: str
    LanguageCode: str
    def __init__(self, Sex: bool = ..., Age: _Optional[int] = ..., UserId: _Optional[str] = ..., SessionId: _Optional[str] = ..., ClientId: _Optional[str] = ..., TrackId: _Optional[str] = ..., EntrypointKey: _Optional[str] = ..., LanguageCode: _Optional[str] = ...) -> None: ...

class ChatItem(_message.Message):
    __slots__ = ("OuterContext", "InnerContext")
    OUTERCONTEXT_FIELD_NUMBER: _ClassVar[int]
    INNERCONTEXT_FIELD_NUMBER: _ClassVar[int]
    OuterContext: OuterContextItem
    InnerContext: InnerContextItem
    def __init__(self, OuterContext: _Optional[_Union[OuterContextItem, _Mapping]] = ..., InnerContext: _Optional[_Union[InnerContextItem, _Mapping]] = ...) -> None: ...

class InnerContextItem(_message.Message):
    __slots__ = ("Replicas",)
    REPLICAS_FIELD_NUMBER: _ClassVar[int]
    Replicas: _containers.RepeatedCompositeFieldContainer[ReplicaItem]
    def __init__(self, Replicas: _Optional[_Iterable[_Union[ReplicaItem, _Mapping]]] = ...) -> None: ...

class ReplicaItem(_message.Message):
    __slots__ = ("Body", "Role", "DateTime", "ResourceId")
    BODY_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    DATETIME_FIELD_NUMBER: _ClassVar[int]
    RESOURCEID_FIELD_NUMBER: _ClassVar[int]
    Body: str
    Role: bool
    DateTime: str
    ResourceId: str
    def __init__(self, Body: _Optional[str] = ..., Role: bool = ..., DateTime: _Optional[str] = ..., ResourceId: _Optional[str] = ...) -> None: ...

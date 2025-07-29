from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Trigger(_message.Message):
    __slots__ = ("type",)
    TYPE_FIELD_NUMBER: _ClassVar[int]
    type: str
    def __init__(self, type: _Optional[str] = ...) -> None: ...

class Workflow(_message.Message):
    __slots__ = ("workflow_id", "chunk", "version", "paused", "owner", "schedule", "triggers", "queue")
    class ScheduleEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    WORKFLOW_ID_FIELD_NUMBER: _ClassVar[int]
    CHUNK_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    PAUSED_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_FIELD_NUMBER: _ClassVar[int]
    TRIGGERS_FIELD_NUMBER: _ClassVar[int]
    QUEUE_FIELD_NUMBER: _ClassVar[int]
    workflow_id: str
    chunk: bytes
    version: str
    paused: bool
    owner: str
    schedule: _containers.ScalarMap[str, str]
    triggers: _containers.RepeatedCompositeFieldContainer[Trigger]
    queue: str
    def __init__(self, workflow_id: _Optional[str] = ..., chunk: _Optional[bytes] = ..., version: _Optional[str] = ..., paused: bool = ..., owner: _Optional[str] = ..., schedule: _Optional[_Mapping[str, str]] = ..., triggers: _Optional[_Iterable[_Union[Trigger, _Mapping]]] = ..., queue: _Optional[str] = ...) -> None: ...

class Result(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

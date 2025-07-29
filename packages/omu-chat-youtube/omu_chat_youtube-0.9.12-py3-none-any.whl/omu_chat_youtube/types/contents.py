from typing import TypedDict

from .chatactions import ChatActions
from .tracking import ClickTrackingParams


class InvalidationId(TypedDict):
    objectSource: int
    objectId: str
    topic: str
    subscribeToGcmTopics: bool
    protoCreationTimestampMs: str


class InvalidationContinuationData(ClickTrackingParams):
    invalidationId: InvalidationId
    timeoutMs: int
    continuation: str


class ContinuationItem(TypedDict):
    invalidationContinuationData: InvalidationContinuationData


type Continuations = list[ContinuationItem]


class LiveChatRenderer(TypedDict):
    continuations: Continuations
    actions: ChatActions


class Contents(TypedDict):
    liveChatRenderer: LiveChatRenderer

import uuid

from pydantic import BaseModel
from typing import Any


class BaseApiResponse(BaseModel):
    result: str


class ApiResponse(BaseApiResponse):
    id: int


class ApiResponseError(BaseApiResponse):
    code: int | None
    error: str | None


class BaseEntity(BaseModel):
    id: int


class TimePoint(BaseModel):
    date: str | None
    time: str | None
    datetime: str | None


class PersonResponse(BaseModel):
    id: str
    name: str


class GroupResponse(BaseModel):
    id: int
    name: str


class PeopleResponse(BaseModel):
    users: list[PersonResponse]
    groups: list[GroupResponse]


class CommentResponse(BaseModel):
    id: int
    task: BaseEntity | None
    project: BaseEntity | None
    contact: PersonResponse | None
    owner: PersonResponse | None
    recipients: PeopleResponse | None
    description: str | None


class ApiCommentResponse(BaseApiResponse):
    comment: CommentResponse


class CustomField(BaseEntity):
    name: str
    type: int
    objectType: int


class BaseUserResponse(BaseEntity):
    name: str | None
    midname: str | None
    lastname: str | None
    email: str | None


class CustomFieldDataResponse(BaseModel):
    field: CustomField
    value: int | str | Any


class CustomFieldValueRequest(BaseModel):
    field: BaseEntity
    value: int | str | Any


class UserResponse(BaseUserResponse):
    customFieldData: list[CustomFieldDataResponse] | None


class ApiUserResponse(BaseApiResponse):
    user: UserResponse


class ContactResponse(BaseUserResponse):
    customFieldData: list[CustomFieldDataResponse] | None


class ApiContactResponse(BaseApiResponse):
    contact: ContactResponse


class FileResponse(BaseModel):
    id: int
    size: int
    name: str
    downloadUrl: str | None


class ApiFileResponse(BaseApiResponse):
    file: FileResponse


class TaskCreateRequest(BaseEntity):
    sourceObjectId: uuid.UUID | None
    sourceDataVersion: str | None
    name: str | None
    description: str | None
    priority: int | None
    status: dict | None
    processId: int | None
    resultChecking: bool | None
    assigner: PersonResponse | None
    parent: BaseEntity | None
    template: BaseEntity | None
    project: BaseEntity | None
    counterparty: PersonResponse | None
    dateTime: TimePoint | None
    startDateTime: TimePoint | None
    endDateTime: TimePoint | None
    delayedTillDate: TimePoint | None
    duration: int | None
    durationUnit: str | None
    durationType: str | None
    overdue: bool | None
    closeToDeadLine: bool | None
    notAcceptedInTime: bool | None
    inFavorites: bool | None
    isSummary: bool | None
    isSequential: bool | None
    assignees: PeopleResponse | None
    participants: PeopleResponse | None
    auditors: PeopleResponse | None
    isDeleted: bool | None
    customFieldData: list[CustomFieldValueRequest] | None
    files: list[FileResponse] | None


class TaskResponse(BaseEntity):
    sourceObjectId: uuid.UUID | None
    sourceDataVersion: str | None
    name: str | None
    description: str | None
    priority: int | None
    status: dict | None
    processId: int | None
    resultChecking: bool | None
    type: str | None
    assigner: PersonResponse | None
    parent: BaseEntity | None
    template: BaseEntity | None
    project: BaseEntity | None
    counterparty: PersonResponse | None
    dateTime: TimePoint | None
    startDateTime: TimePoint | None
    endDateTime: TimePoint | None
    hasStartDate: bool | None
    hasEndDate: bool | None
    hasStartTime: bool | None
    hasEndTime: bool | None
    delayedTillDate: TimePoint | None
    dateOfLastUpdate: TimePoint | None
    duration: int | None
    durationUnit: str | None
    durationType: str | None
    overdue: bool | None
    closeToDeadLine: bool | None
    notAcceptedInTime: bool | None
    inFavorites: bool | None
    isSummary: bool | None
    isSequential: bool | None
    assignees: PeopleResponse | None
    participants: PeopleResponse | None
    auditors: PeopleResponse | None
    recurrence: dict | None
    isDeleted: bool | None
    customFieldData: list[CustomFieldDataResponse] | None
    files: list[FileResponse] | None


class TaskListResponse(BaseApiResponse):
    tasks: list[TaskResponse]

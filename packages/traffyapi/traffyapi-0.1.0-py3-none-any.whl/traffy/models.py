from typing import TypedDict, List, Union


class Task(TypedDict):
    id: str
    title: str
    link: str
    image_url: str


class GetTraffyTasksResponse(TypedDict):
    success: bool
    message: str
    tasks: List[Task]


class CheckTraffyTaskNotCompleted(TypedDict):
    is_completed: bool
    token: None


class CheckTraffyTaskCompleted(TypedDict):
    is_completed: bool
    token: str


CheckTraffyTaskResponse = Union[CheckTraffyTaskNotCompleted, CheckTraffyTaskCompleted]

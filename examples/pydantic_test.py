from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from typing import List, Union
from enum import Enum


class URLModel(BaseModel):
    url: str = Field(
        ...,
        description="A valid URL that points to a resource.",
    )
    display: bool = False


class SingleModel(BaseModel):
    name: str
    age: int
    weight: float
    signup_date: Optional[datetime]
    bio: str = Field(
        default="No bio provided", description="A short biography of the user."
    )
    links: list[URLModel] | None = Field(description="A list of URL objects.")


class PushReason(BaseModel):
    user: str = Field(
        ...,
        description="The user who initiated the push.",
    )
    reason: str = Field()


def push_to_database(
    database_id: int,
    datas: List[SingleModel],
    reason: Union[PushReason, None],
    update_time: datetime,
) -> str:
    return f"Data pushed to database {database_id} with {len(datas)} records. Reason: {reason.reason if reason else 'No reason provided'}. Update time: {update_time}."

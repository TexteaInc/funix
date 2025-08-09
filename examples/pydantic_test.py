from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from funix import funix, pydantic_ui


@pydantic_ui(
    title="model",
    layout=[
        [{"argument": "url", "width": 0.5}, {"argument": "display", "width": 0.5}],
    ],
)
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
    links: list[URLModel] = Field(description="A list of URL objects.")


class PushReason(BaseModel):
    user: str
    reason: str = Field()
    other_model: SingleModel


def where_is_the_datetime(
    t: PushReason = PushReason(
        user="shionsan",
        reason="Please",
        other_model=SingleModel(
            name="shionsan",
            age=1,
            weight=2.0,
            signup_date=datetime.now(),
            bio="No bio provided",
            links=[URLModel(url="https://www.google.com", display=True)],
        ),
    )
) -> str:
    return f"User: {t.user}, Reason: {t.reason}, Time: {datetime.now()}"

# Simply importing pydantic works, but accessing pydantic.BaseModel causes a segfault

import pydantic


class Model(pydantic.BaseModel):
    name: str
    age: int


person = Model(name="John", age=30)
person.model_dump()

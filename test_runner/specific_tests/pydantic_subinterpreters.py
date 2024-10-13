# Simply importing pydantic works in a subinterpreter, but when we try to create a model
# we run into ImportError('module _pydantic_core does not support loading in subinterpreters')

import pydantic


class Model(pydantic.BaseModel):
    name: str
    age: int


person = Model(name="John", age=30)
person.model_dump()

from pydantic import BaseModel


class ModelType(BaseModel):
    id: int
    model_type: str

    class Config:
        orm_mode = True


class Model(BaseModel):
    id: int
    name: str
    model_type_id: int

    class Config:
        orm_mode = True


class GetModelItem(Model):
    model_type: str


class GetModel(BaseModel):
    items: list[GetModelItem]


class PostModel(BaseModel):
    model_name: str
    model_type: str


class PostModelResponse(BaseModel):
    model_id: int


class GetModelType(BaseModel):
    items: list[ModelType]

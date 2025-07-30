from pydantic import BaseModel, Field
from enum import Enum, auto


class ModelType(str, Enum):
    BSRGan = "BSRGan"
    RealESRGan = "RealESRGan"

    @staticmethod
    def from_str(s):
        try:
            return ModelType[s]
        except KeyError:
            raise ValueError(f"{s} is not a valid ModelType")


class Payload(BaseModel):
    data: list = Field(
        ...,
        title='Represent the input numpy array.')

    type: ModelType = Field(
        ...,
        title=f'Represent the model type. options: {[e.name for e in ModelType]}')

    model: str = Field(
        ...,
        title='Represent the pre-trained model path.')

    max_value: int = Field(
        ...,
        title='Represent the maximum value of the input numpy array value.')

    up_scale: int = Field(
        ...,
        title='Represent the up-scale value.')

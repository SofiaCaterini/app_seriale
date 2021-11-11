from pydantic import BaseModel


class Device(BaseModel):
    addr: int
    sensor_type: str
    value: int

    class Config:
        orm_mode = True
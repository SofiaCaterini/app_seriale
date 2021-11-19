
from typing import List, Optional
from pydantic import BaseModel


class DeviceBase(BaseModel):
    id: str
    status: str
    time_last_measurement: str
    sensor_type: str



class DeviceCreate(DeviceBase):
    pass


class Device(DeviceBase):
    pass

    class Config:
        orm_mode = True


class Transaction(BaseModel):
    status: bool
    message: str
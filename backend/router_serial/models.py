from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from .database import Base


class Device(Base):
    __tablename__ = "Devices"

    id = Column(String, primary_key=True, index=True)
    # name = Column(String(100))
    status = Column(String, index=True)
    time_last_measurement = Column(String, index=True)
    # x_location = Column(String(255))
    # y_location = Column(String(255))
    sensor_type = Column(String(100))
    # characteristics = Column(String(255))

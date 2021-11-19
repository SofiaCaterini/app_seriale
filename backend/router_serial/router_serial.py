import asyncio
import sys
import traceback
import time
import datetime

import serial
from fastapi import FastAPI
from typing import List

from sqlalchemy import true
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from serial.threaded import LineReader, ReaderThread
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from . import models, schemas, crud
from .database import Session, engine
from .models import Device

models.Base.metadata.create_all(bind=engine)

q = asyncio.Queue()
router = FastAPI()

Devices = []

router.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


# Dependency
def get_db():
    try:
        db = Session()
        yield db
    finally:
        db.close()


class PrintLines(LineReader):
    _fut = None

    def connection_made(self, transport):
        super(PrintLines, self).connection_made(transport)
        sys.stdout.write('port opened\n')

    def handle_line(self, data):
        sys.stdout.write('line received: {}\n'.format(repr(data)))
        if data.find(" Appli_Generic_PowerOnOff_Set callback received") > 0:
            print("~~ writing")
            # write(b"hello2\r")

        if "ANS" in data:
            # print("Answer!")
            if self._fut is not None:
                self._fut.set_result(data)
                self._fut = None
            else:
                pass
        if "EVT" in data:
            # asyncio.run(start_count())

            # print("Evt!")
            # prende lista device attivi
            addrstr = "srcAddr = "
            # print(data[(data.find(addrstr) + len(addrstr)):(data.find(addrstr) + len(addrstr) + 2)])
            devAttivo = data[(data.find(addrstr) + len(addrstr)):(data.find(addrstr) + len(addrstr) + 2)]
            valuestr = "value = "
            # print(data[(data.find(valuestr) + len(valuestr)):(data.find(valuestr) + len(valuestr) + 2)])
            valueactual = data[(data.find(valuestr) + len(valuestr)):(data.find(valuestr) + len(valuestr) + 2)]

            typestr = "type = "
            typeactual = data[(data.find(typestr) + len(typestr)):(data.find(typestr) + len(typestr) + 4)]
            time_misura = time.localtime()
            newDevice = Device(id=devAttivo, status="ON", time_last_measurement=time_as_string(time_misura),
                               sensor_type=typeactual)
            # Devices.append(newDevice)

            Devices.append(newDevice)
            for index, dev in enumerate(Devices):
                if dev.id == devAttivo and dev.time_last_measurement == time_as_string(time_misura):
                    with Session() as session:
                        create(session, Device, newDevice)
                if dev.id == devAttivo and dev.time_last_measurement != time_as_string(time_misura):
                    Devices[index] = newDevice
                    Devices.pop(len(Devices) - 1)
                    with Session() as session:
                        update(session, devAttivo, time_as_string(time_misura))

            print(Devices)
            # manda gli eventi a mqtt

        else:

            pass

    def connection_lost(self, exc):
        if exc:
            traceback.print_exc(exc)
        sys.stdout.write('port closed\n')

    def send_command(self, cmd):
        if self._fut:  # (se il future non è vuoto)
            raise ValueError("called twice")
        self._fut = asyncio.get_running_loop().create_future()
        write(self, cmd.encode('ascii'))
        return self._fut


async def consumer():
    ser = serial.serial_for_url('com4',
                                baudrate=115200,
                                rtscts=True,
                                bytesize=serial.EIGHTBITS,
                                parity=serial.PARITY_NONE,
                                stopbits=serial.STOPBITS_ONE)
    ser.exclusive = True

    with ReaderThread(ser, PrintLines) as protocol:
        while True:
            task = await q.get()
            print("task:", task["data"])
            res = await protocol.send_command(task["data"])
            task["fut"].set_result(res)


def write(protocol, data):
    for b in data:
        b = bytes([b])
        # print("w", b)
        protocol.transport.write(b)
        time.sleep(0.01)


@router.get("/")
def main():
    return RedirectResponse(url="/docs/")


@router.on_event("startup")
def start_consumer():
    asyncio.create_task(consumer())
    asyncio.create_task(control_status(20, Devices))


@router.get("/devices/", response_model=List[schemas.Device])
def read_devices(db: Session = Depends(get_db)):
    items = crud.get_devices(db)
    return items


@router.get("/test_future")
async def test_future():
    task = {
        "data": "atcl 0003 8202 01 00\r",
        "fut": asyncio.get_running_loop().create_future()}
    await q.put(task)
    print(await task["fut"])


@router.get("/devices/{id}", response_model=schemas.Device)
async def read_device(id: str, db: Session = Depends(get_db)):
    item = crud.get_device(db=db, id=id)
    print(id)
    task = {
        "data": "atcl 00" + id + " 8202 01 00\r",
        "fut": asyncio.get_running_loop().create_future()}
    await q.put(task)
    print(await task["fut"])


def create(session, model, Device):
    instance = session.query(model).filter_by(id=Device.id).first()
    if instance:
        pass
    else:
        instance = Device
        session.add(instance)
        session.commit()


def update(session, id, str):
    if session.query(models.Device).get(id):
        session.query(models.Device).filter_by(id=id).update({'time_last_measurement': str})
        session.flush()
        session.commit()
        return {"status": True, "message": f"Record {id} deleted"}
    else:
        return {"status": False, "message": "No such record"}


def update_status(session, id, str):
    if session.query(models.Device).get(id):
        session.query(models.Device).filter_by(id=id).update({'status': str})
        session.flush()
        session.commit()
        return {"status": True, "message": f"Record {id} deleted"}
    else:
        return {"status": False, "message": "No such record"}


def time_as_string(actual_time):
    time_string = time.strftime("%d/%m/%Y, %H:%M:%S", actual_time)
    return time_string


def sec_between_time(timestr1, timestr2):
    # ate = time_as_string(time.localtime())
    # convert string to datetimeformat
    date1 = datetime.datetime.strptime(timestr1, "%d/%m/%Y, %H:%M:%S")
    date2 = datetime.datetime.strptime(timestr2, "%d/%m/%Y, %H:%M:%S")
    # convert datetime to timestamp
    time1 = datetime.datetime.timestamp(date1)
    time2 = datetime.datetime.timestamp(date2)
    time1 = datetime.datetime.fromtimestamp(time1)
    time2 = datetime.datetime.fromtimestamp(time2)
    time_difference = time2 - time1
    return time_difference.total_seconds()


async def control_status(delay, listdev):
    while true:
        await asyncio.sleep(delay)
        for index, dev in enumerate(listdev):
            if sec_between_time(dev.time_last_measurement, time_as_string(time.localtime())) > delay / 2:
                print("off")
                with Session() as session:
                    update_status(session, dev.id, "OFF")
            else:
                print("on")
                with Session() as session:
                    update_status(session, dev.id, "ON")
        print("check")

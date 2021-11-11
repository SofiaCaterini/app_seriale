import asyncio
import sys
import traceback
import time
import serial
from fastapi import FastAPI
from serial.threaded import LineReader, ReaderThread
from starlette.responses import RedirectResponse

q = asyncio.Queue()
router = FastAPI()

DeviceAttivi = []
Event = {}
Events = []


class PrintLines(LineReader):
    _fut = None

    def connection_made(self, transport):
        super(PrintLines, self).connection_made(transport)
        sys.stdout.write('port opened\n')
        # write(self, b"atcl 0003 8202 00 00\r")

    # def data_received(self, data):
    # sys.stdout.write('data: {}\n'.format(repr(data)))

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
            # print("Evt!")
            # prende lista device attivi
            addrstr = "srcAddr = "
            # print(data[(data.find(addrstr) + len(addrstr)):(data.find(addrstr) + len(addrstr) + 2)])
            devAttivo = data[(data.find(addrstr) + len(addrstr)):(data.find(addrstr) + len(addrstr) + 2)]
            if devAttivo not in DeviceAttivi:
                DeviceAttivi.append(devAttivo)
            print(DeviceAttivi)
            # manda gli eventi a mqtt
            valuestr = "value = "
            # print(data[(data.find(valuestr) + len(valuestr)):(data.find(valuestr) + len(valuestr) + 2)])
            valueactual = data[(data.find(valuestr) + len(valuestr)):(data.find(valuestr) + len(valuestr) + 2)]

            idstr = "type = "
            idactual = data[(data.find(idstr) + len(idstr)):(data.find(idstr) + len(idstr) + 4)]
            new = Event.copy()
            new["Id"] = "Sensor"
            new["Addr"] = devAttivo
            new["Type"] = idactual
            new["Value"] = valueactual
            # if Event["Addr"] not in Events:
            if new not in Events:
                Events.append(new)
            # se è presente un evento che arriva dallo stesso device ma con valore diverso
            for index, value in enumerate(Events):
                if value["Addr"] == new["Addr"] and value["Value"] != new["Value"]:
                    Events[index] = new
                    Events.remove(new)
            print(Events)

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
    # print("pippo")


@router.get("/test_future")
async def test_future():
    task = {
        "data": "atcl 0003 8202 01 00\r",
        "fut": asyncio.get_running_loop().create_future()}
    await q.put(task)
    print(await task["fut"])

import asyncio

import serial_asyncio
from fastapi import FastAPI
from starlette.responses import RedirectResponse

q = asyncio.Queue()
router = FastAPI()


class InputProtocol(asyncio.Protocol):
    _fut = None

    def connection_made(self, transport):
        self.transport = transport
        print("connection made")
        transport.serial.rts = False
        transport.write('prova'.encode())
        self.transport.write("atcl 0003 8202 01 00\n".replace('\n', '').encode('utf8'))
        transport.write(b'\r\nHello, World!\r\n')

    def connection_lost(self, exc):
        pass  # qui ti segni che è sconnesso

    def data_received(self, data):
        print('data received', repr(data.rstrip().strip(b'\r').decode()))
        # self.transport.write("atcl 0003 8202 01 00\n".replace('\n', '').encode('utf8'))
        # qui gestisci i dati in arrivo
        '''if is_result(data):
            if self._fut is not None:
                self._fut.set_result(parse_result(data))
                self._fut = None
            else:
                pass
        else:
            # some event from sensors handle here
            pass'''

    def send_command(self, cmd):
        if self._fut:
            raise ValueError("called twice")

        print("cmd", cmd.encode('utf8'))
        print("cmdnotencode", cmd)
        self._fut = asyncio.get_running_loop().create_future()
        self.transport.write(cmd.encode('utf8'))
        return self._fut


async def consumer():
    transport, protocol = await serial_asyncio.create_serial_connection(asyncio.get_running_loop(), InputProtocol,
                                                                        url='COM4', baudrate=115200)

    while True:
        task = await q.get()
        print("task:", task["data"])
        await protocol.send_command(task["data"])
        task["fut"].set_result("res: ok")


@router.get("/")
def main():
    return RedirectResponse(url="/docs/")


@router.on_event("startup")
def start_consumer():
    asyncio.create_task(consumer())


@router.get("/test_future")
async def test_future():
    task = {
        "data": "atcl 0003 8202 01 00\n",
        "fut": asyncio.get_running_loop().create_future()}
    await q.put(task)
    print(await task["fut"])

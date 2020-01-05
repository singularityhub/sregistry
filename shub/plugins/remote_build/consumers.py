from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.consumer import AsyncConsumer
from channels.exceptions import StopConsumer

import asyncio
import os

class BuildConsumer(AsyncConsumer):
    async def websocket_connect(self, message):
        await self.accept()
        await self.receive()
        await self.close(code=1000)


    async def close(self, code=None):
        """
        Closes the WebSocket from the server end
        """
        if code is not None and code is not True:
            await super().send({"type": "websocket.close", "code": code})
        else:
            await super().send({"type": "websocket.CloseNormalClosure"})

    async def accept(self):
        """
        Accepts an incoming socket
        """
        await self.send({"type": "websocket.accept", "text": "data"})

    async def websocket_disconnect(self, message):
        """
        Called when a WebSocket connection is closed. Base level so you don't
        need to call super() all the time.
        """
        # TODO: group leaving
        await self.disconnect(message["code"])
        raise StopConsumer()

    async def disconnect(self, code):
        """
        Called when a WebSocket connection is closed.
        """
        pass

    async def websocket_receive(self, message):
        await self.receive(text_data=message["text"])

    async def receive(self, text_data=None, bytes_data=None):
        """
        Called with a decoded WebSocket frame.
        """
        self.buildid = self.scope["url_route"]["kwargs"]["buildid"]
        self.specfile = '/tmp/.{}.spec'.format(self.buildid)
        self.specfile = os.path.join(settings.UPLOAD_PATH, self.buildid + ".spec")
        self.filename = os.path.join(settings.UPLOAD_PATH, self.buildid + ".sif")

        cmd = 'singularity build -F {} {}'.format(self.filename, self.specfile)
#        cmd = 'dd if=/dev/zero of={} bs=1k count=10'.format(self.filename)
        text_data, err = await self.run(cmd)
        await self.send({
            "type": "websocket.send",
            "text": text_data
        })
        await self.close()

    async def run(self, cmd):
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        stdout, stderr = await proc.communicate()
        return stdout.rstrip().decode(), stderr



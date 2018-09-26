import time
import asyncio
import collections

from pyppeteer import launch
from functools import partial
from browsBase import Interface

class Headless(Interface):
    """
    """

    @staticmethod
    def _async_trigger(event_exec, target_fn, *args, **kwargs):
        """
        """
        event_exec(target_fn(*args, **kwargs))

    def __init__(self, *args, **kwargs):
        """
        """
        self._browser=None
        self._arguments=args
        self._proxy=kwargs.get("proxy")
        self._binary=kwargs.get("binaryPath")
        self._download=kwargs.get("downloadPath")
        self._user_data_dir=kwargs.get("user_data_dir")
        self._remote_debugging_port=kwargs.get("remote_debugging_port")
        self._loop=asyncio.get_event_loop()
        self._build_methods()
        self._startDriver()

    def _build_methods(self):
        """
        """
        for bindis in dir(self):
            if not bindis.startswith("async_"):continue
            name=bindis.replace("async_", "")
            target_fn=getattr(self, bindis)
            partial_exec=partial(Headless._async_trigger,
                self._loop.run_until_complete, target_fn)
            setattr(self, name, partial_exec)

    async def async__startDriver(self):
        """
        """
        options={
            "headless":True,
            "args":[
                "--window-size=1920,1080",

            ]
        }
        if self._binary:
            options["executablePath"]=self._binary
        if self._user_data_dir:
            options["userDataDir"]=self._user_data_dir
        self._browser = await launch(options)
        self._page = await self._browser.newPage()
        await self._page.setUserAgent(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) "\
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 "\
            "Safari/537.36")

    async def async_get(self, targetUri):
        """
        """
        if not self._browser:
            self._startDriver()
        await self._page.goto(targetUri)
        print(await self._page.content())

    def close(self):
        """
        """
        self._browser.close()
        self._loop.close()

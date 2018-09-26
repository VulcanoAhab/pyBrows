import time
import asyncio
import collections
from pyppeteer import launch

class Headless(Interface):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        """
        self._arguments=args
        self._binary=kwargs.get("binaryPath")
        self._download=kwargs.get("downloadPath")
        self._proxy=kwargs.get("proxy")
        self._remote_debugging_port=kwargs.get("remote_debugging_port")
        self._user_data_dir=kwargs.get("user_data_dir")

        self._startDriver()

    def _startDriver(self):
        """
        """
        options={"headless":True, "args":["--window-size=1920,1080",]}
        if self._binary:
            options["executablePath"]="/usr/local/bin/chromedriver"
        if self._user_data_dir:
            options["userDataDir"]=_USER_DIR
        self._browser = await launch(options)
        self._page = await self._browser.newPage()

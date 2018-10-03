import time
import asyncio
import datetime
import collections

from pyppeteer import launch
from functools import partial
from .browsBase import Interface

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
        self._title={}
        self._source={}
        self._cookies={}
        self._results=[]
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

    def add_toResults(self, resultDict):
        """
        """
        resultDict.update({
            "url":self._page.url,
            "dateTime":datetime.datetime.utcnow().isoformat(),
        })
        self._results.append(resultDict)

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

    @property
    def currentUrl(self):
        """
        """
        return  self._page.url

    @property
    def title(self):
        """
        """
        if (not self._page.url in self._title
           or not self._title[self._page.url]):
           self.page_title()
        return self._title[self._page.url]

    async def async_page_source(self):
        """
        """
        self._source[self._page.url]= await self._page.content()

    async def async_page_title(self):
        """
        """
        if not self._page.url in self._title:
            self._title[self._page.url]=await self._page.title()

    async def async_cookies(self):
        """
        """
        if not self._page.url in self._cookies:
            self._cookies[self._page.url]==await self._page.cookies()

    async def async_saveScreenshot(self, output, **data):
        """
        """
        out_form=data.get("output_format", "png") #default png
        if out_form not in  ["png", "pdf"]:
            msg="[-] Only PNG and PDF formats implemented so far"
            raise NotImplemented(msg)
        if out_form == "png":
            await self._page.screenshot({"path": output})
        else:
            await self._page.pdf({"path": output})

    async def async_get(self, targetUri):
        """
        """
        await self._page.goto(targetUri)

    async def async_xpath(self, xpath_pattern, target_value=None):
        """
        """
        elements=await self._page.xpath(xpath_pattern)
        if not target_value:
            for n,element in enumerate(elements):
                self._results.append({
                    "value":element,
                    "target_value":target_value,
                    "selector":xpath_pattern,
                    "index":n,
                })
        elif target_value and target_value == "text_content":
            js_content="(element) => element.textContent"
        elif target_value and target_value == "href":
            js_content="(element) => element.getAttribute('href')"
        for n,element in enumerate(elements):
            value = await self._page.evaluate(js_content,element)
            self._results.append({
                "value":value,
                "target_value":target_value,
                "selector":xpath_pattern,
                "index":n,
            })

    def results_by_selector(self, selector_pattern):
        """
        """
        return [ r for r in self._results
                 if r["selector"]==selector_pattern]

    async def async_close(self):
        """
        """
        await self._page.close()
        await self._browser.close()

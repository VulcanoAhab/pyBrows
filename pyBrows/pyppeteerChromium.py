import time
import asyncio
import datetime
import collections

from string import Template
from pyppeteer import launch
from functools import partial
from .browsBase import Interface
from pyppeteer.errors import NetworkError

class Headless(Interface):
    """
    """

    _timeout=30000

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
        self._handles={}
        self._browser=None
        self._arguments=args
        self._proxy=kwargs.get("proxy")
        self._binary=kwargs.get("binaryPath")
        self._download=kwargs.get("downloadPath")
        self._headless=kwargs.get("headless", True)
        self._user_data_dir=kwargs.get("user_data_dir")
        self._remote_debugging_port=kwargs.get("remote_debugging_port")
        self._results=collections.defaultdict(list)
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
        self._results[self._page.url].append(resultDict)

    async def async__startDriver(self):
        """
        """
        options={
            "headless":self._headless,
            "args":[
                # "--proxy-server='direct://",
                # "--proxy-bypass-list=*",
                # "--no-sandbox",
                # "--disable-setuid-sandbox",
                # "--ignore-certificate-errors",
                "--disable-web-security",
                "--no-sandbox",
            ]
        }
        if self._binary:
            options["executablePath"]=self._binary
        if self._user_data_dir:
            options["userDataDir"]=self._user_data_dir
        self._browser = await launch(options)
        self._page = await self._browser.newPage()
        self._page.setDefaultNavigationTimeout(self._timeout)
        await self._page.setViewport({"width":1366,"height":768})
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

    @property
    def pageSource(self):
        """
        """
        if (not self._page.url in self._source
           or not self._source[self._page.url]):
           self.page_source()
        return self._source[self._page.url]


    async def async_renew_page(self):
        """
        """
        if not self._page.isClosed():
            await self._page.close()
        self._page = await self._browser.newPage()
        self._page.setDefaultNavigationTimeout(self._timeout)

    async def async_page_source(self):
        """
        """
        if not self._page.url in self._source:
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

    async def async_saveScreenshot(self, output):
        """
        """
        out_form=output.split(".")[-1].strip()
        if out_form not in  ["png", "pdf"]:
            msg="[-] Only PNG and PDF formats implemented so far"
            raise NotImplemented(msg)
        if out_form == "png":
            await self._page.screenshot({"path": output})
        else:
            await self._page.pdf({"path": output})

    async def async_get(self, targetUri, options={}):
        """
        """
        await self._page.goto(targetUri, options)

    async def async_go_back(self):
        """
        """
        await self._page.goBack()

    async def async_click_onElement(self, xpath_pattern,
                                          not_hrefs=[],
                                          not_hrefs_patterns=[],
                                          only_first=True):
        """
        """
        action="fail"
        js_base=Template("""
        function(element){
            var not_hrefs=$not_hrefs;
            var not_hrefs_patterns=$not_hrefs_patterns;
            var href=element.getAttribute("href");
            if (not_hrefs && not_hrefs.indexOf(href) > -1) {
                return {
                    "status":"not_done",
                    "msg":"Has not_ref: "+href}
            }
            if (not_hrefs_patterns){
                for (i=0;i<not_hrefs_patterns.length;++i){
                    var pattern=not_hrefs_patterns[i];
                    if (href.indexOf(pattern) > -1) {
                        return {
                        "status":"not_done",
                        "msg":"Has not_href_pattern: "+pattern
                        }
                    }
                }
            }
            element.click();
        }
        """)
        js_click=js_base.substitute(not_hrefs=not_hrefs,
                                    not_hrefs_patterns=not_hrefs_patterns)
        elements=await self._page.xpath(xpath_pattern)
        if elements:
            for n,element in enumerate(elements):

                failDict=await self._page.evaluate(js_click, element)
                if not failDict:
                    await self._page.waitForNavigation()
                    action="sucess"
                self._results[self._page.url].append({
                    "click":action,
                    "selector":xpath_pattern,
                    "index":n,
                    "failDict":failDict
                    })

                if only_first:break
                action="fail"

        else:
            self._results[self._page.url].append({
                "click":action,
                "selector":xpath_pattern,
                })

    async def async_evaluate(self, js_content, js_id):
        """
        """
        value = await self._page.evaluate(js_content)
        self._results[self._page.url].append({
            "value":value,
            "js_id":js_id,
            "selector":None,
        })

    async def async_evaluate_handle(self, js_content, js_id):
        """
        """
        value=await self._page.evaluateHandle(js_content)
        self._handles[js_id]=value

    async def async_evaluate_onElement(self, xpath_pattern, js_content,
                                                    only_visible=False):
        """
        """
        only_visible="""
        function(element) {
            var rect=element.getBoundingClientRect();
            if (rect.height ==0 || rect.width==0){
                return 0
            }
            return 1
        }
        """
        elements=await self._page.xpath(xpath_pattern)
        if not elements: return
        for element in elements:
            if only_visible:
                is_visible = await self._page.evaluate(only_visible,
                                                            element)
                if not is_visible:continue
            value = await self._page.evaluate(js_content,element)
            self._results[self._page.url].append({
                "value":value,
                "target_value":None,
                "selector":xpath_pattern,
                "js_id":None,
                "index":0,
            })
            break

    async def async_evaluate_onElements(self, xpath_pattern, js_content):
        """
        """
        elements=await self._page.xpath(xpath_pattern)
        if elements:
            for n,element in enumerate(elements):
                value = await self._page.evaluate(js_content,element)
                self._results[self._page.url].append({
                    "value":value,
                    "target_value":None,
                    "selector":xpath_pattern,
                    "js_id":None,
                    "index":n,
                })

    async def async_xpath(self, xpath_pattern, target_value=None):
        """
        """
        elements=await self._page.xpath(xpath_pattern)
        if not elements:return
        if not target_value:
            for n,element in enumerate(elements):
                self._results[self._page.url].append({
                    "element":element,
                    "target_value":target_value,
                    "selector":xpath_pattern,
                    "js_id":None,
                    "index":n,
                })
            return
        if target_value and target_value == "text_content":
            js_content="(element) => element.textContent"
        if target_value and target_value == "href":
            js_content="(element) => element.getAttribute('href')"
        for n,element in enumerate(elements):
            value = await self._page.evaluate(js_content,element)
            self._results[self._page.url].append({
                "value":value,
                "target_value":target_value,
                "selector":xpath_pattern,
                "js_id":None,
                "index":n,
            })

    def results_by_selector(self, selector_pattern):
        """
        """
        return [ r for r in self._results[self._page.url]
                 if r.get("selector", "empty")==selector_pattern]

    def results_by_js_id(self, js_id):
        """
        """
        return [ r for r in self._results[self._page.url]
                 if r.get("js_id",0)==js_id]

    async def async_close(self):
        """
        """
        if not self._page.isClosed():
            await self._page.close()
        await self._browser.close()

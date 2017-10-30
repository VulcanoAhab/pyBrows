import requests
from selenium import webdriver
from .browsBase import Interface
from .headers import chromeForMac
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities



# == browsers base
class Vanilla(Interface):
    """
    """
    _headers={}

    @staticmethod
    def _extract(elements, extractor, targetName=None):
        """
        """
        response=[]
        if extractor in ["text", "text_content"]:
            if not targetName:
                targetName="text"
            for n,e in enumerate(elements):
                response.append({targetName:e.text, "index":n})
        elif extractor == "generic_link":
            if not targetName:
                targetName="generic_link"
            for n,e in enumerate(elements):
                for p in ["src","data-src","href"]:
                    link=e.get_attribute(p)
                    if not link:continue
                    response.append({targetName:link, "index":n})
        else:
            for n,e in enumerate(elements):
                value=e.get_attribute(extractor)
                if not value:continue
                if not targetName:
                    targetName=extractor
                response.append({targetName:value, "index":n})
        return response

    def __init__(self, desired_caps={}, service_args=[], headers={}, **kwargs):
        """
        """
        self._startDriver(desired_caps, service_args, **kwargs)
        if headers:self._setHeaders(headers)
        elif self._headers:self._setHeaders(self._headers)

    def _setHeaders(self, headers):
        """
        """
        toFilter=['Accept-Encoding',] #avoid phantom bug
        finalHeaders={k:v for k,v in headers.items()
                          if k not in toFilter}
        header_scrit="""
        this.customHeaders = {headers};
        """.format(headers=str(headers))
        self._driver_script(script=header_scrit)

    def _driver_script(self, script, args=[]):
        """
        """
        self._wd.execute('executePhantomScript',
            {'script': script, 'args': args})

    def _startDriver(self, desired_caps={}, service_args=[]):
        """
        options
        -------
        --proxy=XXX.XXX.XXX.XXX:PORT
        --proxy-type=http
        --web-security=false
        """
        serviceDefaults=[
            '--ignore-ssl-errors=yes',
        ]
        desiredDefaults={
            "webdriver.log.driver":"INFO"
        }
        #add defaults
        desired_caps.update(desiredDefaults)
        desired_caps.update(DesiredCapabilities.PHANTOMJS)
        service_args.extend(serviceDefaults)
        #start driver
        self._wd=webdriver.PhantomJS(desired_capabilities=desired_caps,
                                     service_args=service_args)
        #set window size
        self._wd.set_window_size(1124, 850)
        #add command to run scripts on the page env
        phantom_exc_uri='/session/$sessionId/phantom/execute'
        cmds=self._wd.command_executor._commands
        cmds['executePhantomScript'] = ('POST', phantom_exc_uri)
        #log headers
        headers_script="""
        this.onResourceReceived = function(response) {
            for (var i=0;i<response.headers.length;++i){
                console.log('#HEADERS', response.headers[i]);
            }
        }.bind(this);
        """
        self._driver_script(headers_script)

    @property
    def pageSource(self):
        """
        """
        return self._wd.page_source

    @property
    def currentUrl(self):
        """
        """
        return self._wd.current_url

    @property
    def title(self):
        """
        """
        return self._wd.title

    def setLoadTimeout(self, timeout=30):
        """
        """
        self._wd.set_page_load_timeout(timeout)

    def setInteractionTimeout(self, timeout=30):
        """
        """
        self._wd.implicitly_wait(30)

    def get(self, targetUri):
        """
        """
        self._wd.get(targetUri)

    def xpath(self, selector, extractor=None, targetName=None):
        """
        """
        elements=self._wd.find_elements_by_xpath(selector)
        if  not extractor: return elements
        return Vanilla._extract(elements, extractor, targetName=targetName)

    def elementByName(self, elementName, extractor=None, targetName=None):
        """
        """
        elements=self._wd.find_elements_by_name(elementName)
        if  not extractor: return elements
        return self._extract(elements, extractor, targetName=targetName)

    def sendKeysByName(self, **data):
        """
        """
        _reqs=["elementName", "keysToSend"]
        if not all([e in data for e in _reqs]):
            raise AttributeError("[-] {} are "\
                                 "required".format(",".join(_reqs)))
        elementName=data["elementName"]
        keysToSend=data["keysToSend"]
        elementIndex=data.get("elementIndex",0) #default 0
        targetEl=self.elementByName(elementName)
        if targetEl is None:
            raise Exception("[-] Unable to "\
                            "find element: {}".format(elementName))
        targetEl[elementIndex].send_keys(keysToSend)

    def saveScreenshot(self, **data):
        """
        """
        if not data.get("output"):
            raise AttributeError("[-] Output is required")
        imgType=data.get("imgType", "png") #default png
        if imgType != "png":
            raise NotImplemented("[-] Only PNG type implemented so far")
        self._wd.save_screenshot(data["output"])

    def getScreenshot(self, imgType="base64"):
        """
        """
        if imgType != "base64":
            raise NotImplemented("[ONLY BASE64 IMPLEMENTED]")
        return self._wd.get_screenshot_as_base64()

    def savePageSource(self, **data):
        """
        """
        if not data.get("ouput"):
            raise AttributeError("[-] Output is required")
        page_source=self.page_source
        fd=open(data["output"], "w")
        fd.write(page_source)
        fd.close()

    def runConsoleScript(self, scriptIn):
        """
        """
        return self._wd.execute_script(scriptIn)

    def headlessDownloadFile(self, targetUrl, testForCaptcha=None):
        """
        work-around for headless mode
        -----------------------------
        testForCaptcha should be a function
        to deal with captchas :: receives the driver
        as paramater

        returns
        --------
        file binary
        """
        self._wd.get(targetUrl)
        if testForCaptcha:testForCaptcha()
        #time to download
        session = requests.Session()
        cookies = self._wd.get_cookies()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        response = session.get(targetUrl)
        return response.content

    def back(self):
        """
        """
        self._wd.back()

    def close(self):
        """
        """
        self._wd.quit()



# === browsers type
class Chrome(Vanilla):
    """
    """
    _os="mac"
    _oses={"mac":chromeForMac.HEADERS,}
    _headers=_oses[_os]

    def __init__(self, desired_caps={}, service_args=[], headers={}, **kwargs):
        """
        """
        super().__init__(desired_caps=desired_caps,
                         service_args=service_args,
                         headers=headers)
        if not kwargs.get("noWaits"):
            self.setLoadTimeout() #default to 30s
            self.setInteractionTimeout() #default to 30s

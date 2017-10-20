import requests
from .browsBase import Interface
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Canary(Interface):
    """
    """

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

    def __init__(self, binaryPath, arguments, downloadPath):
        """
        """
        self._binary=binaryPath
        self._arguments=arguments
        self._download=downloadPath
        self._startDriver()

    def _startDriver(self):
        """
        """
        #add defaults
        options = webdriver.ChromeOptions()
        options.binary_location=self._binary
        options.add_experimental_option("prefs", {
            "download.default_directory": self._download,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,
            "Page.setDownloadBehavior":"allow",
        })
        for argument in self._arguments:options.add_argument(argument)
        options.add_argument("--window-size=1920,1080")

        #start driver
        self._wd=webdriver.Chrome(chrome_options=options)


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

    def saveScreenshot(self, output=None, **data):
        """
        """
        if not output:
            raise AttributeError("[-] Output is required")
        imgType=data.get("imgType", "png") #default png
        if imgType != "png":
            raise NotImplemented("[-] Only PNG type implemented so far")
        self._wd.save_screenshot(output)

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
        if testForCaptcha:testForCaptcha(self._wd)
        resolvedUrl=self._wd.current_url
        #time to download
        session = requests.Session()
        cookies = browser.get_cookies()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        response = session.get(resolvedUrl)
        return response.content

    def back(self):
        """
        """
        self._wd.back()

    def close(self):
        """
        """
        self._wd.close()

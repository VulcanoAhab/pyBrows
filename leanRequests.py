
import requests
from .browsBase import Interface
from lxml import html

class Vanilla(Interface):
    """
    """
    def __init__(self, headers={}):
        """
        """
        self._wd=resquests.Session()
        self._wd.headers=headers
        self._res=None
        self._lx=None

    @property
    def pageSource(self):
        """
        """
        return self._wd.text

    @property
    def title(self, *args, **kwargs):
        """
        """
        raise NotImplemented()

    @property
    def currentUrl(self):
        """
        """
        return self._res.url

    def get(self, url, **kwargs):
        """
        """
        self._res=self._wd.get(url, **kwargs)
        #self._lx=html.fromstring(self._res.text)

    def binContent(self):
        """
        """
        return self._res.content

    def post(self, *args, **kwargs):
        """
        """
        raise NotImplemented()

    def xpath(self, selector, extractor=None, targetName=None):
        """
        """
        raise NotImplemented()

    def elementByName(self, elementName, extractor=None, targetName=None):
        """
        """
        raise NotImplemented()

    def saveScreenshot(self, **data):
        """
        params
        -------
        output[required] -> filePath or DB
        """
        raise NotImplemented()

    def savePageSource(self, **data):
        """
        params
        -------
        output -> fileName or DB
        """
        raise NotImplemented()

    def getScreenshot(self, **data):
        """
        params
        -------
        imgType -> png, base64. Default:base64
        """
        raise NotImplemented()

    def sendKeysByName(self, **data):
        """
        params
        ------
        elementName[required]
        keysToSend [required]
        elementIndex [required]
        """
        raise NotImplemented()

    def close(self):
        """
        """
        raise NotImplemented()

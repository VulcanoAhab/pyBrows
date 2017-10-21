
class Interface:
    """
    """

    @property
    def pageSource(self):
        """
        """
        raise NotImplemented()

    @property
    def title(self, *args, **kwargs):
        """
        """
        raise NotImplemented()

    @property
    def currentUrl(self, *args, **kwargs):
        """
        """
        raise NotImplemented()

    def get(self, *args, **kwargs):
        """
        """
        raise NotImplemented()

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

    def headlessDownloadFile(self, **data):
        """
        """
        raise NotImplemented()

    def close(self):
        """
        """
        raise NotImplemented()


class Interface:
    """
    """

    @property
    def page_source(self):
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

    def save_page_source(self, *args, **kwargs):
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

    def save_screenshot(self, format="base64"):
        """
        """
        raise NotImplemented()

    def get_screenshot(self, format="base64"):
        """
        """
        raise NotImplemented()

    def close(self):
        """
        """
        raise NotImplemented()

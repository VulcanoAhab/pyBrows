from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from .headers import chromeForMac
from .browsBase import Interface


# == browsers base
class Vanilla(Interface):
    """
    """
    _headers={}

    def __init__(self, desired_caps={}, service_args=[], headers={}):
        """
        """
        self._startDriver(desired_caps, service_args)
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
    def page_source(self):
        """
        """
        return self._wd.page_source

    def get(self, targetUri):
        """
        """
        self._wd.get(targetUri)

    def _extract(elements, extractor, targetName=None):
        """
        """
        response=[]
        if extractor in ["text", "text_content"]:
            if not targetName:
                targetName="text"
            for e in elements:
                response.append({targetName:e.text})
        elif extractor == "generic_link":
            if not targetName:
                targetName="generic_link"
            for e in elements:
                for p in ["src","data-src","href"]:
                    link=e.get_attribute(p)
                    if not link:continue
                    response.append({targetName:link})
        else:
            for e in elements:
                value=e.get_attribute(extractor)
                if not value:continue
                if not targetName:
                    targetName=extractor
                response.append({targetName:value})
        return response

    def xpath(self, selector, extractor=None, targetName=None):
        """
        """
        elements=self._wd.find_elements_by_xpath(selector)
        if  not extractor: return elements
        return self._extract(elements, extractor, targetName=targetName)

    def elementByName(self, elementName, extractor=None, targetName=None):
        """
        """
        elements=find_elements_by_name(elementName)
        if  not extractor: return elements
        return self._extract(elements, extractor, targetName=targetName)

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

    def __init__(self, desired_caps={}, service_args=[], headers={}):
        """
        """
        super().__init__(desired_caps=desired_caps,
                         service_args=service_args,
                         headers=headers)

import logging
from datetime import datetime
import requests
import pandas as pd
import time
from io import BytesIO 

logger = logging.getLogger(__name__)
    
__username__ = None
__password__ = None
__token__    = None
__auth__     = None

__delayBetweenRequests__ = 0.25
__fileDownloadTimeout__  = 600.0

restApiURL = 'https://restapi.ivolatility.com'

class Auth(requests.auth.AuthBase):
    def __init__(self, apiKey):
        self.apiKey = apiKey
    def __call__(self, r):
        r.headers["apiKey"] = self.apiKey
        return r

def setRestApiURL(url):
    global restApiURL
    restApiURL = url

def getDelayBetweenRequests():
    global __delayBetweenRequests__
    return __delayBetweenRequests__
    
def setDelayBetweenRequests(value):
    global __delayBetweenRequests__
    __delayBetweenRequests__ = value
    
def getFileDownloadTimeout():
    global __fileDownloadTimeout__
    return __fileDownloadTimeout__
    
def setFileDownloadTimeout(value):
    global __fileDownloadTimeout__
    __fileDownloadTimeout__ = value
    
def getToken(username, password):
    return requests.get(restApiURL + '/token/get', params={'username':username, 'password':password}).text

def createApiKey(nameKey, username, password):
    return requests.post(restApiURL + '/keys?nameKey={}'.format(nameKey), json={'username':username, 'password':password}).json()['key']
    
def deleteApiKey(nameKey, username, password):
    return requests.delete(restApiURL + '/keys?nameKey={}'.format(nameKey), json={'username':username, 'password':password}).status_code == 200
    
def setLoginParams(username = None, password = None, token = None, apiKey = None):
    global __username__
    global __password__
    global __token__
    global __auth__
    
    __username__ = username
    __password__ = password
    __token__    = token
    __auth__     = None
    if apiKey is not None:
        __auth__ = Auth(apiKey)

def __raiseFileDownloadTimeout(start, fileDownloadTimeout, endpoint, urlForDetails):
    elapsed = (datetime.now() - start).total_seconds()
    if elapsed >= fileDownloadTimeout:
        raise requests.Timeout(f'Contact with support support@ivolatility.com\nMessage for support:\n\tWrite your args for endpoint;\n\tEndpoint: {endpoint};\n\tUrlForDetails: {urlForDetails};');

def setMethod(endpoint):
    loginParams = {}
    if __auth__ is not None:
        pass
    elif __token__ is not None:
        loginParams = {'token': __token__}
    elif __username__ is not None and __password__ is not None:
        loginParams = {'username':__username__, 'password':__password__}

    URL = restApiURL + endpoint
    
    def getMarketDataFromFile(urlForDetails, delayBetweenRequests, fileDownloadTimeout):        
        start = datetime.now()
        
        isNotComplete = True
        while isNotComplete:
            __raiseFileDownloadTimeout(start, fileDownloadTimeout, endpoint, urlForDetails)
            
            response = requests.get(urlForDetails, auth=__auth__)
            response.raise_for_status()
            
            responseJSON = response.json()
            
            isNotComplete = responseJSON[0]['meta']['status'] != 'COMPLETE'
            
            if isNotComplete:
                time.sleep(delayBetweenRequests)
        
        while True:
            __raiseFileDownloadTimeout(start, fileDownloadTimeout, endpoint, urlForDetails)
            
            try:
                if 'urlForDownload' in responseJSON[0]['data'][0]:
                    urlForDownload = responseJSON[0]['data'][0]['urlForDownload']
                else:
                    return pd.DataFrame()
                break
            except IndexError as e:
                time.sleep(delayBetweenRequests)
                response = requests.get(urlForDetails, auth=__auth__)
                response.raise_for_status()
                
                responseJSON = response.json()
        
        response = requests.get(urlForDownload, auth=__auth__)
        response.raise_for_status()
        
        return pd.read_csv(BytesIO(response.content), compression='gzip')
        
    def requestMarketData(params):
        delayBetweenRequests = __delayBetweenRequests__
        fileDownloadTimeout  = __fileDownloadTimeout__
        
        if 'delayBetweenRequests' in params.keys(): delayBetweenRequests = params.pop('delayBetweenRequests')
        if 'fileDownloadTimeout' in params.keys(): fileDownloadTimeout = params.pop('fileDownloadTimeout')
        
        response = requests.get(URL, auth=__auth__, params=params)
        
        response.raise_for_status()
        
        if response.status_code == 204:
            return pd.DataFrame()
        
        contentType = response.headers['content-type']
        
        if contentType == 'text/csv':
            return pd.read_csv(BytesIO(response.content))
        elif contentType == 'application/x-bzip':
            return pd.read_csv(BytesIO(response.content), compression='zip')
        elif contentType in ['application/json', 'text/plain;charset=UTF-8']:
        
            responseJSON = response.json()
            
            if isinstance(responseJSON, list):
                return pd.DataFrame(responseJSON)
            else:
                urlForDetails = None
                if 'urlForDetails' in responseJSON['status']:
                    urlForDetails = responseJSON['status']['urlForDetails']
                
                if urlForDetails:
                    return getMarketDataFromFile(urlForDetails, delayBetweenRequests, fileDownloadTimeout)
                else:
                    return pd.DataFrame(responseJSON['data'])
        
        raise NotImplementedError(f'For endpoint {endpoint} not implemented.\nContact with support support@ivolatility.com\nMessage for support:\n\tEndpoint: {endpoint};\n\tcontent-type: {contentType};\n\tStatus Code: {response.status_code};\n\tText: {response.text}')
        return pd.DataFrame()

    def factory(**kwargs):
        params = dict(loginParams, **kwargs)
        if 'from_' in params.keys(): params['from'] = params.pop('from_')
        elif '_from' in params.keys(): params['from'] = params.pop('_from')
        elif '_from_' in params.keys(): params['from'] = params.pop('_from_')
        return requestMarketData(params)

    return factory

import re, requests, os
from config import cfg
from utils import Cache

class Spider(object):
    def __init__(self, *, timeout=None, headers=cfg.default_headers, \
            headers_path=None, keys=None, cache_path='html_cache',\
            encoding=None):
        self.sess = requests.Session()
        self.timeout=timeout
        self.headers = self.make_headers(headers_path, keys) \
            if isinstance(headers_path, str) else headers
        self.cache_path = cache_path
        self.cache = Cache(self.cache_path)
        self.encoding = encoding

    def make_headers(self, headers_path, keys):
        assert isinstance(keys, (list, set, None))
        headers = {}
        keys = set(keys) if keys else keys
        with open(headers_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                x = line.find(':')
                if x != -1 and (not keys or line[:x] in keys):
                    headers[line[:x]] = line[x+1:-1]
        return headers

    def get(self, *args, **kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = self.headers
        if 'timeout' not in kwargs and self.timeout:
            kwargs['timeout'] = self.timeout

        try:
            response = self.sess.get(*args, **kwargs)
        except:
            return None

        if self.encoding:
            response.encoding = self.encoding
        return response
            
    def post(self, *args, **kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = self.headers
        if 'timeout' not in kwargs and self.timeout:
            kwargs['timeout'] = self.timeout

        try:
            response = self.sess.post(*args, **kwargs)
        except:
            return None

        if self.encoding:
            response.encoding = self.encoding
        return response

    def html_save(self, response, name):
        self.cache.bin_save(response.content, name)

    def str_save(self, text, name):
        self.cache.str_save(text, name)

    def download(self, name, *args, **kwargs):
        self.html_save(self.get(*args, **kwargs), name)


    def login(self, url, success_judge, \
            certcode_url=None, cache_name='./data', anonymous=False, \
            **kwargs):
        from getpass import getpass
        _input = getpass if anonymous else input
        
        def get_certcode(url):
            print('[LOG] downloading certcode from %s ..' % url)
            name = 'certcode.jpg'
            certcode_path = os.path.join(self.cache_path, name)
            self.download(name, url)
            print('[LOG] try to import cv2..')
            try:
                import cv2
                img = cv2.imread(certcode_path)
                if 'recognition' in kwargs:
                    print('[LOG] use auto recognition instead!')
                    return kwargs['recognition'](img, kwargs['pattern'])
                print('[SUC] successfully import cv2. please watch the image window and input certcode..')
                cv2.imshow(cache_name, img)
                cv2.waitKey(3000)
            except:
                print('[ERR] failed to import cv2. please input certcode from %s' % certcode_path)
            certcode = str(input('[I N] certcode: '))
            return certcode

        print('[LOG] start to login %s ..' % url)
        information = Cache(cache_name)
        data = information.load('login')
        if not data:
            username = _input('[I N] username: ')
            password = getpass('[I N] password: ')
            tel = _input('[I N] tel: ')
            ####    ####    ####    ####
            #   change data format to what target website needs
            data = {
                'nickName': username,
                'password': password,
                'logintype': 'PLATFORM',
            }
            ####    ####    ####    ####
            information.save(tel, 'tel')
            information.save(data, 'login')
        certcode = get_certcode(certcode_url) if certcode_url else None

        ####    ####    ####    ####
        #   change data format to what target website needs
        if certcode:
            data['checkCode'] = certcode
        ####    ####    ####    ####

        print('[LOG] hi, user %s.' % (data['nickName'] \
                if not anonymous else 'anonymous'))

        response = self.post(url, data=data, headers=self.headers)
        self.html_save(response, 'login.html')

        
        return success_judge(response)

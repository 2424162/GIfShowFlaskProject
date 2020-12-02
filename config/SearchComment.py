import copy
import requests
import hashlib
from urllib import parse
from Config import config  # 从Config.py获取配置好的data和headers


class SearchComment:
    def __init__(self, photoId, page=0):  # 默认页数为0

        self.page = page
        configs = config()
        self.headers2 = copy.deepcopy(configs.HEADERS)
        self.headers = copy.deepcopy(configs.HEADERS)  # 请求headers
        self.sig_data = configs.SIG_DATA
        self.sig_data.update({'photoId': photoId,

                              'photoPageType': '3'}
                             )
        self.salt = config().SALT

    def sig_and_headers(self, sig):  # sig算法 ：将需要验证的data和header参数名首字排序，然后转二进制
        sig_str = ""
        url_headers = {}
        head = list(self.headers)
        sig_key = self.headers
        sig_key.update(sig)
        for i in sorted(list(sig_key)):
            sig_str = sig_str + i + "=" + sig_key[i]
        head.sort()
        for i in head:
            url_headers[i] = self.headers[i]
        self.url_tail = parse.urlencode(self.headers2)
        return sig_str

    def search_workpage_request(self, sig):  # 最后的requests请求
        data = copy.deepcopy(sig)  # 读Config.py的数据
        sig_str = self.sig_and_headers(data)
        salt = '382700b563f4'
        str = sig_str + salt
        m = hashlib.md5(str.encode())
        sig = m.hexdigest()
        data.update({"sig": sig,
                     '__NS_sig3':'2181602469c67337a002570c537'+sig[1:3],
                     '__NStokensig':  '70b479038007ab3deb0e44654560243d3256d1cc340b7dbc9a'+sig[1:3],
                     })
        workpage_url_hair = "https://apissl.ksapisrv.com/rest/n/comment/list/v2?"
        result = requests.post(url=workpage_url_hair + self.url_tail, data=data)
        result = result.json()
        self.pcursor = result['pcursor']
        print("+++++" + self.pcursor)
        return result

    def search_workpage(self, sig):  # 判断搜索页数是否请求参数加ussid
        for page in range(0, self.page + 1):
            print(page)
            if (page == 0):
                yield self.search_workpage_request(sig)
            else:
                users_follow_data = {'pcursor': self.pcursor,
                                     'user_id': '8172604',
                                     'order': 'desc',
                                     'count': '10',
                                     }
                sig_tmp = copy.deepcopy(sig)
                # print(sig_tmp)
                sig_tmp.update(users_follow_data)
                yield self.search_workpage_request(sig_tmp)

if __name__ == "__main__":
    SW = SearchComment("5246130656361544585", 2)
    tiems = SW.search_workpage(SW.sig_data)
    strs = ''
    for i in tiems:
        print(str(i))

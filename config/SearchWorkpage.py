import copy
import requests
import hashlib
from urllib import parse
from Config import config  #从Config.py获取配置好的data和headers

class SearchWorkpage:
    def __init__(self,keyword,pcursor=0): #默认页数为0

        self.pcursor = pcursor
        configs = config()
        self.headers2 = copy.deepcopy(configs.HEADERS)

        self.headers = copy.deepcopy(configs.HEADERS)     #请求headers
        self.sig_data = configs.SIG_DATA
        self.sig_data.update({'keyword': keyword})
        self.salt = config().SALT


    def sig_and_headers(self,sig):   #sig算法 ：将需要验证的data和header参数名首字排序，然后转二进制
        sig_str = ""
        url_headers = {}
        print(self.headers)

        head = list(self.headers)
        sig_key = self.headers
        sig_key.update(sig)
        print(self.headers)
        for i in sorted(list(sig_key)):
            sig_str = sig_str + i + "=" + sig_key[i]
        head.sort()
        for i in head:
            url_headers[i] = self.headers[i]

        self.url_tail = parse.urlencode(self.headers2)
        return sig_str
    def users_data_process(self,result):  #返回的数据做解析
        result_list = []
        #print("解析函数")
        for data in result['feeds']:
            #print(data)
            try:
                puretitle = data['caption']
            except:
                puretitle = "空"
            try:
                user_name = data['user_name']
            except:
                user_name = "kong"
            serverexptag = data['serverExpTag']
            try:
                work_url = data['main_mv_urls'][0]['url']
            except:
                work_url = "wu"
            re_dict = {"user_name":user_name,"puretitle":puretitle,"serverexptag":serverexptag,"work_url":work_url}
            result_list.append(re_dict)
            # #print(puretitle)
            # #print(user_name)
            # #print(serverexptag)
            # #print(work_url)
        return str(result_list)


    def get_ussid(self,sig):   #获取ussid，第一页的参数没有ussid,第二页的ussid在第一页的返回值里面
        data = copy.deepcopy(sig)
        sig_str = self.sig_and_headers(data)
        salt = '382700b563f4'
        str = sig_str + salt
        m = hashlib.md5(str.encode())  #转成二进制后+salt 做md5加密就得到sig
        sig = m.hexdigest()
        ##print(sig)
        data.update({"sig":sig})
        workpage_url_hair = "http://apissl.gifshow.com/rest/n/search/feed?"
        result = requests.post(url=workpage_url_hair + self.url_tail, data=data)
        result = result.json()
        ##print(result)
        self.ussid = result['ussid']


    def search_workpage_request(self,sig):  #最后的requests请求
        data = copy.deepcopy(sig) #读Config.py的数据
        sig_str = self.sig_and_headers(data)
        salt = '382700b563f4'
        str = sig_str + salt
        m = hashlib.md5(str.encode())
        sig = m.hexdigest()
        #print(sig)
        data.update({"sig":sig,
                     '__NS_sig3': '2181602469c67337a002570c537'+sig[1:3],
                     '__NStokensig': '70b479038007ab3deb0e44654560243d3256d1cc340b7dbc9a'+sig[1:3],
                     })
        #print(data)
        workpage_url_hair = "http://apissl.gifshow.com/rest/n/search/feed?"
        result = requests.post(url=workpage_url_hair + self.url_tail, data=data)
        print(workpage_url_hair)
        print(self.url_tail)
        result = result.json()
        #print(result)
        serverexptag = self.users_data_process(result)


        return  serverexptag
    def search_workpage(self,sig):      #判断搜索页数是否请求参数加ussid
        print(sig)
        for page in range(0, self.pcursor + 1):
            #print(page)
            if (page == 0):
                self.get_ussid(sig)
                yield self.search_workpage_request(sig)
            else:
                print(self.ussid)
                users_follow_data = {'pcursor': str(page),
                                     'ussid': self.ussid,
                                     }
                print(page)
                print(self.ussid)
                sig_tmp = copy.deepcopy(sig)
                #print(sig_tmp)
                sig_tmp.update(users_follow_data)
                yield self.search_workpage_request(sig_tmp)


if __name__ == "__main__":
        SW = SearchWorkpage("手机",3)
        tiems = SW.search_workpage(SW.sig_data)
        strs = ''
        for i in tiems:
            print(i)




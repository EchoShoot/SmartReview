import requests
from urllib.parse import quote,urljoin
from hashlib import md5
import json
import random
import logging
#logging.basicConfig(level=logging.INFO)

appKey = '7d06bf4e164161c3'
secretKey = 'kde6N0fg3LaRNFZxQvAvloDGHyKJqqeH'

fromLang = 'EN'
toLang = 'zh-CHS'
salt = random.randint(1, 65536)

errorCodeTable = {
	'101':"缺少必填的参数，出现这个情况还可能是et的值和实际加密方式不对应",
	'102':"不支持的语言类型",
	'103':"翻译文本过长",
	'104':"不支持的API类型",
	'105':"不支持的签名类型",
	'106':"不支持的响应类型",
	'107':"不支持的传输加密类型",
	'108':"appKey无效，注册账号， 登录后台创建应用和实例并完成绑定， 可获得应用ID和密钥等信息，其中应用ID就是appKey（ 注意不是应用密钥）",
	'109':"batchLog格式不正确",
	'110':"无相关服务的有效实例",
	'111':"开发者账号无效，可能是账号为欠费状态",
	'201':"解密失败，可能为DES,BASE64,URLDecode的错误",
	'202':"签名检验失败",
	'203':"访问IP地址不在可访问IP列表",
	'301':"辞典查询失败",
	'302':"翻译查询失败",
	'303':"服务端的其它异常",
	'401':"账户已经欠费停",
	}

def enquery(text):
	try:
		sign = appKey+text+str(salt)+secretKey
		sign = md5(sign.encode('utf-8')).hexdigest()  # 经历 MD5 加密
		payload = {'appKey':appKey,'q':quote(text),'from':fromLang,'to':toLang,'salt':str(salt),'sign':sign}
		response = requests.get('http://openapi.youdao.com/api',params=payload)
		explain = json.loads(response.text)
	except Exception as e:
		print(e)
	else:
		errorCode = explain['errorCode']
		if errorCode in errorCodeTable.keys():
			raise ValueError('errorCode:{} {}'.format(errorCode, errorCodeTable[errorCode]))
		if explain.get('basic'):  # 获取基础释义
			return explain['basic']['explains']
		else:  # 否则返回翻译结果
			return explain['translation']

if __name__ == "__main__":
	print(enquery('happy'))
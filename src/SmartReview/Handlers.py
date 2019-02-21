from SmartReview import Error
import os
import json
import logging
logger = logging.getLogger(__name__)
from collections import UserDict
from contextlib import contextmanager
from tqdm import tqdm
from SmartReview.Base import Vocabulary
from SmartReview.Base import basepath,savepath

		
class FileHandlers(UserDict):
	""" 形成 {'hello':'你好','yes':'对'...} 的形式 """
	savepath = savepath
	filetype = NotImplemented
		
	@classmethod
	def process_FileToDict(cls, filepath):
		raise NotImplementedError
		
		
class JsonFileHandlers(FileHandlers):
	""" 目的是类似以下格式的 json 中提取内容 
		[
			{"word":"hello", "explain":"你好"},
			{"word":"yes", "explain":"对"},
		]
		形成 {'hello':'你好','yes':'对'...} 的形式
	"""
	filetype = '.json'
	
	@classmethod
	def process_FileToDict(cls, filepath):
		assert filepath.endswith(cls.filetype),'{} 不是 {} 格式的文件'.format(filepath,cls.filetype)
		
		assert not os.path.samefile(filepath, cls.savepath),"filepath:{} 不能与 savepath:{} 一致".format(filepath,cls.savepath)
		with open(filepath,'r') as f:
			words = json.load(f)
			datas = {each['word']:each['explain'] for each in words}
		return cls(datas)
	
	
class TxtFileHandlers(FileHandlers):
	""" 目的是类似以下格式的 txt 中提取内容 
		hello, "你好"
		yes, "对"
		形成 {'hello':'你好','yes':'对'...} 的形式
		"""
	filetype = '.txt'
	
	@classmethod
	def process_FileToDict(cls, filepath):				
		assert filepath.endswith(cls.filetype),'{} 不是 {} 格式的文件'.format(filepath,cls.filetype)
		assert not os.path.samefile(filepath, cls.savepath),"filepath:{} 不能与 savepath:{} 一致".format(filepath,cls.savepath)
		datas = {}
		with open(filepath,'r') as f:
			for line in f:
				pair = re.findall(r'^([\w-]+)[, ]*(.*)$', line)  # 提取信息
				for word, explain in pair:
					if not explain:  # 如果没有预先释义,就调用第三方模块来查询释义
						explain = json.dumps(youdao.enquery(word), ensure_ascii=False)
					else:
						explain = json.dumps((explain,), ensure_ascii=False)
					datas[word] = explain  # 装入
		return cls(datas)
		

FILE_HANDLERS_BASE = {
	'json': JsonFileHandlers,
	'txt': TxtFileHandlers,
}		


class FileProcess(UserDict):
	
	@staticmethod
	def get_filetype(filepath):
		""" 获取文件类型 """
		return filepath.split('.')[-1]

	@staticmethod
	def get_handler(filetype):
		""" 利用文件类型获取 handler """
		handler = FILE_HANDLERS_BASE.get(filetype, None)  # 找到对应处理类
		if handler is None:  # 如果没有找到处理类
			logger.error('no handler available in FILE_HANDLERS_BASE')
		return handler
		
	def process(self, filepath, covered=False):
		""" 将文件内容,导入到数据库中 """
		filetype = self.get_filetype(filepath)  # 获取文件类型
		handler = self.get_handler(filetype)  # 获取处理 handler
		words = handler.process_FileToDict(filepath)  # 利用 handler 处理,得到单词表
		assert isinstance(words, UserDict),"handler.process_FileToDict 应该返回一个 UserDict 子类"
		# 配置进度条
		pbar = tqdm(words.items(), unit='个', unit_scale=True, position=0)
		pbar.set_description('Process -> {:^15}'.format(filepath))  
		# 开始迭代处理
		for word,explain in pbar:
			if self.data.get(word,None) is None:  # 如果数据库索引中不存在该单词,就创建!
				if not explain:  # 如果是单词没有释义就报错
					raise Error.NotFoundExplain('{} - {} 没有找到释义'.format(filepath,word))
				v = Vocabulary(word, explain)  # 形成 Vocabulary 对象
				self.data[word] = v
			elif covered is True:  # 如果单词已经存在,并且确定要覆盖释义
				old_word = self.data[word]  # 提取就的单词对象
				old_word.explain = explain  # 替换释义
				self.data[word] = old_word  # 更新数据库
		else:
			pbar.set_postfix(word=word)  # 显示进度条状态
		logger.info('Vocabulary Loading Completed!')
		return self.data


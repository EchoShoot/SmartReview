class RecordsIsNotExist(Exception):
    """ 不存在 records 记录 """


class UpdateRecordsFailed(Exception):
    """ 更新 records 失败 """


class NotFoundExplain(Exception):
    """ 单词没有释义 """
    
    
class NotFoundSuchFile(Exception):
    """ 没有找到指定文件 """
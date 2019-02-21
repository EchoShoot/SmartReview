# -*- coding: utf-8 -*-
# @Time    : 2018/1/13 上午12:23
# @Author  : ZhangYaoWu
# @Email   : 852822425@qq.com
# @File    : Tactics.py
# @Software: PyCharm
import json
import logging
import shutil
import os
import re
from collections import namedtuple, UserDict, UserList, Counter, defaultdict
from itertools import chain
from SmartReview import Error
from datetime import datetime, timedelta
from tqdm import tqdm
import time
from SmartReview.Tools import youdao
from collections import deque
from pprint import pformat
import math

logger = logging.getLogger(__name__)
from pkg_resources import resource_filename, Requirement
basepath = resource_filename(Requirement.parse('SmartReview'),'SmartReview/save')
savepath = os.path.join(basepath,'database.json')
        
Record = namedtuple('Record', 'speed timestamp stats')  # 存储结构向量

class Associate(set):
    """ 这个类主要是为 Vocabulary 提供,关联词添加功能 """

    def add(self, word: str):
        """ 添加关联词 """
        if isinstance(word, Vocabulary):
            word = word.value  # 获取单词
        super(Associate, self).add(word)

    def remove(self, word: str):
        """ 移除关联词 """
        if isinstance(word, Vocabulary):
            word = word.value  # 获取单词
        super(Associate, self).remove(word)

    @classmethod
    def load(cls, your_list=None):
        """ 反序列化 """
        if your_list is None:
            your_list = set()
        return cls(your_list)

    def dump(self):
        """ 序列化 """
        return list(self)


class DayLog(UserList):
    """ 提供一个二级,存放每次记录的结构 """

    def __init__(self, *args, **kwargs):
        super(DayLog, self).__init__(*args, **kwargs)
        self.records_lst = list()  # 本次背词状态

    def add_record(self, record):
        """ 更新一条记录 """
        assert isinstance(record, Record), '只接受 Record 类参数'
        self.records_lst.append(record)  # 加入

    def alter_record(self, record):
        """ 修改该最后一次记录 """
        assert isinstance(record, Record), '只接受 Record 类参数'
        item = self.records_lst.pop()  # 删去最后一个
        self.add_record(record)
        return item, record

    def update_records(self):
        """ 保存操作结果,dumps() 函数调用的时候也会调用这个函数 """
        if self.records_lst:  # 如果存在 records
            self.append(self.records_lst.copy())  # 将本次背词状态加入多级日志表
            self.records_lst.clear()  # 清除原状态
        else:
            raise Error.UpdateRecordsFailed('本次没有 records 记录,你可以用 try...except: pass 来无视这个错误.')

    def get_records(self, index=-1) -> list:
        """ 获取指定 index 天的记录 """
        try:
            return self.data[index]
        except IndexError:
            raise Error.RecordsIsNotExist('只含有 {} 次记录,你的索引值超出了这个范围'.format(len(self.data)))

    @property
    def last_records(self) -> list:
        """ 获取上一次的背词状态的完整记录 """
        try:
            return self.get_records(-1)
        except Error.RecordsIsNotExist:
            raise Error.RecordsIsNotExist('DayLog.data 是空的,不存在上一次的记录')

    def append(self, your_list):
        for elem in your_list:
            assert isinstance(elem, Record), "append() received an error rank {elemtype} " \
                                             ",it only received {needtype} rank".format(elemtype=type(elem),
                                                                                        needtype=Record)
        super(DayLog, self).append(your_list)

    @classmethod
    def load(cls, your_mulit_list):
        """ 反序列化 """
        datas = []
        if your_mulit_list:  # your_list 存在
            assert isinstance(your_mulit_list,
                              list), "load() Only received list rank! current rank is {}".format(
                type(your_mulit_list))
            for records in your_mulit_list:
                datas.append([Record(*record) for record in records])
        return cls(datas)

    def dump(self):
        return self.data


class ReviewManage(object):
    review_table = [12, 1 * 24, 2 * 24, 4 * 24, 7 * 24, 15 * 24]  # 单位是小时
    time_table = ['已逾期', '今早', '今晚', '明早', '明晚', '后天', '第4天', '第7天', '第15天', '半个月后']  # 依据 review_table 计算出来的

    def __init__(self, daylog, review_index):
        self.daylog = daylog
        self.AM_h, self.AM_m = map(int, '6:30'.split(':'))  # 早上你开始背单词的最早时间
        self.PM_h, self.PM_m = map(int, '20:30'.split(':'))  # 晚上你开始背单词的最早时间
        self.__review_index = review_index or 0  # review_index 的值可能是负数,也能是一个很大的数!

    def slide_left(self):
        """ 向左滑动 """
        # 为了防止一个掌握的单词,因为曾经掌握 +100,结果十年没有复习了,现在已经不会了,借此快速降级
        if self.is_slide_over:
            self.__review_index = len(self.review_table)  # 快速归位
        self.__review_index -= 1

    def slide_right(self):
        """ 向右滑动 """
        # 为了防止一个顽固单词,曾经顽固 -100,结果现在已经会了,不过还没有偿还回来,借此快速升级
        if self.is_slide_below:
            self.__review_index = 0  # 快速归位
        self.__review_index += 1

    @property
    def is_slide_over(self):
        """ 该单词掌握 """
        return True if self.__review_index > len(self.review_table) else False

    @property
    def is_slide_below(self):
        """ 顽固词汇 """
        return True if self.__review_index < 0 else False

    @property
    def next_review_interval(self):
        """ 距离下一次的复习间隔 """
        index = self.__review_index
        if index < 0:  # 如果index 过小,将索引定为0的返回
            index = 0
        elif index >= len(self.review_table):  # 如果 index 超出列表最大索引值,每超过一个多3天!
            return self.review_table[-1] * 3600 + (index-len(self.review_table)) * 72 * 3600
        return self.review_table[index] * 3600  # 滑动复习间隙 (小时转换成秒)

    @property
    def next_review_timestamp(self) -> float:
        """ 获取下一次的复习的时间戳 """
        try:
            last_timestamp = self.daylog.last_records[-1].timestamp  # 上次背单词的时间戳
            review_time = last_timestamp + self.next_review_interval  # 得到下一次复习的时间
        except Error.RecordsIsNotExist:
            review_time = time.time() - 59  # 当前时间减去 59 秒,来确保应当复习

        return review_time

    def fix_time(self, predict_time):
        """ 人性化修正,背单词的开始时间 """
        before_pm = (predict_time - timedelta(days=1)).replace(hour=self.PM_h, minute=self.PM_m)  # 前一天晚上
        cur_am = predict_time.replace(hour=self.AM_h, minute=self.AM_h)  # 当天上午
        cur_pm = predict_time.replace(hour=self.PM_h, minute=self.PM_m)  # 当天下午

        if before_pm <= predict_time < cur_am:
            return before_pm  # 当你预测时间是 昨天下午 ~ 今天早上, 算作"昨天晚上"要背的任务量
        elif cur_am <= predict_time < cur_pm:
            return cur_am  # 当你预测时间是 今天上午 ~ 今天下午, 算作"今天早上"要背的任务量
        else:
            return cur_pm  # 当你预测时间是 今天下午 ~ 明天上午, 算作"今天晚上"要背的任务量

    @property
    def next_review_time(self):
        """ 离该单词下一次复习的剩余的时间 """
        current_time = datetime.now()
        predict_time = datetime.fromtimestamp(self.next_review_timestamp)  # 预期复习的时间
        predict_time = self.fix_time(predict_time)  # 修正复习时间

        if predict_time <= current_time:
            index = 0  # 逾期
        elif predict_time.date() == current_time.date():
            if 'AM' in predict_time.strftime('%p'):
                index = 1  # 今早
            else:
                index = 2  # 今晚
        elif predict_time.date() == current_time.date() + timedelta(days=1):
            if 'AM' in predict_time.strftime('%p'):
                index = 3  # 明早
            else:
                index = 4  # 明晚
        elif predict_time.date() == current_time.date() + timedelta(days=2):
            index = 5  # 后天
        elif current_time.date() + timedelta(days=2) < predict_time.date() <= current_time.date() + timedelta(days=4):
            index = 6  # 4天
        elif current_time.date() + timedelta(days=4) < predict_time.date() <= current_time.date() + timedelta(days=7):
            index = 7  # 7天
        elif current_time.date() + timedelta(days=7) < predict_time.date() <= current_time.date() + timedelta(days=15):
            index = 8  # 15天
        else:
            index = 9
        return self.time_table[index]  # 获取中文解释

    @classmethod
    def default_times_chooses(cls):
        """ 提供默认选项 """
        if 'AM' in datetime.now().strftime('%p'):
            times = cls.time_table[:2]  # 已经逾期的与上午的
        else:
            times = cls.time_table[:3]  # 已经逾期与今天上午和今天下午的
        return times

    def is_need_review(self, times=None):
        """ 通过时间参数判断是否需要复习 """
        if times is None:
            times = self.default_times_chooses()
        else:
            assert isinstance(times, list), "参数 times 必须是 list 类型, 请参考 self.time_table"
            assert set(times).issubset(set(self.time_table)), "你传入的为 {} 不是 {} 的子集!".format(times, self.time_table)
        return self.next_review_time in times

    @classmethod
    def load(cls, daylog, review_index):
        """ 反序列化 """
        return cls(daylog, review_index)

    def dump(self):
        """ 序列化 """
        return self.__review_index


class Auxiliary(object):
    """ 用来辅助记忆的工具函数 """

    # 用来语音播报
    @staticmethod
    def say(text, speaker=None, speed=4):
        from subprocess import Popen
        assert isinstance(text, str), "只能语音播报 str 类型"
        assert 1 <= speed <= 10, "speed 范围在 1~10"
        if speaker:
            return Popen(['say', text, '-v{}'.format(speaker), '-r{}'.format(30 + speed * 60)])
        return Popen(['say', text, '-r{}'.format(30 + speed * 60)])

    # 词根分析
    def etyma_memory(self):
        raise NotImplementedError('尚未实现')

    # 混淆词分析
    def associate_memory(self):
        raise NotImplementedError('尚未实现')

    # 例句分析
    @property
    def illustrate(self):
        raise NotImplementedError('尚未实现')

    # 相似词分析
    @property
    def similarity(self):
        raise NotImplementedError('尚未实现')


class Vocabulary(object):
    """ 词汇 """
    rank_table = ['精通', '掌握', '记住', '清晰', '模糊', '混淆', '忘记', '顽固', '待定']  # 精通,掌握,记住,清晰后移,待定与模糊不动,混淆,忘记,顽固前移

    def __init__(self, word, explain, review_index=None, datas=None, associate=None):
        # super(Vocabulary, self).__init__()
        self.value = word  # 词汇
        self.explain = explain  # 释义
        self.daylog = DayLog.load(datas)  # 多级日志表
        self.associate = Associate.load(associate)  # 关联词
        self.review = ReviewManage.load(self.daylog, review_index)  # 复习管理

    def __repr__(self):
        return "{clsname}(word='{word}',explain='{explain}',rank={rank}) & next_review_time: {review_time}".format(
            clsname=self.__class__.__name__,
            word=self.value, explain=self.explain,
            rank=self.rank, review_time=self.review.next_review_time)

    @property
    def priority(self):
        """ 单词的优先级 """
        return self.rank_table.index(self.rank)

    @property
    def rank(self):
        """ 单词的类别: 对单词的掌握度 """
        index = -1  # 待定
        try:
            records = self.daylog.last_records
            if len(records) == 1 and records[0].stats is True:  # 只有一个记录,状态为 True
                if self.review.is_slide_over:  # 根据旧的状态,判断是否掌握了的单词
                    if records[0].speed < 2.3:
                        index = 0  # 精通
                    else:
                        index = 1  # 掌握
                else:
                    index = 2  # 记住
            elif len([record for record in records if record.stats is False]) == 1:  # 只有含有一个 False 状态
                index = 3  # 清晰
            elif len([record for record in records if record.stats is False]) <= 3:  # 只有含有小于3个 False 状态
                index = 4  # 模糊
            else:  # 忘记
                if self.review.is_slide_below:  # 根据旧的状态,判断是否为顽固词汇
                    index = 7  # 顽固
                elif len(self.associate) != 0:
                    index = 5  # 混淆
                else:
                    index = 6  # 忘记
        except Error.RecordsIsNotExist:
            logger.debug('last record is not exist')
        return self.rank_table[index]  # 获取中文解释

    @classmethod
    def default_ranks_chooses(cls):
        """ 默认级别选项 """
        ranks = cls.rank_table[:-1]  # 除了待定的都可以
        return ranks

    @classmethod
    def default_times_chooses(cls):
        """ 默认时间选项 """
        times = ReviewManage.default_times_chooses()
        return times

    def is_need_review(self, rank=None, times=None) -> bool:
        """ 用来判断是否需要复习,默认是已经逾期的才需要复习,和掌握程度无关 """
        if rank is None:
            rank = self.default_ranks_chooses()  # 采用默认选项
        else:
            assert isinstance(rank, list), "参数 rank 必须是 list 类型, 请参考 self.rank_table"
            assert set(rank).issubset(set(self.rank_table)), "你传入的为 {} 不是 {} 的子集!".format(self.rank_table, rank)
        # 通过检查当前的 rank 值是不是属于 指定的 rank 范围,当期的 next_review_time 是否属于 times 范围
        return self.rank in rank and self.review.is_need_review(times)

    @classmethod
    def loads(cls, dic):
        """ 反序列化 """
        word = dic.get('word')
        explain = dic.get('explain')
        data = dic.get('data')
        review_index = dic.get('review_index')
        associate = dic.get('associate')
        # 将 row_data 中的值都转换成 record 类型,因为是二级列表所以才会下面这么麻烦
        self = cls(word, explain, review_index, data, associate)
        return self

    def update_status(self):
        """ 保存单词的记录,更新单词的评级 """
        try:
            self.daylog.update_records()  # 在序列化前,将结果存入日志表
        except Error.UpdateRecordsFailed:  # 如果不存在日志表就不动
            pass
        else:
            # 精通,掌握,记住,清晰后移,待定与模糊不动,混淆,忘记,顽固前移
            word_type = self.rank  # 调整 review_index 的位置
            if word_type in ['精通', '掌握', '记住', '清晰']:
                self.review.slide_right()
            elif word_type in ['混淆', '忘记', '顽固']:
                self.review.slide_left()
            else:
                pass

    def dumps(self):
        """ 序列化 """
        return {'word': self.value, 'explain': self.explain, 'review_index': self.review.dump(),
                'data': self.daylog.dump(),
                'associate': self.associate.dump()}


class Dictionary(UserDict):
    """ 充当词汇书 """

    def __init__(self, *args, **kwargs):
        super(Dictionary, self).__init__(*args, **kwargs)
        self.masterySet = set()  # 记住
        self.vagueSet = set()  # 有印象
        self.forgetList = deque()  # 忘记
        self.reviewList = deque()  # 待背单词
        os.makedirs(basepath, exist_ok=True)  # 创建文件夹

    @classmethod
    def loadFrom(cls, filepath='', covered=False):
        """ 从数据库提取单词 """
        # 如果存在文件数据库就自动加载
        assert filepath=='' or os.path.isfile(filepath),'filepath:"{}" Not Found! currentpath:"{}"'.format(filepath,os.getcwd())
                
        datas = {}
        logger.info('your current path:{}'.format(os.getcwd()))
        if os.path.isfile(savepath):
            with open(savepath, 'r') as f:
                logger.info('path: {} is opened now!'.format(savepath))
                datas = {value: Vocabulary.loads(word) for value, word in json.load(f).items()}
            logger.info(' {} words is loaded'.format(len(datas)))
        self = cls(datas)
        
        if os.path.isfile(filepath):
            from SmartReview.Handlers import FileProcess
            words = FileProcess(self.data)  # 利用文件处理器来依据当前的字典处理文件
            words.process(filepath, covered)
            self.data.update(words)  # 更新数据库

        return self

    def update_words_records(self):
        """ 更新所有单词的记录 """
        for word in chain(self.masterySet, self.vagueSet, self.forgetList, self.reviewList):
            word.update_status()  # 更新日志状态
            self.data[word.value] = word  # 将四个状态集的单词更新到 self.data
        else:  # 清空状态集里面的单词
            self.masterySet.clear()
            self.vagueSet.clear()
            self.forgetList.clear()
            self.reviewList.clear()
            logger.info('all words records has updated!')

    def save(self):
        """ 保存到文件 """
        self.update_words_records()  # 更新所有单词的状态
        savebakpath = os.path.join(basepath,'database_{}.json'.format(datetime.now().date()))
        if os.path.exists(savepath):
            shutil.copyfile(savepath,
                        savebakpath)  # 进行备份,保证意外发生的时候还留一手
        with open(savepath, 'w') as f:
            json.dump(self.data, f, default=Vocabulary.dumps, ensure_ascii=False, indent=4)
        # json.dump(self.data, f, default=Vocabulary.dumps,ensure_ascii=False)

    def save_and_get_report(self):
        """ 保存结果,并获取报告,用于显示各状态的变动情况 """
        old_total = sum(self.info_ranks.values())
        old = (Counter({key: value / old_total for key, value in self.info_ranks.items()}))
        print('old is:', self.info_ranks)
        self.update_words_records()  # 保存更新
        new_total = sum(self.info_ranks.values())
        new = (Counter({key: value / new_total for key, value in self.info_ranks.items()}))
        print('new is:', self.info_ranks)

        result = []
        for key, value in (new - old).items():
            result.append('{} +{}%'.format(key, round(value * 100, 3)))
        for key, value in (old - new).items():
            result.append('{} -{}%'.format(key, round(value * 100, 3)))
        logger.info('report show that:{}'.format(result))
        return '\n'.join(result)

    def info(self):
        """ 目前词库里面单词的状态 """
        ranks = self.info_ranks
        times = self.info_times
        return 'ranks = {}\ntimes = {}\n'.format(dict(ranks), dict(times))

    @property
    def info_ranks(self):
        """ 获取ranks统计 """
        ranks = Counter([word.rank for word in self.values()])  # 单词掌握度统计
        return ranks

    @property
    def info_times(self):
        """ 获取时间统计 """
        times = Counter([word.review.next_review_time for word in self.values()])  # 剩余时间统计
        return times


    def size_of_needreview(self, ranks=None, times=None):
        """ 计算要复习的数量 """
        num = 0
        for word in self.data.values():
            if word.is_need_review(ranks, times) and word not in self.reviewList:
                num += 1
        return num
    
    def select_by_proportion(self, ranks=None, times=None, count=100):
        """ 按照比例抽取单词数量 """
        temp = defaultdict(list)
        for word in sorted(self.data.values(), key=lambda x: x.priority):
            if word.is_need_review(ranks, times):
                if word not in self.reviewList:  # 不在列表里面才计数
                    temp[word.rank].append(word)
        total = sum(map(len, temp.values()))
        for value in temp.values():
            self.reviewList.extend(value[:math.ceil(len(value) / total * count)])
        logger.info('extract {}'.format(
            list(zip(temp.keys(), map(lambda x: math.ceil(len(x) / total * count), temp.values())))))
        logger.info('{} words has add in reviewList'.format(len(self.reviewList)))
        return self.reviewList

    def select(self, ranks=None, times=None, count=100):
        """ 从词库中选单词来背,默认检查 已逾期 的所有 单词类别, count 控制背词数量 """
        index = 0
        for word in sorted(self.data.values(), key=lambda x: x.priority):
            if word.is_need_review(ranks, times):
                if word not in self.reviewList:
                    self.reviewList.append(word)  # 不在列表里面才添加
                    index += 1  # 进行计数累计
                    if index >= count:  # 当数量达到就弹出去
                        break
        logger.info('extract {}'.format(list(Counter([word.rank for word in self.reviewList]).items())))
        logger.info('{} words has add in reviewList'.format(len(self.reviewList)))
        return self.reviewList


def load():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('wordpath', help="单词路径, 仅支持.txt\.json格式")
    args = parser.parse_args()
    wordpath = os.path.join(os.getcwd(), args.wordpath)  # 计算文件位置
    echo = Dictionary.loadFrom(wordpath,covered=True)
            
    print(echo.info())
    echo.save()

if __name__ == '__main__':
    load()
    

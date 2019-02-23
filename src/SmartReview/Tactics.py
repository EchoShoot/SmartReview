# -*- coding: utf-8 -*-
# @Time    : 2018/1/16 上午02:27
# @Author  : BiarFordlander
# @Email   : BiarFordlander@gmail.com
# @File    : Tactics.py
# @Software: PyCharm
import logging
import os
import random

from collections import deque, Counter
from SmartReview.Base import Dictionary
import random

#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class LearnTactics(Dictionary):
    """ 学习策略:瀑布流策略 """

    def __init__(self, *args, **kwargs):
        super(LearnTactics, self).__init__(*args, **kwargs)
        # self.masterySet = set()  # 记住
        # self.vagueSet = set()  # 有印象
        # self.forgetList = deque()  # 忘记
        # self.reviewList = deque()  # 待背单词
        self.CheckMode = True  # 检查模式
        os.makedirs('save', exist_ok=True)  # 创建文件夹

    def __show(self):
        """
         显示当前的各个栈的状态,没有什么其他的作用
        :return:
        """
        logger.info('\nself.reviewList:{}\nmasterySet:{}学会\nvagueSet:{}有印象\nforgetSet:{}忘记\n\n'.format(
            repr(self.reviewList), repr(self.masterySet), repr(self.vagueSet), repr(self.forgetList)))

    def __inspect(self, word):
        """
         检查一个单词是否记着
        :param word:
        :return: True/False
        """
        stats = bool(random.randint(0, 1))
        return stats

    def fetch(self):
        """
         获取一个待检查的单词
        :return: word/None
        """
        word = None
        if self.CheckMode:  # 如果是检查模式
            try:
                word = self.reviewList.popleft()
            except IndexError:
                logger.debug('self.reviewList Empty!')
                self.CheckMode = False
                logger.debug('switch to self.CheckMode=False')
                logger.info('切换至: 学习模式')
        else:  # 如果是学习模式
            try:
                word = self.forgetList.popleft()
            except IndexError:
                if len(self.vagueSet):  # 如果否存在有印象的单词
                    logger.debug('self.forgetSet Empty!')
                    for each in self.vagueSet:  # 全部倒回给 self.review_list
                        self.reviewList.append(each)
                    else:
                        self.vagueSet.clear()
                        self.CheckMode = True
                        logger.debug('send self.vagueSet to self.reviewList and switch to self.CheckMode=True')
                        logger.info('切换至: 检查模式')
                else:
                    raise KeyError('所有单词检查完毕')
        logger.debug('pop:{}'.format(word))
        return word or self.fetch()

    def add_remember(self, word):
        """
         设置单词为记住状态
        :param word:
        :return:
        """
        if word is None:  # 如果单词 word 为 None,没有必要继续了
            logger.debug('word is None')
            return
        if self.CheckMode:
            self.masterySet.add(word)
            logger.debug('{} add to self.masterySet'.format(word))
        else:
            self.vagueSet.add(word)
            logger.debug('{} add to self.vagueSet'.format(word))

    def add_forget(self, word):
        """
         设置单词为忘记状态
        :param word:
        :return:
        """
        if word is None:  # 如果单词 word 为 None,没有必要继续了
            logger.debug('word is None')
            return
        self.forgetList.append(word)  # 添加到忘记
        if random.randint(0, 1):  # 不方便频繁打乱
            random.shuffle(self.forgetList)  # 打乱顺序
        logger.debug('{} add to self.forgetList'.format(word))

    @property
    def process(self):
        """ 用于返回剩余个数 """
        total = len(self.reviewList) + len(self.vagueSet) + len(self.forgetList) + len(self.masterySet)
        return 1 if total == 0 else len(self.masterySet) / total

    def _launch(self):
        """
         用来展示运作的流程,没有其他存在的实际意义
        :return:
        """
        while True:
            self.__show()  # 显示
            try:
                word = self.fetch()  # 获取一个待检查的单词
                if word is None:
                    continue
            except KeyError:
                break
            else:
                stats = self.__inspect(word)
                logger.debug('stats is {}'.format(stats))
                if stats:  # 检查是否记得
                    self.add_remember(word)
                else:
                    self.add_forget(word)
        print('检查完成!')


if __name__ == '__main__':
    engine = LearnTactics({'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E', 'F': 'F'})
    engine.reviewList.extend(engine.values())
    engine._launch()

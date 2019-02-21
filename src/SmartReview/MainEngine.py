# -*- coding: utf-8 -*-
# @Time    : 2018/1/17 下午10:27
# @Author  : ZhangYaoWu
# @Email   : 852822425@qq.com
# @File    : MainEngine.py
# @Software: PyCharm
from SmartReview.UI import UIBase, UIConfig, UISearch
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QDialog, QTableWidgetItem, QTableWidget, QAction
from PyQt5.QtCore import Qt, QObject
from PyQt5 import QtGui
from SmartReview.Tactics import LearnTactics
import re
from SmartReview.Base import Record
from SmartReview.Base import Dictionary, Vocabulary
import json
import time
import logging
from SmartReview.Tools import pysay

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class SearchDialog(QDialog, UISearch.Ui_Dialog):
    """ 程序逻辑上的功能 """

    def __init__(self, *args, **kwargs):
        self.book = kwargs.pop('book')
        self.mainwindow = kwargs.pop('mainwindow')
        super(SearchDialog, self).__init__(*args, **kwargs)
        self.setupUi(self)  # 安装 UI

        self.set_tableContent(['单词', '释义'], self.wordsTable, self.find())
        self.wordEdit.textChanged.connect(self.autofind)  # 当文字改变就查找到对应的单词
        self.explainEdit.textChanged.connect(self.autofind)

    @classmethod
    def LoadFrom(cls, book, mainwindow):
        assert isinstance(book, Dictionary), "book 必须是 Dictionary 类型!"
        return cls(book=book, mainwindow=mainwindow)

    def show(self):
        self.wordEdit.setText('')
        self.explainEdit.setText('')
        super(SearchDialog, self).show()

    @pyqtSlot()
    def autofind(self):
        """ 自动寻找并且刷新列表 """
        word_pattern = self.wordEdit.text() if self.wordEdit.text() else '.*'
        explain_pattern = self.explainEdit.text() if self.explainEdit.text() else '.*'
        result = self.find(word_pattern, explain_pattern)
        self.set_tableContent(['单词', '释义'], self.wordsTable, result)

    def find(self, word_pattern='.*', explain_pattern='.*'):
        """ 从当前单词库中寻找已经存在的单词 """
        word_pattern = word_pattern.strip('\\[]')  # 清理特殊字符,防止意外退出
        explain_pattern = explain_pattern.strip('\\[]')
        if word_pattern == explain_pattern == '.*':
            return dict()
        else:
            if isinstance(self.book, Dictionary):
                result = {word.value: word.explain for word in self.book.values() if
                          re.search(word_pattern, word.value) and re.search(explain_pattern, word.explain)}  # 所有的单词
            else:
                result = {word: explain for word, explain in self.book.items() if
                          re.search(word_pattern, word) and re.search(explain_pattern, explain)}  # 所有的单词
            return result

    @staticmethod
    def set_tableContent(headerlabels, table, source):
        """ 用来设置列表的内容 """
        assert isinstance(source, dict), "参数 source 应当是一个 Dict 对象"
        table.setHorizontalHeaderLabels(headerlabels)  # 设置标题
        table.setColumnCount(2)  # 有两列
        table.setRowCount(len(source))  # 设置表的行数
        table.setEditTriggers(QTableWidget.NoEditTriggers)  # 不允许修改内容
        table.setSelectionBehavior(QTableWidget.SelectRows)  # 点击就是选择一行
        table.setSelectionMode(QTableWidget.SingleSelection)  # 多个可选
        for index, content in enumerate(source.items()):
            table.setItem(index, 0, QTableWidgetItem(str(content[0])))
            table.setItem(index, 1, QTableWidgetItem(str(content[1]).replace('\n',' ')))
        table.resizeColumnsToContents()

    def accept(self):
        """ 点击接受 """
        if self.wordsTable.selectedIndexes():
            word, explain = self.wordsTable.selectedIndexes()
            word = word.data()
            explain = explain.data()
            if self.mainwindow.word:
                cur_word = self.mainwindow.word  # 获取当前正在背的单词
                cur_word.associate.add(word)
            else:
                logger.warning('你当期没有正在背的单词,所以添加关联词失败!')
        super(SearchDialog, self).accept()


class ConfigDialog(QDialog, UIConfig.Ui_Dialog):
    """ 起到配置程序的目的 """

    def __init__(self, *args, **kwargs):
        super(ConfigDialog, self).__init__(*args, **kwargs)
        self.setupUi(self)  # 安装 UI
        self.book = LearnTactics.loadFrom()  # 加载单词书

        self.set_tableContent(['程度', '数量'], self.ranksTable, self.book.info_ranks, Vocabulary.default_ranks_chooses())
        self.set_tableContent(['时间', '数量'], self.timesTable, self.book.info_times, Vocabulary.default_times_chooses())
        self.countSlider.valueChanged.connect(self.countLCD.display)  # 先设定信号槽,这样 slider 设置初始值的时候,就会联动lcd
        self.ranksTable.itemSelectionChanged.connect(self.flush_selectedLCD)  # 当选择发生变化重新统计个数
        self.timesTable.itemSelectionChanged.connect(self.flush_selectedLCD)  # 当选择发生变化重新统计个数
        self.flush_selectedLCD()  # 刷新统计
        self.set_slider(self.countSlider)

#        def show(self):
#            # 每次界面弹出,需要显示的信息!
#            super(ConfigDialog, self).show()
            
    def flush_selectedLCD(self):
        ranks = self.get_selected_key(self.ranksTable)
        times = self.get_selected_key(self.timesTable)
        self.selectedLCD.display(self.book.size_of_needreview(ranks, times))  # 设置已选词汇数量

    @staticmethod
    def set_slider(slider, min=10, max=120, default=100):
        slider.setMinimum(min)  # 最少背 10 个单词
        slider.setMaximum(max)  # 最多背 120 个单词
        slider.setValue(default)  # 默认背 100个

    @staticmethod
    def set_tableContent(headerlabels, table, source, default_chooses=None):
        if default_chooses is None:
            default_chooses = list()
        assert isinstance(source, dict), "参数 source 应当是一个 Dict 对象"
        table.setHorizontalHeaderLabels(headerlabels)  # 设置标题
        table.setRowCount(len(source))  # 设置表的行数
        table.setEditTriggers(QTableWidget.NoEditTriggers)  # 不允许修改内容
        table.setSelectionBehavior(QTableWidget.SelectRows)  # 点击就是选择一行
        table.setSelectionMode(QTableWidget.MultiSelection)  # 多个可选
        for index, content in enumerate(source.items()):
            table.setItem(index, 0, QTableWidgetItem(str(content[0])))
            table.setItem(index, 1, QTableWidgetItem(str(content[1])))
            if content[0] in default_chooses:
                table.selectRow(index)
        table.resizeColumnsToContents()  # 依据列的内容调整列的宽度

    @staticmethod
    def get_selected_key(table):
        """ 获取表格中的背选中的值 """
        return [line.data() for line in table.selectedIndexes() if line.column() == 0]

    @staticmethod
    def get_selected_value(table):
        """ 获取表格中的背选中的值 """
        return [line.data() for line in table.selectedIndexes() if line.column() == 1]

    def accept(self):
        ranks = self.get_selected_key(self.ranksTable)
        times = self.get_selected_key(self.timesTable)
        if self.radioProportion.isChecked():  # 如果采用比例算法
            self.book.select_by_proportion(ranks, times, count=self.countSlider.value())
        elif self.radioPriority.isChecked():  # 如果采用优先级算法
            self.book.select(ranks, times, count=self.countSlider.value())
        else:
            raise NotImplementedError('你选择的算法暂时还没有实现!')
        super(ConfigDialog, self).accept()


class MainWindow(QMainWindow, UIBase.Ui_MainWindow):
    """ 程序界面上的功能 """

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)  # 安装 UI
        self.configDialog = ConfigDialog()
        self.book = self.configDialog.book
        self.searchDialog = SearchDialog.LoadFrom(self.configDialog.book, self)
        self.word = None  # 单词本身
        self.completed = False  # 背单词机器的标识, True 代表背词结束
        self.timeStart = None  # 按下去的时间戳
        self.timeEnd = None  # 松开的时间戳
        self.timeSpeed = None  # 按压的时间
        self.word_explain.hide()  # 刚开始不显示 word_explain
        self.word_status.hide()  # 刚开始不显示 word_status
        self.install_signals_and_slots()  # 安装信号槽机制

    def install_signals_and_slots(self):
        self.auto_speaker.toggled[bool].connect(self.muteEvent)  # 智能朗读
        self.word_status.toggled[bool].connect(self.switchStatus)  # 记住与忘记的状态转换
        self.configButton.clicked[bool].connect(self.configDialog.show)  # 显示配置界面
        self.associationButton.clicked[bool].connect(self.searchDialog.show)  # 配置添加关联词

    @pyqtSlot(bool)
    def muteEvent(self, turn_on):
        """ 配置是否智能朗读单词 """
        if turn_on is True:
            self.say('已开启智能朗读')
            self.auto_speaker.setText('智能朗读')
        else:
            self.auto_speaker.setText('已静音')
        logger.info('[MODE_SWITCH] mute is {}'.format(not turn_on))

    @pyqtSlot(bool)
    def switchStatus(self, status):
        """ 切换单词的状态 """
        if status is True:
            self.word_status.setText('已记住')
            self.word_explain.setStyleSheet('QLabel {background-color: none}')
        else:
            self.say('已忘记')
            self.word_status.setText('已忘记')
            if self.book.CheckMode is False:
                self.word_explain.setStyleSheet('QLabel {background-color: gray}')
        logger.debug('[STAUTS_SWITCH] word_status is {}'.format(status))

    def saveStatus(self):
        """ 设置单词的状态 """
        if self.word_status.isChecked():
            self.book.add_remember(self.word)  # 设置为记住状态
            logger.debug("{} marked remeber".format(self.word.value))
        else:
            self.book.add_forget(self.word)  # 设置为忘记状态
            logger.warning("{} marked forget".format(self.word.value))

    def switchWord(self):
        if self.word is not None:  # 如果单词存在
            self.saveStatus()  # 保存结果
            if self.timeStart > self.timeEnd:  # 按下按钮以后 timeStart 肯定是大于 timeEnd 的
                record = Record(speed=self.timeSpeed, timestamp=self.timeStart,
                                stats=self.word_status.isChecked())  # 生成记录
                logger.debug('{} added a new recode: {}'.format(self.word_before.text(), record))
                self.word.daylog.add_record(record)  # 添加到日志
        try:
            self.word_explain.hide()
            self.word_current.show()
            self.word = self.book.fetch()
            self.word_status.setChecked(True)  # 设置为记住
        except KeyError:
            self.say('已全部检查完毕!请手动按 ESC 来保存本次复习')
            self.completed = True
            self.word_current.setText('已全部检查完毕!')
            self.word = None
        else:
            if self.book.CheckMode is False:  # 在非检查模式下,才朗读!
                self.say(self.word.value, speaker='Ava')
            self.word_current.setText(self.word.value)  # 将当前单词的设置为内容

    def setExplain(self):
        """ 设置释义与进度 """
        self.word_current.hide()
        self.word_explain.show()
        if self.completed is True:
            smalltitle = '待保存...'
            explain = self.book.save_and_get_report()  # 显示单词掌握信息
            association = None
        else:
            smalltitle = self.word.value
            explain = self.word.explain
            association = ' | '.join(self.word.associate)  # 混淆词
        self.word_explain.setText(explain)  # 设置释义
        self.word_explain.setAlignment(Qt.AlignCenter)  # 将位置垂直中齐
        self.word_before.setText(smalltitle)  # 设置单词
        self.associationLabel.setText(association)  # 设置关联词
        print("进度 {}%".format(round(self.book.process*100,2)))
        self.speed_progress.setValue(self.book.process * 100)
        if self.completed is True:
            self.word_status.hide()  # 程序结束以后隐藏掉一些部件
            self.auto_speaker.hide()
        else:
            self.word_status.show()
            self.auto_speaker.show()

    def keyPressEvent(self, QKeyEvent):
        """ 按下事件 """
        if QKeyEvent.key() == Qt.Key_Control:  # 如果按下 Command 键
            logger.debug('key:{} is press'.format('Key_Control'))
            self.timeStart = time.time()
            self.switchWord()  # 切换到下一个单词
        elif QKeyEvent.key() == Qt.Key_Alt:  # 如果按下 空格
            logger.debug('key:{} is press'.format('Key_Alt'))
            if self.word_status.isChecked():
                self.word_status.setChecked(False)  # 表示忘记
            else:
                self.say(self.word.value, speaker='Ava')

    def keyReleaseEvent(self, QKeyEvent):
        """ 松开事件 """
        if QKeyEvent.key() == Qt.Key_Control:  # 如果松开 Command 键
            logger.debug('key:{} is release'.format('Key_Control'))
            self.timeEnd = time.time()
            self.timeSpeed = self.timeEnd - self.timeStart
            self.setExplain()
        if QKeyEvent.key() == Qt.Key_Escape:  # 如果松开 Escape 就保存
            self.configDialog.book.save()
            self.say('已保存!')
            self.word_before.setText('已保存')

    # def mousePressEvent(self, QMouseEvent):
    #     """ 鼠标按下事件 """
    #     if QMouseEvent.button() == Qt.LeftButton:
    #         logger.debug('Mousekey:{} is press'.format('LeftButton'))
    #         self.timeStart = time.time()
    #         self.switchWord()  # 切换到下一个单词
    #     if QMouseEvent.button() == Qt.RightButton:
    #         logger.debug('Mousekey:{} is press'.format('RightButton'))
    #         self.word_status.setChecked(False)  # 表示忘记
    #
    # def mouseReleaseEvent(self, QMouseEvent):
    #     """ 鼠标释放事件 """
    #     if QMouseEvent.button() == Qt.LeftButton:
    #         logger.debug('Mousekey:{} is release'.format('LeftButton'))
    #         self.timeEnd = time.time()
    #         self.timeSpeed = self.timeEnd - self.timeStart
    #         self.setExplain()

    def say(self, text, speaker=None, speed=4):
        """ 用来语音朗读 """
        if self.auto_speaker.isChecked() is False:  # 开启智能朗读的情况下才发音
            text = ''  # 如果不是采用这个方式,那些调用 say('hello').wait()的代码会报错!
        pysay.say(text,speaker,speed)

def main():
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    xx = MainWindow()
    xx.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
   main() 
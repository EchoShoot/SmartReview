# SmartReview
本人认为, 艾宾浩斯遗忘曲线仅反应了人类的遗忘大致规律. 但这种规律并不一定就符合每一个人的事实情况, 因为记忆力的好坏与 "记忆方法 \ 年龄 \ 身体状态" 都有着很大的关系.

![Image of SmartReview](intro/banner.png)

本单词智能复习项目:
- 设计之初采集了 "思考时间 \ 复习间隙 \ 学习难度..." 等多个维度数据, 为未来利用 "人工智能" 测量单词遗忘规律提供了前提数据基础.
- 暂时采用 "艾宾浩斯遗忘曲线 + 混淆关联词" 的记词方案作为过渡性方案, 并实际应用中帮助我记忆与巩固了 5500 多个考研词汇.


## 安装方式

![Image of download](intro/download.png)

将该项目下载到本地以后, cd 切换至 "SmartReview" 文件夹中, 输入以下命令:
```Shell
$ python3 setup.py install
```
> 详细安装方式请看 "[./SmartReview/SmartReview使用说明书.pdf](SmartReview使用说明书.pdf)"


## 使用方法
项目安装完毕后, 会为你配置两个命令行工具 "**smartload**" 与 "**smartreview**"
```Shell
$ smartload {你要导入 单词词库.json 的路径位置}  # 仅支持.txt\.json格式
$ smartreview  # 启动程序
```

### 使用流程:

![Image of UI](intro/uiMain.png)

1. 按下 ctrl(Windows) \ command(Macos) 弹出词汇, 回忆词汇含义, 松开键后查看含义核对含义.
2. 若记住了含义, 则重复 "步骤1". 否则敲击 "空格键" 将为该词汇标记为 "未记住".
3. 对于混淆的词汇, 点击 "添加混淆词". (支持正则表达式搜索单词)
4. 每次松开键后如果单词下方含有以前添加的混淆词, 你应该停留下来也尝试回忆词汇含义.
5. 当所有词汇都回顾完毕后, 手动按 ESC键 进行保存.
> 本软件会依据 "艾宾浩斯遗忘曲线" 并依据你对词汇的掌握程度自动分配下一次合适回顾词汇, 混淆词背词方案将有效的解决词汇混淆等问题.
> 更详细使用方法请看 "[./SmartReview/SmartReview使用说明书.pdf](SmartReview使用说明书.pdf)"


## 关于词库
在路径 "[./SmartReview/src/SmartReview/source](src/SmartReview/source)" 中有我在扇贝爬下来的词库:
* 考研单词.json
* 六级单词.json

> 如果需要**四级词汇**可以自己写爬虫去抓 [扇贝单词网-四级词汇](https://www.shanbay.com/wordbook/175219/), 或者联系我(BiarFordlander@gmail.com). 


### 导入格式:
通常 "txt格式" 用来添加自己生活中遇到的新词, "json格式" 用来添加网上抓的词库.

.json 格式
```json
[
  {"word":"hello", "explain":"你好"},
  {"word":"yes", "explain":"对"},
]
```

.txt 格式
```
hello, "你好"
yes "对"
nice
```
> - 可以选择"逗号"或"空格"来隔开单词与释义.
> - 如果没有填写单词释义, 将会自动调用有道词典来添加单词释义.

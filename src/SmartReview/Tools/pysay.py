def say(text, speaker=None, speed=4):
	""" 用来语音朗读 """
	from subprocess import Popen
	import sys
	import math
	
	assert isinstance(text, str), "只能语音播报 str 类型"
	assert 1 <= speed <= 10, "speed 范围在 1~10"
	rate = (30 + speed * 60)  # 计算速度
	
	if 'darwin' in sys.platform:  # 如果是 MacOS系统
		if speaker:
			return Popen(['say', text, '-v{}'.format(speaker), '-r{}'.format(rate)])
		return Popen(['say', text, '-r{}'.format(rate)])
	elif 'win32' in sys.platform:  # 如果是 Windows系统
		try:
			import win32com.client
		except ModuleNotFoundError as e:
			print('Please use "pip install pypiwin32" to fix this problem!')
		else:
			speaker = win32com.client.Dispatch("SAPI.SpVoice")
			speaker.Rate = rate
			speaker.Speak(text)
	else:
		raise Exception('''Your system is temporarily not supported!
						   You can use "pip uninstall pysay" remove 
						   this Module from your computer''')
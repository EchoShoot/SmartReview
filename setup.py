from setuptools import setup, find_packages

def get_install_requires():
	import sys
	install_requires = ['PyQt5==5.9.2',
					 'tqdm==4.19.5',
					 'requests==2.18.4',
					]
	if 'darwin' in sys.platform: # MacOS 系统
		pass
	elif 'win32' in sys.platform: # Windows 系统
		install_requires.extend(['pypiwin32'])
		
	return install_requires


setup(
	name='SmartReview',  # 项目名称
	version='1.0.1',  # 项目版本
	url='https://github.com/EchoShoot/SmartReview',  # 网址
	description='A high-level review vocabulary tool!',  # 简要描述
	author='ZhangYaowu',  # 作者
	maintainer='EchoShoot',  # 维护人(请各Fork本项目二次开发的朋友, 可在这里填入你的昵称)
	maintainer_email='BiarFordlander@gmail.com',  # 维护人的邮箱
	license='GPL',  # 请遵守GPL协议, 若需商用请找我单独授权!
	zip_safe=False,  # 有些工具不支持zip压缩，而且压缩后也不方便调试，建议设为 False!
	python_requires='>=3.6',  # 支持的 Py 版本
	packages=find_packages('src'),  # 包含所有src中的包
	package_dir = {'':'src'},  # 告诉distutils包都在src下
	include_package_data=True,
	# 包含 SmartReview 项目下 resouces 文件夹里面 所有的文件!
	entry_points={
			'console_scripts': ['smartreview = SmartReview.MainEngine:main',
			'smartload = SmartReview.Base:load']
	},
	install_requires = get_install_requires(),  # 模块所依赖的模块包
	classifiers=[
		'Module :: SmartReview',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GPL License',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3.6',
	],
)

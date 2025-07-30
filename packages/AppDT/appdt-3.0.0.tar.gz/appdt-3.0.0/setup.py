from setuptools import setup
 
setup(
    name='AppDT',
    version='3.0.0',
    description='(This Is A Chinese Package)此工具箱可以帮您快速构建Windows™应用程序，也可以快速生成安装包',
    long_description="""# AppDT
此工具箱可以帮您快速构建Windows应用程序，也可以快速生成安装包。安装完毕后请在命令行中输入“adt”来运行它
# Pyenvdler
此工具随AppDT第三方库版一起安装，exe安装包版暂不提供
- 使用方法：
- 在需要部署环境的目录下打开命令行，输入“Pyenvdler <需部署环境版本>”命令并执行即可""",
    long_description_content_type="text/markdown",
    author='xumouren225588',
    author_email='xumouren225588@163.com',
    url="https://github.com/xumouren225588/AppDT",
    packages=['AppDT'],
    license='Mulan Permissive Software License Version 2 (Mulan PSL v2)',
    install_requires=[
        'pyinstaller',
        'PyQt5',
        'chardet',
        "wget",
        "tqdm"
    ],
    python_requires='>=3.5',
    entry_points={
        'console_scripts': [
            'adt=AppDT.whlcode:adt',
            'pyenvdler=AppDT.whlcode:pyenvdler'
        ],
    },
    classifiers=[
        
        "Programming Language :: Python",
        "Operating System :: Microsoft :: Windows"
    ],
)

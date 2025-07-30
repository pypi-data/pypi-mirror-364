#Copyright (c) 2025 xumouren225588
#AppDT is licensed under Mulan PSL v2.
#You can use this software according to the terms and conditions of the Mulan
#PSL v2.
#You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
#THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY
#KIND, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
#NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
#See the Mulan PSL v2 for more details.
s4y1lh4w=1 #此处是调试点，如需调试，请将等号后面的数字改为您要调试的模块序号（默认第一个）

def adt():
    from PyQt5.QtWidgets import QApplication, QFileDialog
    
    def open_file_dialog():
        # 创建QApplication实例（这是必需的）
        app = QApplication([])
        # 弹出文件选择窗口
        file_path, _ = QFileDialog.getOpenFileName(None, "请选择icon图标", "", "icon图标 (*.ico);;")
        
        
    
        # 这里可以添加处理文件路径的代码
        if file_path:
            return file_path
    
        # 注意：在这个示例中，主窗口实际上并没有显示，所以我们不需要显式地关闭它
        # 如果你想要在某个时候显示主窗口，你可以调用 root.deiconify() 来恢复它
    def open_file_dialog2():
        # 创建QApplication实例（这是必需的）
        app = QApplication([])
        # 弹出文件选择窗口
        file_path, _ = QFileDialog.getOpenFileName(None, "请选择包含简介和声明的文件", "", "Text Files (*.txt);;Markdown Files (*.md);;All Files (*.*)")
        
        
    
        # 这里可以添加处理文件路径的代码
        if file_path:
            return file_path
    
        # 注意：在这个示例中，主窗口实际上并没有显示，所以我们不需要显式地关闭它
        # 如果你想要在某个时候显示主窗口，你可以调用 root.deiconify() 来恢复它
    
    import os
    sysdir22=os.getenv("SystemDrive")+"\\"
        
    import random
    import re
    while True:

        def extract_integer_after_minus(s):
            # 正则表达式匹配减号后的整数
            pattern = r'-(\d+)'
            match = re.search(pattern, s)
            if match:
                return int(match.group(1))  # 返回整数
            else:
                return None  # 如果没有匹配到则返回None
        print("欢迎使用软件开发和生成安装包工具（App Development Tools），作者：xumouren225588")
        atype_list=["[1]新建","[2]打开","[3]封装","[4]删除项目","[5]打开作者主页"]
        for b in range(len(atype_list)):
            print(atype_list[b])
        atype=str(input("请输入您要选择的功能前的序号："))

        if atype=="1":
            importname_list=[]
            filename=None
            V=None
            while True:
                filename=str(input("请输入您要创建的项目的名称："))
                def contains_invalid_chars(s):
                    # 正则表达式匹配除数字、大小写英文字母和下划线以外的字符
                    pattern = r'[^0-9a-zA-Z_]'
                    return re.search(pattern, s) is not None
         
                def starts_with_digit(s):
                    # 正则表达式匹配以数字开头的字符串
                    pattern = r'^[0-9].*'
                    return re.match(pattern, s) is not None
                a=contains_invalid_chars(filename)
                b=starts_with_digit(filename)
                if a or b or not(filename):
                    print("您输入的内容包含其他符号或者以数字开头或为空！")
                else:
                    break
            while True:
                V=input("请输入您要创建的项目的版本号（示例：1.1.2 禁止输入非数字或小数点字符）：")
                def contains_non_numeric_characters(s):
                    return not re.match(r'^[0-9.]*$', s)
                c=contains_non_numeric_characters(V)
                if c:
                    print("输入了非数字或小数点字符！")
                else:
                    break
            
            ifenter=input("请按回车键开始构建")
    
            
            
     
            
     
    
            print("正在构建……")
            
     
            # 创建进度条对象，初始化时设置总迭代次数
            
              # 增加进度条的进度
            try:
                os.mkdir(sysdir22+'项目')
            except FileExistsError:
                None
    
            # 关闭进度条
    
            try:
                os.makedirs(sysdir22+'软件项目\\'+filename,exist_ok=True)
            except FileExistsError:
                print('文件夹已存在')
            
    
            
            
            
            
            
           
            
            with open(sysdir22+'软件项目\\'+filename+'\\'+filename+".py","w",encoding="utf-8") as f:
                f.write("")
                
            
    
    
            with open(sysdir22+'软件项目\\'+filename+'\\'+"规格参数.txt","w",encoding='utf-8') as f:
                f.write(filename+'\n')
                f.write(str(V)+'\n')
                
            print("构建完成！")
            
            import subprocess
    
            
            first_subfolder2 = sysdir22+'软件项目\\'+filename+'\\'
    
            # 判断操作系统，选择合适的命令
    
            
    
            # 获取当前工作目录
    
     
            # 打开资源管理器并导航到当前工作目录
            subprocess.run(['explorer', first_subfolder2])
    
        elif atype=="2":
    

            # 指定要检查的文件夹路径
            folder_path = sysdir22+'软件项目\\'
     
            # 检查文件夹是否存在
            if os.path.exists(folder_path):
        
    
                from pathlib import Path
         
                def get_folder_paths(base_dir):
                    """
                    获取给定目录下所有子文件夹的路径
                    """
                    return [str(p) for p in Path(base_dir).iterdir() if p.is_dir()]
         
                def select_folder_by_number(base_dir):
                    """
                    通过控制台输入序号选择文件夹
                    """
                    folder_paths = get_folder_paths(base_dir)
                    for i, folder_path in enumerate(folder_paths, 1):
                        print(f"{i}. {folder_path}")
            
                    while True:
                        try:
                            selection = input("请输入序号选择文件夹: ")
                    
                    
                            index = int(selection) - 1
                            if 0 <= index < len(folder_paths):
                                return folder_paths[index]
                            else:
                                print("无效的序号，请重新输入。")
                        except ValueError:
                            print("非法输入，请输入一个整数。")
         
                base_dir = sysdir22+'软件项目\\'  # 替换为您的基础目录路径
                selected_folder = select_folder_by_number(base_dir)
        
                import subprocess
                # 打开资源管理器并导航到当前工作目录
                subprocess.run(['explorer', selected_folder])
            else:
                print("无项目")
    
        elif atype=="3":
            import os

            # 指定要检查的文件夹路径
            folder_path = sysdir22+'软件项目\\'
     
            # 检查文件夹是否存在
            if os.path.exists(folder_path):
        
                from pathlib import Path
         
                def get_folder_paths(base_dir):
                    """
                    获取给定目录下所有子文件夹的路径
                    """
                    return [str(p) for p in Path(base_dir).iterdir() if p.is_dir()]
         
                def select_folder_by_number(base_dir):
                    """
                    通过控制台输入序号选择文件夹
                    """
                    folder_paths = get_folder_paths(base_dir)
                    for i, folder_path in enumerate(folder_paths, 1):
                        print(f"{i}. {folder_path}")
            
                    while True:
                        try:
                            selection = input("请输入序号选择文件夹: ")
                    
                    
                            index = int(selection) - 1
                            if 0 <= index < len(folder_paths):
                                return folder_paths[index]
                            else:
                                print("无效的序号，请重新输入。")
                        except ValueError:
                            print("非法输入，请输入一个整数。")
         
                base_dir = sysdir22+'软件项目\\'  # 替换为您的基础目录路径
                selected_folder = select_folder_by_number(base_dir)
                cs35=selected_folder+"\\规格参数.txt"
                wdesktop=input("请输入您的项目的主程序在项目文件夹里的相对路径（包含后缀名）：")
                print("请选择您要添加的功能")
                def choose_set():
                    # 示例列表
                    items = ["生成快捷方式", "添加启动项", "设置安装程序图标", "添加声明文件"]
                    # 用于存储选中状态的字典，键为列表索引，值为True/False
                    selected = {i: False for i in range(len(items))}
                
                    while True:
                        # 清除屏幕（注意：在Windows中可能需要使用os.system('cls')）
                        
                        i2=1
                        # 显示列表和选中状态
                        for i, item in enumerate(items):
                            if selected[i]:
                                print("→"+str(i2)+item)
                            else:
                                print(" "+str(i2)+item)
                            i2+=1
                        # 允许用户输入
                        user_input = input("请输入序号选择项目（输入减号加序号清除选中，输入y保存并退出）：").strip()
                
                        # 处理用户输入
                        if user_input.lower() == 'y':
                            print("已保存选中项。")
                            return list(selected.values())
                            break
                        elif user_input.startswith('-'):
                            # 尝试清除选中状态
                            try:
                                index = int(user_input[1:])-1
                                if 0 <= index < len(items):
                                    selected[index] = False
                                else:
                                    print("无效的序号，请输入有效的序号。")
                            except ValueError:
                                print("无效的输入，请输入序号或y。")
                        else:
                            # 尝试选中项目
                            try:
                                index = int(user_input)-1
                                if 0 <= index < len(items):
                                    selected[index] = not selected[index]  # 切换选中状态
                                else:
                                    print("无效的序号，请输入有效的序号。")
                            except ValueError:
                                print("无效的输入，请输入序号或y。")

                set_list=choose_set()
                with open(cs35, "r", encoding='utf-8') as f:
                    lines = [line.rstrip('\n') for line in f]
                prname=lines[0]
                vers=lines[1]
                code1=None
                code2=None
                fp2=None
                fp3=None
                if set_list[0]:
                    code1=f"""
    def create_shortcut(self, exe_name, extract_path):
        vbs_script = '''
Set oShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
strTargetFile = "%s"
strShortcutPath = CreateObject("WScript.Shell").ExpandEnvironmentStrings("%%USERPROFILE%%") & "\\\\Desktop\\\\%s.lnk"
Set oShortcut = oShell.CreateShortcut(strShortcutPath)
oShortcut.TargetPath = strTargetFile
oShortcut.WindowStyle = 1
oShortcut.Description = "%s"
oShortcut.WorkingDirectory = ""
oShortcut.Save
        ''' % (exe_name, "{prname}", "{prname}")
        temp_vbs_file = os.path.join(os.environ['TEMP'], 'create_shortcut.vbs')
        with open(temp_vbs_file, 'w', encoding="cp936") as vbs_file:
            vbs_file.write(vbs_script)
        subprocess.run(['cscript', '//nologo', temp_vbs_file], check=True)
        os.remove(temp_vbs_file)

                    """
                    code4="self.create_shortcut(exe_name, extract_path)"
                else:
                    code1="    #code1"
                    code4="#code4"
                if set_list[1]:
                    code2="""
    def add_exe_to_startup(self, exe_path):
        try:
            if not os.path.exists(exe_path):
                messagebox.showerror("错误", "文件不存在：" + exe_path)
                return
            with reg.ConnectRegistry(None, reg.HKEY_CURRENT_USER) as hkey:
                with reg.OpenKey(hkey, 'Software\\\\Microsoft\\\\Windows\\\\CurrentVersion', 0, reg.KEY_WRITE) as base_key:
                    try:
                        with reg.OpenKey(base_key, 'Run', 0, reg.KEY_WRITE) as run_key:
                            reg.SetValueEx(run_key, os.path.basename(exe_path), 0, reg.REG_SZ, exe_path)
                    except FileNotFoundError:
                        with reg.CreateKey(base_key, 'Run') as run_key:
                            reg.SetValueEx(run_key, os.path.basename(exe_path), 0, reg.REG_SZ, exe_path)
        except PermissionError:
            messagebox.showerror("错误", "修改注册表需要管理员权限。")
        except Exception as e:
            messagebox.showerror("错误", str(e))
                    """
                    code5="self.add_exe_to_startup(exe_name)"
                else:
                    code2="    #code2"
                    code5="#code5"
                if set_list[2]:
                    print("请选择安装程序图标")
                    fp2=open_file_dialog()
                else:
                    fp2=None
                if set_list[3]:
                    print("请选择介绍和声明文件")
                    fp3=open_file_dialog2()
                    import chardet

                    with open(fp3, 'rb') as f:
                        raw_data = f.read(10000)  # 读取文件的前10000个字节
                    
                    # 使用chardet检测编码
                    result = chardet.detect(raw_data)
                    encoding2 = result['encoding']  # 获取检测到的编码
                    with open(fp3,"r", encoding=encoding2) as f:
                        text2=f.read()
                    code3=f"""
        scrollable_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=50, height=10)
        scrollable_text.grid(pady=20)
    
        # 向Text控件中插入一些文本
        scrollable_text.insert(tk.END, '''{text2}''')

                    """
                else:
                    code3="        #code3"
                ifenter=input(f"即将封装：{selected_folder}，请按回车键开始！")
                cs35=os.path.join(selected_folder, "规格参数.txt")
                

                import zipfile
                import os

                def make_zipfile(output_filename, source_dir):
                    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for root, dirs, files in os.walk(source_dir):
                            # 添加目录中的每一个文件
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, os.path.join(source_dir, '..'))
                                zipf.write(file_path, arcname)

                # 使用示例
                output_filename = 'build.zip'
                source_dir = selected_folder
                make_zipfile(output_filename, source_dir)
                with open('build.zip','rb') as f:
                    recode=f.read()
                import base64
                encoded_data = str(base64.b85encode(recode))
                
                with open(f"{prname}-{vers}-setup.py","w",encoding="utf-8") as f:
                    
                    f.write(f"""

import os
import tempfile
from base64 import b85decode
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tkinter import scrolledtext
import zipfile
import threading
import shutil
import subprocess
import winreg as reg

DATA = {encoded_data}

class SelfExtractingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("{prname}-{vers}-安装程序")

        # 设置默认解压路径
        self.default_extract_path = os.environ.get('localappdata', '') + "\\\\{prname}"

        # 创建UI组件
        self.create_widgets()

    def create_widgets(self):
        
{code3}
        
        # 解压路径输入框和按钮
        self.extract_path_label = tk.Label(self.root, text="选择安装路径：")
        self.extract_path_label.grid(pady=10)

        self.extract_path_entry = tk.Entry(self.root, width=50)
        self.extract_path_entry.grid(pady=10)
        self.extract_path_entry.insert(0, self.default_extract_path)

        self.browse_button = tk.Button(self.root, text="浏览", command=self.browse_folder)
        self.browse_button.grid(pady=10)

        # 解压按钮
        self.extract_button = tk.Button(self.root, text="现在安装", command=self.extract_files)
        self.extract_button.grid(pady=10)

        # 进度条
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.grid(pady=10)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.extract_path_entry.delete(0, tk.END)
            self.extract_path_entry.insert(0, folder_selected)

    def extract_files(self):
        extract_path = self.extract_path_entry.get()
        
        # 隐藏非进度条元素
        self.extract_path_label.grid_remove()
        self.extract_path_entry.grid_remove()
        self.browse_button.grid_remove()
        self.extract_button.grid_remove()
        
        # 创建解压线程
        threading.Thread(target=self.extract, args=(extract_path,)).start()

    def extract(self, extract_path):
        try:
            import os
            import tempfile
            tmpdir = tempfile.mkdtemp()
            zip_file_path = os.path.join(tmpdir, "setup.zip")
            with open(zip_file_path, "wb") as fp:
                fp.write(b85decode(DATA))
        
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                total_files = len(zip_ref.namelist())
                extracted_files = 0
                for file in zip_ref.namelist():
                    zip_ref.extract(file, extract_path)
                    extracted_files += 1
                    self.progress_bar["value"] = (extracted_files / total_files) * 100
                    self.root.update_idletasks()
            if tmpdir:
                import shutil
                shutil.rmtree(tmpdir, ignore_errors=True)
            
            # 创建快捷方式和添加到启动项的代码...
            exe_name = os.path.join(extract_path, "{prname}\\\\{wdesktop}")
            install_file1=os.path.join(extract_path, "{prname}")
            {code4}
            {code5}
            import os
            import shutil

            # 获取%appdata%环境变量的值
            appdata_path = os.getenv('APPDATA')

            # 定义你想要创建的文件夹名称
            folder_name = "{prname}"

            # 完整路径：%appdata%下的MyNewFolder
            full_folder_path = os.path.join(appdata_path, folder_name)
            os.makedirs(full_folder_path)
    
            # 定义要写入文件的名称和内容
            file_name = "path.txt"
            
            
            # 完整文件路径
            full_file_path = os.path.join(full_folder_path, file_name)
            
            # 写入文件
            with open(full_file_path, 'w') as file:
                file.write(install_file1)
            # 安装完成后显示成功消息，并关闭主窗口
            messagebox.showinfo("成功", "安装成功！")
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("错误", str(e))
            

{code1}

{code2}

if __name__ == "__main__":
    root = tk.Tk()
    app = SelfExtractingApp(root)
    root.mainloop()

    


                    """)
                try:
                    import subprocess
                    if fp2 is None:
                        subprocess.run(["pyinstaller","-F","-w",f"{prname}-{vers}-setup.py"], check=True)
                    else:
                       subprocess.run(["pyinstaller","-F","-w",f"--icon={fp2}",f"{prname}-{vers}-setup.py"], check=True)
                    import shutil
                    shutil.copy2(f"dist\\{prname}-{vers}-setup.exe",f"{prname}-{vers}-setup.exe")
                    
                    os.remove("build.zip")
                    os.remove(f"{prname}-{vers}-setup.py")
                    os.remove(f"{prname}-{vers}-setup.spec")
                    shutil.rmtree("build")
                    shutil.rmtree("dist")
                    
                    
                    print("封装完成！")
                except Exception as e:
                    print(f"发生错误：{e}")
            else:
                print("无项目")


    
        elif atype=="4":
            # 指定要检查的文件夹路径
            folder_path = sysdir22+'软件项目\\'
     
            # 检查文件夹是否存在
            if os.path.exists(folder_path):
                from pathlib import Path
         
                def get_folder_paths(base_dir):
                    """
                    获取给定目录下所有子文件夹的路径
                    """
                    return [str(p) for p in Path(base_dir).iterdir() if p.is_dir()]
         
                def select_folder_by_number(base_dir):
                    """
                    通过控制台输入序号选择文件夹
                    """
                    folder_paths = get_folder_paths(base_dir)
                    for i, folder_path in enumerate(folder_paths, 1):
                        print(f"{i}. {folder_path}")
            
                    while True:
                        try:
                            selection = input("请输入序号选择文件夹: ")
                    
                    
                            index = int(selection) - 1
                            if 0 <= index < len(folder_paths):
                                return folder_paths[index]
                            else:
                                print("无效的序号，请重新输入。")
                        except ValueError:
                            print("非法输入，请输入一个整数。")
         
                base_dir = sysdir22+'软件项目\\'  # 替换为您的基础目录路径
                selected_folder = select_folder_by_number(base_dir)
                
                import shutil
                shutil.rmtree(selected_folder)
                print("删除成功！")
        

                def has_subdirectories(folder_path):
                    for folder_name in os.listdir(folder_path):
                        if os.path.isdir(os.path.join(folder_path, folder_name)):
                            return True
                    return False
         
                # 使用示例
                folder_path = sysdir22+'软件项目\\'
                if has_subdirectories(folder_path):
                    None
                else:
                    import shutil
                    shutil.rmtree(folder_path)
                
            else:
                print("无项目")
        elif atype=="5":
            import webbrowser

            # 打开一个特定的网页
            webbrowser.open('https://gitee.com/xumouren225588/AppDT')
        else:
            print("无效命令！")


if __name__=="__main__" and s4y1lh4w==1: #序号：1
    adt()

def pyenvdler():
    
    import sys

    ver=sys.argv[1]

    import os
    print("正在下载运行环境……")
    import wget
    wget.download(f"https://mirrors.huaweicloud.com/python/{ver}/python-{ver}-embed-amd64.zip","embedtemp.zip")
    import zipfile
    from tqdm import tqdm
    def unzip_with_progress(zip_file_path, extract_to):
        with zipfile.ZipFile(zip_file_path) as zip_ref:
            total_files = len(zip_ref.infolist())
            with tqdm(total=total_files, unit='file') as pbar:
                for file_info in zip_ref.infolist():
                    zip_ref.extract(file_info, extract_to)
                    pbar.update(1)
    zip_file_path = 'embedtemp.zip'
    extract_to = "pyenv"
    print("\n正在解压……")
    unzip_with_progress(zip_file_path, extract_to)
    print("正在下载pip……")
    wget.download(f"https://mirrors.aliyun.com/pypi/get-pip.py","get-pip.py")
    import os

    appdata_roaming = os.getenv("APPDATA")
    pip_path = os.path.join(appdata_roaming, "pip")
    if os.path.exists(pip_path):
        None
    else:
        import os
        os.mkdir(pip_path)
        mirror=os.path.join(pip_path, "pip.ini")
        with open(mirror, "w", encoding="utf-8") as f:
            f.write('''
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
            ''')
    os.system(".\\pyenv\\python.exe .\\get-pip.py")
    your_directory = "pyenv"
    pth_files = [f for f in os.listdir(your_directory) if f.endswith("._pth")]
    
    first_pth_file_name = pth_files[0]
        
    # 打开文件并读取所有行
    file_path = os.path.join("pyenv",first_pth_file_name)  # 替换为你的文件路径
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 检查文件是否为空
    if lines:
        # 删除最后一行的所有井号
        last_line = lines[-1].rstrip('\n')  # 去掉最后一行末尾的换行符
        last_line = last_line.replace('#', '')  # 删除井号
        lines[-1] = last_line + '\n'  # 将修改后的内容写回最后一行

    # 将修改后的内容写回文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)
    print("下载完成！！")
if __name__=="__main__" and s4y1lh4w==2: #序号：2
    pyenvdler()

def home_page():
    import webbrowser
    
    # 打开一个特定的网页
    webbrowser.open('https://gitee.com/xumouren225588/AppDT')
if __name__=="__main__" and s4y1lh4w==3: #序号：3
    home_page()

# Copyright(C) 2013 Huangtao
#
# 库函数
# 模块：界面处理
# 作者：黄涛
# 创建：2013-5-26
# 修改：2013-8-20 新增bind的处理功能
from tkinter import *
from tkinter import messagebox as mb
import xml.etree.ElementTree as ET
from tkinter.ttk import *
from tkinter.font import Font
from functools import partial
from mylib.xmlfile import *
class UiMgr(XMLBase):
    '''
    窗口生成模块

    使用xml文件描述窗口，然后使用本模块生成窗口
    用法：ui=UiMgr()
          ui.create_frame(master,name,owner=None)
          ui.create_menu(master)
    '''
    def init(self):
        self.font=Font(family='微软雅黑',size=10)
        style=Style()
        style.configure('.',font='微软雅黑 10')

    def add_child(self,owner,master,node):
        for child in node:
            d=child.attrib.copy()
            if child.tag=='cascade':
                w=Menu(master,font=self.font)
                d['menu']=w
                if 'name' in d:
                    name=d.pop('name')
                    exec('owner.%s=w'%(name))
                master.add_cascade(d)
                self.add_child(owner,w,child)
            elif child.tag=='command':
                if 'command' in d:
                    if d['command'][0:5]=='part.':
                        d['command']=partial(owner.handle_menu,
                                name=d['command'][5:])
                    else:
                        d['command']=eval(".".join(("owner",d['command'])))
                master.add_command(d)
            elif child.tag=='separator':
                master.add_separator()
    
    def create_menu(self,master):
        '''
        增加主菜单

        参数说明：
        master:当前模块的实例
        '''
        node=self.root.find('./Menu[@name="mainmenu"]')
        if node:
            top=master.winfo_toplevel()
            master.mainmenu=Menu(top,font=self.font)
            top["menu"]=master.mainmenu
            self.add_child(master,master.mainmenu,node)

    def create_frame(self,master,name,owner=None):
        node=self.root.find("./Frame[@name='%s']"%(name))
        if owner is None:
            owner=master
        if node:
            d=node.attrib.copy()
            d.pop('name')
            if d:
                master.config(d)
            self.proc_child(owner,master,node)

    def proc_child(self,owner,master,node):
        for child in node:
            d=child.attrib.copy()
            if child.tag=='pack':
                master.pack(d)
            elif child.tag=='grid':
                master.grid(d)
            elif child.tag=='bind':
                if 'seq' in d: 
                    seq='<%s>'%d.get('seq')
                elif 'vseq' in d:
                    seq='<<%s>>'%d.get('vseq')
                if seq:
                    master.bind(seq,eval('owner.'+\
                        d.get('func')),d.get('add'))
            else:
                widget=eval(child.tag.capitalize())(master)
                if 'name' in d:
                    childname=d.pop('name')
                    exec('owner.%s=widget'%(childname))
                for key in d:
                    if key=='command':
                        d[key]=eval("owner.%s"%(d[key]))
                    elif key in ('textvariable','listvariable','variable'):
                        s=StringVar()
                        owner.var_list[d[key]]=s
                        d[key]=s
                widget.config(cnf=d)
                self.proc_child(owner,widget,child)

class BaseFrame(Frame):
    
    def __init__(self,master=None):
        super().__init__(master)
        self.var_list={}
        self.__data={}
        self.create()

    def __getitem__(self,index):
        if ',' in index:
            names=self.split_str(index,' ,\n\t')
            return tuple(self[name] for name in names)
        else:
            if index in self.var_list:
                return self.var_list[index].get() or None
            else:
                return self.__data.get(index)

    def __setitem__(self,index,value):
        if ','in index:
            names=self.split_str(index,' ,\n\t')
            if value:
                for i in range(len(names)):
                    self[names[i]]=value[i]
            else:
                for i in range(len(names)):
                    self[names[i]]=None
        if index in self.var_list:
            self.var_list[index].set(value or '')
        else:
            self.__data[index]=value or None
    
    def create(self):
        pass

    def init(self):
        pass

    def showerr(self,msg):
        mb.showerror(title='错误',message=msg)

    def showinfo(self,msg):
        mb.showinfo(title='提示信息',message=msg)
    
    def split_str(self,string,seps):
        t,d=0,[]
        string+=seps[0]
        for i in range(len(string)):
            if string[i] in seps:
                if i>t:
                    d.append(string[t:i])
                t=i+1
        return d

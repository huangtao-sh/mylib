#!/usr/bin/python3
# Copyright Huangtao
# 项目：函数库
# 模块：配置函数
# 创建：2013-12-30
# 修改：2013-12-31
# 修改：2014-07-22 采用全局资源模式，即所有的子类共享资源
from os.path import expanduser
from xml.etree.ElementTree import *
from xml.dom.minidom import parseString
from mylib.des import *
from mylib.stdlib import join,Linux,write_file
from re import compile 

class XMLBase():

    p1=compile(r"([a-zA-Z]+)((?:\[.*?\])*)")
    p2=compile(r"""\[@([a-zA-Z]+)=((?:'(.*?)')|(?:"(.*?)"))\]""")
    __config_modified=False
    
    @property
    def config_modified(self):
        return self.__config_modified  
    
    @config_modified.setter
    def config_modified(self,value):
        self.__config_modified=value

    def open_config(config_file_name):
        pass

    def __init__(self,config_file_name=None):
        if config_file_name:
            self.open_config(config_file_name)
    
    def getroot(self):
        return Element('root')

    def set_attrib(self,path,attrib=None):
        node=self.get_node(path)
        if node is not None:
            node.attrib=attrib
    
    def get_attrib(self,path):
        node=self.get_node(path,True)
        if node is not None:
            return node.attrib.copy()

    def parse_path(self,path):
        r=[]
        k=self.p1.findall(path)
        tag=""
        attr={}
        if k:
            tag=k[0][0]
            if len(k[0])>1:
                k=self.p2.findall(k[0][1])
                if k:
                    for i in k:
                        attr[i[0]]=i[2] if i[2] else i[3]     
        return tag,attr

    def get_node(self,path,exists=False):
        if exists:
            return self.config_root.find(path)
        else:
            node=self.config_root
            self.config_modified=True
            for p in path.split('/'):
                subnode=node.find(p)
                if subnode is None:
                    tag,attr=self.parse_path(p)
                    subnode=SubElement(node,tag)
                    if attr:
                        subnode.attrib=attr 
                node=subnode
            return node

    def save_config(self):
        if self.config_modified:
            xml=tostring(self.config_root).decode()
            dom=parseString(xml)
            xml=dom.toprettyxml(indent='    ',encoding='utf-8')
            d=['%s\n'%(x) for x in xml.decode().splitlines() if x.strip()]
            write_file(self.config_file_name,d)

class Config(XMLBase):
    __config_modified=False
    config_file_name=None
    config_root=None
    
    @staticmethod
    def open_config(config_file_name):
        self=Config
        try:
            self.config_file_name=config_file_name
            self.config_root=parse(config_file_name).getroot()
        except:
            self.config_root=self.getroot()
        self.config_modified=False
    
    @property
    def config_modified(self):
        return Config.__config_modified  
    
    @config_modified.setter
    def config_modified(self,value):
        Config.__config_modified=value
    
    @staticmethod
    def getroot():
        return Element('Config')
    
    def initial_path(self,path_type,path=None):
        os='linux' if Linux else 'windows'
        p="InitialPath[@os='%s']/Item[@type='%s']"%(os,path_type)
        node=self.config_root.find(p)
        if path:
            if node is None:
                node=self.get_node(p,False)
            elif path==node.attrib['dir']:
                return                            
            node.attrib={'type':path_type,'dir': path}
            self.config_modified=True
            self.save_config()
        else:
            p=node.attrib['dir'] if node is not None else '~'
            return expanduser(p)

    def my_cnf(self,name=None,cnf=None):
        return self.default_cnf('MySQL',name,cnf)

    def user_cnf(self,name=None,cnf=None):
        return self.default_cnf('User',name,cnf)
    
    def enum_cnf(self,section):
        node=self.get_node(section)
        if node is not None:
            return [child.tag for child in node] 
    
    def enum_user(self):
        return self.enum_cnf('User')

    def default_cnf(self,section,name=None,cnf=None):
        encrypt_key=['passwd','password']
        if name is None:
            attrib=self.get_attrib(section)
            if attrib:
                name=attrib.get('default')
            if name is None:
                name='default'
        path='/'.join([section,name])
        if cnf:
            for key in encrypt_key:
                if key in cnf:
                    cnf[key]=encrypt(cnf[key])
            self.set_attrib(path,cnf)
            attrib=self.get_attrib(section)
            attrib['default']=name
            self.set_attrib(section,attrib)
            self.save_config()
        else:
            cnf=self.get_attrib(path)
            if cnf:
                for key in encrypt_key:
                    if key in cnf:
                        cnf[key]=decrypt(cnf[key])
                return cnf
if __name__=='__main__':
    config=Config('mylib/prdmgr.xml')
    print(config.enum_user())

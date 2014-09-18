from configparser import *
from os.path import exists
from mylib.des import *
class Config:
    '''
    参数配置文件
    作者：黄涛
    创建：2013-7-25
    修改：
    '''
    def __init__(self):
        self.__parser=ConfigParser()
        self.parser.read('config.ini')
    @property
    def mycnf(self):
        d=self.read('MySQL')
        if 'passwd' in d:
            d['passwd']=decrypt(d['passwd'])
        return d
    @mycnf.setter
    def mycnf(self,cnf=None):
        if cnf:
            if 'passwd' in cnf:
                cnf['passwd']=encrypt(cnf['passwd'])
            self.write('MySQL',cnf)
    @property
    def parser(self):
        return self.__parser
    def read(self,section):
        return dict(self.parser[section])
    def write(self,section,cnf=None,**kwargs):
        if cnf is None:
            cnf={}
        cnf.update(kwargs)
        self.parser[section]=cnf
        self.save()
    def save(self):
        with open('config.ini','w') as fn:
            self.parser.write(fn)
    def InitDir(self,DirType,path=None):
        if 'InitDir' in self.parser.sections():
            if path:
                self.parser['InitDir'][DirType]=path
                self.save()
            else:
                if DirType in self.parser['InitDir']:
                    v=self.parser['InitDir'][DirType]
                else:
                    v=None
                return  v
        else:
            if path:
                self.parser['InitDir']={DirType:path}
                self.save()
'''
class xmlConfig:
    FileName='config.xml'
    def __init__(self):
        if  exists(self.FileName):
            self._xml=parse(self.FileName)
        else:
            self._xml=ElementTree()
            self._root=self._xml._setroot(Element('Config'))
        self._root=self._xml.getroot()
        self.modify=False
    def save(self):
        if self.modify:
            src=tostring(self.root,'utf-8')
            src=minidom.parseString(src)
            src=src.toprettyxml(indent='  ')
            r=ElementTree(fromstring(src))
            
            ElementTree(r).write(self.FileName)
    @property
    def MyConf(self):
        d=self.root.find('MySQL')
        if d:
            return d.attrib
    @MyConf.setter
    def MyConf(self,cnf={}):
        if cnf:
            e=self.root.find('MySQL')
            if e:
                e.attrib=cnf
            else:
                SubElement(self.root,'MySQL',attrib=cnf)
            self.modify=True
    @property
    def root(self):
        return self._root
'''

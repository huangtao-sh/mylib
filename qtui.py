#!/usr/bin/python3
# 项目：库函数
# 名称：QT5库函数
# 作者：黄涛
# 创建：2014-2-8
# 修订：2014-03-02　使用Dict来检索Window 和 Widget
#                   增加property name=value功能
#                   增加var varname=property功能
# 修订：2014-04-05  新增actiongroup相关功能
# 修订：2014-07-20  增加对PyQt4的支持
from sys import argv,exit
from os.path import splitext,join
from functools import partial
from datetime import datetime,date,time
try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import QIcon
    from PyQt5.QtCore import *
except:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
from mylib.textparser import parser
widgets={}
def get_propertys(widget):
    ps=widgets.get(widget.__class__)
    if ps is None:
        a=dir(widget)
        ps=dict((x.lower(),x)for x in a)
        widgets[widget.__class__]=ps 
    return ps

class MTableWidget(QTableWidget):
    def setData(self,data):
        self.setRowCount(len(data))
        for r,row in enumerate(data):
            for c,col in enumerate(row):
                self.setItem(r,c,QTableWidgetItem(col))

class MComboBox(QComboBox):

    def setCurrentText(self,value):
        pass
    def setItems(self,items):
        self.clear()
        self.addItems(items)
class MTextEdit(QTextEdit):

    def plainText(self):
        return self.toPlainText()

class QGui:
    ui_root=None
    __windows={}
    __widgets={}
    widget_propertys={}
    tools=('menubar','actions','toolbar')
    widgets={
            'label':QLabel,
            'lineedit':QLineEdit,
            'edit':QLineEdit,
            'pushbutton':QPushButton,
            'button':QPushButton,
            'datetimeedit':QDateTimeEdit,
            'groupbox':QGroupBox,
            'dateedit':QDateEdit,
            'combobox':MComboBox,
            'textedit':MTextEdit,
            'spinbox':QSpinBox,
            'treeview':QTreeView,
            'checkbox':QCheckBox,
            'plaintextedit':QPlainTextEdit,
            'tablewidget':MTableWidget,
            'table':MTableWidget,
            'list':QListWidget,
            }
    layouts={
            'form':QFormLayout,
            'vbox':QVBoxLayout,
            'hbox':QHBoxLayout,
            'grid':QGridLayout,
            }
    @staticmethod
    def main(Window):
        app=QApplication(argv)
        main_win=Window()
        exit(app.exec_())

    def showerr(self,msg):
        return QMessageBox.critical(self,'Error',msg)

    def showinfo(self,msg):
        return QMessageBox.information(self,'Information',msg)
    
    def get_open_files(self,title,init_dir=None,parttern=None):
        a=QFileDialog.getOpenFileNames(self,title,init_dir,parttern)
        if isinstance(a,tuple):
            a=a[0]
        return a 

    def get_save_file(self,title,init_dir=None,parttern=None):
        return QFileDialog.getSaveFileName(self,title,init_dir,parttern)

    def showask(self,msg):
        return QMessageBox.question(self,'Question',msg)

    def __init__(self,file_name):
        self.open_ui(file_name)

    @staticmethod
    def open_ui(file_name):
        self=QGui
        try:
            self.ui_root=parser(file_name)
        except:
            self.ui_root=[]
        self.__windows={}
        self.__widgets={}
        for node in self.ui_root:
            name=node.attrib.get('name').lower()
            if name:
                if node.tag=='window':
                    self.__windows[name]=node
                elif node.tag=='widget':
                    self.__widgets[name]=node

    def create_window(self,owner,name,content=None):
        node=parser(content=content) if content else \
            self.__windows.get(name.lower())
        if node is not None:
            cfg=node.attrib
            owner.menus={}
            if not hasattr(owner,'_actions'):
                owner._actions={}
            if not hasattr(owner,'actiongroups'):
                owner.actiongroups={}
            for child in node:
                tag=child.tag
                if tag=='link':
                    child=self.get_link(child)
                    tag=child.tag
                attrib=child.attrib
                if tag in self.tools:
                    getattr(self,'create_%s'%(tag))(child,owner)
                elif tag in self.layouts:
                    owner.setLayout(self.create_layout(child,owner,owner))
                elif tag == 'property': 
                    self.set_property(owner,owner,attrib)
                elif tag=='connect':
                    self.do_connect(owner,owner,attrib) 
                elif tag=='variable':
                    self.set_var(owner,owner,attrib)

    def create_layout(self,node,owner,head):
        attrib=node.attrib
        layout=self.layouts[node.tag]()
        for child in node:
            label=child.attrib.get('label')
            tag=child.tag
            widget=None
            if tag=='link':
                child=self.get_link(child)
                tag=child.tag
            if tag in self.widgets:
                widget=self.create_widget(child,owner,layout)
            elif tag in self.layouts:
                widget=self.create_layout(child,owner,layout)
            elif(tag=='stretch')and(node.tag in ['hbox','vbox']):
                layout.addStretch()
            elif tag == 'property': 
                self.set_property(owner,layout,child.attrib)
            if widget is not None:
                if node.tag=='form':
                    if label:
                        layout.addRow(label,widget)
                    else:
                        layout.addRow(widget)
                elif node.tag in ['hbox','vbox']:
                    if child.tag in ['hbox','vbox','form','grid']: 
                        layout.addLayout(widget)
                    else:
                        layout.addWidget(widget)
                elif node.tag=='grid':
                    pos=child.attrib.get('pos')
                    if pos:
                        args=[int(x) for x in pos.split(',')]
                    if child.tag in ['hbox','vbox','form','grid']: 
                        eval('layout.addLayout(widget,%s)'%(pos))
                    else:
                        eval('layout.addWidget(widget,%s)'%(pos))
        return layout
    
    def create_widget(self,node,owner,layout):
        cattrib=node.attrib
        ctext=cattrib.get('text')
        widget=self.widgets[node.tag](ctext)
        for child in node:
            tag=child.tag
            if tag=='link':
                child=self.get_link(child)
                tag=child.tag
            attrib=child.attrib
            if tag in self.layouts:
                widget.setLayout(self.create_layout(child,owner,owner))
            elif tag == 'property': 
                self.set_property(owner,widget,attrib)
            elif tag=='connect':
                self.do_connect(owner,widget,attrib) 
            elif tag=='variable':
                self.set_var(owner,widget,attrib)
        name=cattrib.get('name')
        if name:
            setattr(owner,name,widget)
        return widget
    
    def get_link(self,node):
        attrib=node.attrib
        name=attrib.get('target')
        if name:
            node=self.__widgets.get(name)
            return node.childs()[0]

    def set_var(self,owner,widget,attrib):
        for var,p in attrib.items():
            s=p.split('.')
            t=None
            if len(s)>1:
                p=s[0]
                t=eval(s[-1])
            owner.var_list[var]=WidgetVar(widget,p,t)

    def set_property(self,owner,widget,attrib):
        var=attrib.get('var')
        value=attrib.get('value')
        if var:
            v=WidgetVar(widget,attrib.get('name'))
            owner.var_list[var]=v
        elif value:
            eval('widget.set%s(%s)'%(attrib.get('name'),value))
        else:
            for p in attrib:
                eval('widget.set%s(%s)'%(p,attrib.get(p)))

    def do_connect(self,owner,widget,attrib):
        slot=attrib.get('slot')
        if slot:
            if not('.' in slot):
                slot='owner.%s'%(slot)
            eval('widget.%s.connect(%s)'%(attrib.get('singal'),
                slot))
        else:
            for singal in attrib:
                slot=attrib.get(singal)
                if not('.' in slot):
                    slot='owner.%s'%(slot)
                eval('widget.%s.connect(%s)'%(singal,
                    slot))

    def create_menubar(self,node,owner,head=None):
        head=QMenuBar()
        owner.setMenuBar(head)
        for child in node:
            try:
                self.create_menu(child,owner,head)
            except:
                pass
    
    def create_menu(self,node,owner,head=None):
        tag=node.tag
        if tag=='action':
            head.addAction(owner._actions[node.attrib.get('name')])
        elif tag=='separator':
            head.addSeparator()
        elif tag=='menu':
            head=head.addMenu(node.attrib.get('text'))
            ag=node.attrib.get('actions')
            if ag:
                head.addActions(owner.actiongroups.get(ag).actions())
            for child in node:
                self.create_menu(child,owner,head)
            name=node.attrib.get('name')
            if name:
                owner.menus[name]=head
        elif tag=='toolbar':
            head=owner.addToolBar(node.attrib.get('text'))
            for child in node:
                self.create_menu(child,owner,head)
    
    create_toolbar=create_menu

    def create_actions(self,node,owner,head=None):
        agname=node.attrib.get('name')
        if agname:
            ag=owner.actiongroups.get(agname,None)
            if ag is None:
                ag=QActionGroup(owner)
                owner.actiongroups[agname]=ag
        for child in node:
            attr=child.attrib
            name=attr.get('name')
            if child.tag=='separtor':
                action=QAction(owner)
                action.setSeparator(True)
            else:
                triggered=attr.get('triggered')
                text=attr.get('text')
                shortcut=attr.get('shortcut')
                tip=attr.get('tip')
                action=QAction(text,owner,statusTip=tip)
                icon=attr.get('icon','')
                if icon:
                    icon=QIcon(join(owner.base_dir,icon))
                    action.setIcon(icon)
                if shortcut:
                    action.setShortcut(shortcut)
                if triggered:
                    if triggered.startswith('part.'):
                        action.triggered.connect(
                            partial(owner.add_child,
                            triggered[5:]))
                    else:
                        if '.' not in triggered:
                            triggered='owner.%s'%(triggered)
                        action.triggered.connect(
                                eval(triggered))
            if agname:
                ag.addAction(action)
            if name:
                owner._actions[name]=action
                
class MainWindow(QMainWindow):
    def __init__(self):
        self.title=''
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.ui_file=splitext(argv[0])[0]+'.gui'
        self.ui_name='MainWindow'
        self.status_bar=self.statusBar() 
        self.init_ui()       
        try:
            self.ui=QGui(self.ui_file)
            self.ui.create_window(self,self.ui_name)
        except:
            pass
        self.move((qApp.desktop().width()-self.width())/2,
                (qApp.desktop().height()-self.height())/2)
        self.setWindowTitle(self.title)
        self.show()

class MDIWindow(MainWindow):
    def init_ui(self):
        self.mdiArea = QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCentralWidget(self.mdiArea)
        self.activate_next=self.mdiArea.activateNextSubWindow
        self.activate_prev=self.mdiArea.activatePreviousSubWindow
        self.cascade_childs=self.mdiArea.cascadeSubWindows
        self.tile_childs=self.mdiArea.tileSubWindows
        self.close_childs=self.mdiArea.closeAllSubWindows
        self.mdiArea.subWindowActivated.connect(self.sub_activated)
        #self.mdiArea.closeActiveSubWindow=self.close_child
        self.childs={}

    def create_widget(self,name):
        pass

    def add_child(self,name,initial=None,submit=False):
        w=self.childs.get(name)
        if w:
            self.mdiArea.setActiveSubWindow(w)
            child=w.widget()
        else:
            child=self.create_widget(name)
            if child:
                if hasattr(child,'initial'):
                    child.update_data(child.initial)
                w=self.mdiArea.addSubWindow(child)
                child.owner=w
                w.destroyed.connect(self.close_child)
                x=(self.mdiArea.width()-w.width())/2
                y=(self.mdiArea.height()-w.height())/2
                w.move(x,y)
                w.show()
                self.childs[name]=w
        if initial:
            child.update_data(initial)
        
        if submit and hasattr(child,'submit'):
            child.submit()
        return child
    
    def close_child(self,w):
        keys=[k for k,v in self.childs.items() if v==w]
        [self.childs.pop(k) for k in keys]
        '''
        for k in self.childs:
            if self.childs[k]==w:
                break
        else:
            return
        self.childs.pop(k)
        '''
    def sub_activated(self,sub):
        title=self.title
        if sub:
            title='%s [ %s ]'%(title,sub.windowTitle())
        self.setWindowTitle(title)

class WidgetVar:
    
    def __init__(self,widget,property_,tp=None):
        property_=property_.lower()
        if tp:
            self.out_type=tp
        ps=get_propertys(widget)
        g=ps.get(property_)
        s=ps.get('set'+property_)
        if g:
            self.get_method=getattr(widget,g)
            self.in_type=type(self.get_method())
        if s:
            self.set_method=getattr(widget,s)

    def get(self):
        try:
            var=self.get_method()
            if hasattr(self,'out_type'):
                var=convert(var,self.out_type)
            return var
        except:
            pass

    def set(self,value):
        try:
            if hasattr(self,'in_type'):
                value=convert(value,self.in_type)
            self.set_method(value)
        except:
            pass

class Widget(QWidget):
    
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.var_list={}
        self.__data={}
        self.init_ui()
    showerr=QGui.showerr
    showinfo=QGui.showinfo
    showask=QGui.showask
    get_open_files=QGui.get_open_files
    get_save_file=QGui.get_save_file

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
            if value is None:
                value=''
            self.var_list[index].set(value)
        else:
            self.__data[index]=value or None
    
    def init_ui(self):
        pass

    def init(self):
        pass

    def update_data(self,data):
        for k,v in data.items():
            self[k]=v

    def split_str(self,string,seps):
        t,d=0,[]
        string+=seps[0]
        for i in range(len(string)):
            if string[i] in seps:
                if i>t:
                    d.append(string[t:i])
                t=i+1
        return d

    def close(self):
        self.owner.close()

def convert(var,tp=str,fmt=None):
    
    def to_int(var,fmt):
        try:
            if type(var) in (date,QDate,QDateTime):
                var=to_datetime(var,fmt)
            if type(var) in(float,str):
                return int(var)
            if isinstance(var,bool):
                return 1 if var else 0
            elif isinstance(var,datetime):
                return var.toordinal()            
        except:
            pass
    def to_float(var,fmt):
        try:
            if isinstance(var,QTime):
                var=var.toPyTime()
            if type(var)in(date,QDate,QDateTime):
                var=to_datetime(var,fmt)
            if type(var) in(int,str):
                return float(var)
            if isinstance(var,bool):
                return 1.0 if var else 0.0
            elif isinstance(var,datetime):
                return var.toordinal()+((var.second/60+var.minute)/60+var.hour)/24      
            elif isinstance(var,time):
                return ((var.second/60+var.minute)/60+var.hour)/24
        except:
            pass
    def to_str(var,fmt):
        if var is not None:
            if type(var) in (QDate,QTime,QDateTime):
                var=to_datetime(var,fmt)
            if fmt:
                return format(var,fmt)
            else:
                return '%s'%(var)
        else:
            return ''

    def to_bool(var,fmt):
        return True if var else False
    
    def to_QDate(var,fmt):
        dt=to_datetime(var,fmt)
        if dt:
            return QDate(dt.date())
    
    def to_QTime(var,fmt):
        dt=to_datetime(var,fmt)
        if dt:
            return QTime(dt.time())
    
    def to_QDateTime(var,fmt):
        dt=to_datetime(var,fmt)
        if dt:
            return QDateTime(*dt.timetuple()[:6])

    def to_time(var,fmt):
        dt=to_datetime(var,fmt)
        if dt:
            return dt.time()

    def to_datetime(var,fmt):
        if True:
            if isinstance(var,str):
                try:
                    var=float(var)
                except:
                    return datetime.strptime(var,'%Y-%m-%d %H:%M:%S')
            if type(var)==QDate:
                var= var.toPyDate()

            if type(var)==QTime:
                var=var.toPyTime()
            if isinstance(var,QDateTime):
                return var.toPyDateTime()

            elif isinstance(var,float):
                d=int(var)
                dt=datetime.fromordinal(d) if d else datetime()
                d=(var-d)*24
                h=int(d)
                d=(d-h)*60
                m=int(d)
                d=(d-m)*60
                s=int(d)
                return dt.replace(hour=h,minute=m,second=s) 
                
            elif isinstance(var,int):
                if var:
                    return datetime.fromordinal(var)
            elif type(var) in(date,datetime):
                return datetime(*var.timetuple()[:7])
            elif isinstance(var,time):
                return datetime(1,1,1,var.hour,var.minute,var.second)
            
        else:
            return None

    def to_date(var,fmt):
        dt=to_datetime(var,fmt)
        if dt:
            return dt.date()
    func={
            str:to_str,
            bool:to_bool,
            int:to_int,
            float:to_float,
            datetime:to_datetime,
            QDateTime:to_QDateTime,
            time:to_time,
            QTime:to_QTime,
            date:to_date,
            QDate:to_QDate,
            }
    return var if isinstance(var,tp) else func[tp](var,fmt)
if __name__=='__main__':
    a=[
        QDate(2015,1,2),
        QDateTime(2012,3,5,14,20),
        QTime(1,0,0),
        100000.5,
        1000000.73,
        '2013-01-01 10:43:23',
        '2014-2-23   10:25:01',
        date(2014,5,6),
        time(10,25,30),
        datetime(2014,4,3,10,25),
        True,
        False,
        0,
    ]
    for x in a:
        print(convert(x,float))



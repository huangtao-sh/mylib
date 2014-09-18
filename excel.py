# Copyright(C) Huangtao
# 项目：公共模块
# 模块：Excel读写模块
# 作者：黄涛
# 创建：2013-8-27
# 修改：2013-8-28 如果有打开的Excel文件，Excel不再退出 

from win32com.client import Dispatch
class Excel():

    def __init__(self,filename=None,sheetname=None):
        self.book=None
        self.sheet=None
        self.application=Dispatch('Excel.Application')
        self.application.visible=1
        if filename:
            self.book=self.application.workbooks.open(filename)
        if sheetname:
            self.sheetname=sheetname
    
    def add_book(self):
        self.book=self.application.workbooks.add()
   
    def close(self):
        if self.book:
            self.book.close

    def save_as(self,name):
        name=name.replace('/','\\')
        self.book.SaveAs(name)

    @property
    def sheetname(self):
        return self.sheet.name
    
    @sheetname.setter
    def sheetname(self,name=None):
        self.sheet=self.book.Sheets(name)
        self.sheet.name=name

    def save(self):
        if not self.book.saved:
            self.book.save;

    def quit(self):
        self.close()
        if self.application.workbooks.count==0:
            self.application.quit()
        del self.application

    def get_text(self,row,col):
        return self.sheet.Cells(row,col).Text

    def set_value(self,row,col,value):
        self.sheet.Cells(row,col).Value=value

    def get_value(self,row,col):
        return self.sheet.Cells(row,col).Value

if __name__=='__main__':
    excel=Excel()
    try:
        excel.add_book()
        excel.set_value(1,1,'hello')
        excel.save_as('d:/abc.xls')
    finally:
        excel.quit()

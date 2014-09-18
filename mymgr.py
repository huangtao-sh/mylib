#  MySQL 处理模块
#  作者：黄涛
#  创建：2013-5-30
#  修改：2013-6-15 新增MyMgr类，采用面象对象的方式进行编程
#  修改：2014-01-25 新增分拆数据的功能，split_data函数，同时将
#                   exec及texec的数据修改为分批次执行
#  调用方法：exec(sql)
#            query(sql,proc)
from mysql import connector
from threading import Thread

class MyMgr:
    '''
    MySQL连接组件
    用法：
        m=MyMgr(cnf)
        m.execute(sql,params,multi)执行SQL语句
        m.query(sql,params,multi,proc)执行查询，其中proc为回调函数
        m.exec_many(sql,params_list)批量执行SQL语句
        m.texec(sql,params_list)使用线程批量执行SQL语句
        m.tquery(sql,params,multi,proc)使用线程执行查询，其中proc为回调函数
    '''
    def __init__(self,cnf=None):
        self.connected=False
        self.my=None
        self.cur=None
        self.cnf=cnf
        try:
            self.my= connector.connect(**self.cnf)
            self.connected=True
            self.cur=self.my.cursor()
        except BaseException as err:
            print(err)

    def __del__(self):
        if self.connected:
            if self.cur:
                self.cur.close()
            self.my.close()
    
    def call_proc(self,proc_name,args=None,proc=None):
        if self.connected:
            d=self.cur.callproc(proc_name,args)
            if proc:
                data=[result for result in self.cur.stored_results()]
                if len(data)==1:
                    proc(data[0])
                else:
                    proc(data)
            return d

    def execute(self,sql,params=None,multi=None):
        '''
        执行单一SQL语句
        参数说明：
            sql:SQL语句，如"select * from T1 where dt=%s"
            params:SQL语中的变量，形式如(123,'hunter')
            multi:是否执行多条语句，True 或 False
        '''
        self.query(sql,params,multi)
        self.my.commit()

    
    @staticmethod
    def split_data(data,step=10000):
        b,e=0,0
        count=len(data)
        for e in range(step,count,step):
            yield data[b:e]
            b=e
        if e<count:
            yield data[e:count]

    def exec_many(self,sql,sql_params):
        '''
        执行多条SQL语句
        参数说明：
            sql:SQL语句
            sql_params:SQL语句中的变量，形式如：(('123',12),('456',45))
        '''
        if self.connected:
            try:
                for params in self.split_data(sql_params):
                    self.cur.executemany(sql,params)
                self.my.commit()
            except BaseException as err:
                print(err)

    def query(self,sql,params=None,multi=None,proc=None):
        '''
        执行SQL查询，查询成功后调用proc函数
        参数说明：
            sql:SQL语句
            params:参数值，形式如：('123',45)
            multi:是否执行多条语句，True 或 False
            proc：回调函数，原型为：proc(cursor)
        '''
        if self.connected:
            self.cur.execute(sql,params=params,multi=multi)
            if proc:
                proc(self.cur)
            else:
                return self.cur
                

    def query_str(self,sql,params=None,multi=None):
        self.query(sql,params,multi)
        d=self.cur.fetchall()
        if d:
            return d[0][0]

    def query_list(self,sql,params=None,multi=None,direction=0):
        self.query(sql,params,multi)
        d=self.cur.fetchall()
        if d:
            if direction:
                return d[0]
            else:
                return tuple(r[0] for r in d)

        
    def exec_thread(self,func,arg):
        if self.connected:
            m=MyMgr(self.cnf)
            eval("Thread(target=m.%s,args=arg).start()"%(func))

    def texec(self,sql,sql_params):
        '''
        使用线程执行SQL语句。参数说明同execmany
        '''
        self.exec_thread("exec_many",(sql,sql_params))

    def tquery(self,sql,params=None,multi=None,proc=None):
        '''
        使用线程执行查询，参数说明同query
        '''
        self.exec_thread("query",(sql,params,multi,proc))
 
if __name__=='__main__':
    help(MyMgr)
 

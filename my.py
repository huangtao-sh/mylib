#  MySQL 处理模块
#  作者：黄涛
#  创建：2014-7-21
#  调用方法：exec(sql)
#            query(sql,proc)

from mysql import connector
from threading import Thread

class Mysql:
    '''
    MySQL连接组件
    用法：
        m=MyMgr(mysql_cnf)
        m.execute(sql,params,multi)执行SQL语句
        m.query(sql,params,multi,proc)执行查询，其中proc为回调函数
        m.exec_many(sql,params_list)批量执行SQL语句
        m.texec(sql,params_list)使用线程批量执行SQL语句
        m.tquery(sql,params,multi,proc)使用线程执行查询，其中proc为回调函数
    '''

    mysql_cnf=None
    __connection=None
    __cursor=None
    connected=False

    @staticmethod
    def connect_(kwargs):
        self=Mysql
        if kwargs:
            Mysql.mysql_cnf=kwargs
        self.disconnect()
        self.__connection=connector.connect(**Mysql.mysql_cnf)
        self.__cursor=self.__connection.cursor()
        self.connected=True

    @staticmethod
    def disconnect():
        Mysql.connected=None
        try:
            if Mysql.__cursor:
                Mysql.__cursor.close()
            if Mysql.__connection:
                Mysql.__connection.close()
        finally:
            Mysql.__cursor=None
            Mysql.__connection=None
    
    def call_proc(self,proc_name,args=None,proc=None):
        if self.connected:
            d=self.__cursor.callproc(proc_name,args)
            if proc:
                data=[result for result in self.__cursor.stored_results()]
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
        self.__connection.commit()
    
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
                    self.__cursor.executemany(sql,params)
                self.__connection.commit()
            except BaseException as err:
                print(err)

    def query(self,sql,params=None,multi=None,proc=None):
        '''
        执行SQL查询，查询成功后调用proc函数
        参数说明：
            sql:SQL语句
            params:参数值，形式如：('123',45)
            multi:是否执行多条语句，True 或 False
            proc：回调函数，原型为：proc(__cursor)
        '''
        if self.connected:
            self.__cursor.execute(sql,params=params,multi=multi)
            if proc:
                proc(self.__cursor)
            else:
                return self.__cursor
                

    def query_str(self,sql,params=None,multi=None):
        self.query(sql,params,multi)
        d=self.__cursor.fetchall()
        if d:
            return d[0][0]

    def query_list(self,sql,params=None,multi=None,direction=0):
        self.query(sql,params,multi)
        d=self.__cursor.fetchall()
        if d:
            if direction:
                return d[0]
            else:
                return tuple(r[0] for r in d)

        
    def exec_thread(self,func,arg):
        if self.connected:
            try:
                m=Mysql()
                m.__connection=connector.connect(**Mysql.mysql_cnf)
                m.__cursor=m.__connection.cursor()
                m.connected=True
                Thread(target=func(m,*arg)).start()
            finally:
                m.__cursor.close()
                m.__connection.close()

    def texec(self,sql,sql_params):
        '''
        使用线程执行SQL语句。参数说明同execmany
        '''
        self.exec_thread(Mysql.exec_many,(sql,sql_params))

    def tquery(self,sql,params=None,multi=None,proc=None):
        '''
        使用线程执行查询，参数说明同query
        '''
        self.exec_thread(Mysql.query,[sql,params,multi,proc])

if __name__=='__main__':
    m=Mysql()
    mysql_cnf={
            'host':'localhost',
            'user':'hunter',
            'passwd':'123456',
            'db':'prdmgr',}
    m.connect(mysql_cnf)
    k=m.query('select * from branch')
    for r in k:
        print(r)

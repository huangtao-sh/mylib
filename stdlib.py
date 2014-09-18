import os
import sys
from shutil import copy,copytree,rmtree
from codecs import BOM_UTF8,BOM_LE,BOM_BE
from filecmp import dircmp
from datetime import date,timedelta

Linux= True if sys.platform.startswith('linux') else False

# join函数的格式化版，可以保持分隔符的统一
# 默认在WINDOWS平台下使用“\”，在Linux平台下使用“/”

def join(*args,sep=os.path.sep):
    path=os.path.join(*args)
    old_sep='/' if sep=='\\' else '\\'
    return os.path.join(*args).replace(old_sep,sep)

# 写文本文件，使用utf-8编码，不带BOM
def write_file(file_name,text,encoding='utf-8'):
    with open(file_name,'w',encoding=encoding) as fn:
        if isinstance(text,list):
            fn.writelines(text)
        else:
            fn.write(text)
        
BOM_CODE={
    BOM_UTF8:'utf_8',
    BOM_LE:'utf_16_le',
    BOM_BE:'utf_16_be',
    }
    
DEFAULT_CODES=['utf8','gbk','utf16','big5']

def decode_file(d):
    for k in BOM_CODE:
        if k==d[:len(k)]:
            text=d[len(k):].decode(BOM_CODE[k])
            return text.splitlines()
    for encoding in DEFAULT_CODES:
        try:
            text=d.decode(encoding)
            return text.splitlines()
        except:
            continue
    raise Exception('解码失败')    

# 全部读取文件，并进行解码，解码失败则触发异常
def read_file(file_name):
    with open(file_name,'rb')as fn:
        return decode_file(fn.read())

# 以源目录为基准，更新目标目录的文件，仅复制需要更新的文件
def smart_copy(src,dest,ignore=None):
    dc=dircmp(src,dest,ignore=ignore)
    #删除目标中不存在的文件
    for f in dc.right_only:
        f=join(dc.right,f)
        if os.path.isdir(f):
            rmtree(f)
        else:
            remove(f)
        print('文件 %s 已被删除。'%(f))
    #拷备目标目录中不存在的文件
    for f in dc.left_only:
        sf=join(dc.left,f)
        if os.path.isdir(sf):
            copytree(sf,join(dc.right,f))
        else:
            copy(sf,dc.right)
        print('文件或目录 %s 已被更新'%(sf))
    #更新不同文件
    for f in dc.diff_files:
        f=join(dc.left,f)
        copy(f,dc.right)
        print('文件 %s 已被更新。'%(f))
    #处理子文件夹
    for d in dc.common_dirs:
        smart_copy(join(dc.left,d),join(dc.right,d))

def leap_year(year):
    return year%400==0 or(year%4==0 and year%100!=0)
    
def end_of_month(date):
    return (date+timedelta(days=1)).day==1    
    
def year_frac(begin,end,basis=0):
    BASIS={
        '30/360':0,
        'ACT/365':1,
        'ACT/360':2,
        'AFI/365':3,
        '30E/360':4,
        'YMD':5,
        }
    if isinstance(basis,str):
        basis=BASIS[mode]
    if basis in (1,2,3):
        days=(end-begin).days
    else:
        days=(end.year-begin.year)*360+(end.month-begin.month)*30
    
    if basis in (4,5):
        d1=30 if begin.day>30 else begin.day
        d2=30 if end.day>30 else end.day
        if basis==5:
            if (end_of_month(end)and(d1>d2)):
                d2=d1
        days+=d2-d1
    if basis ==0:
        d1=30 if end_of_month(begin) else begin.day
        d2=30 if end_of_month(end) else end.day
        if(end.day==31)and(begin.day<30):
            d2=31
        days+=d2-d1
        
    if basis in (0,2,4,5):
        base=360
    elif basis==3:
        base=365
    elif basis==1:
        if end.year==begin.year:
            base=366 if leap_year(begin.year) else 365
        elif(end.year-begin.year==1)and((end.month<begin.month)or(end.month==begin.month and end.day<=begin.day)):
            if(leap_year(begin.year))and(begin<=date(begin.year,2,29)):
                base=366
            elif(leap_year(end.year))and(end>=date(end.year,2,29)):
                base=366
            else:
                base=365
        else:
            base=sum([366 if leap_year(y) else 365 for y in range(begin.year,end.year+1)])/(end.year-begin.year+1)
    return days,days/base
    
def date_add(day,years=0,months=0,days=0,weeks=0):
    '''
    日期加减函数，如果是整年、整月，如无对应日期，则以到期月份的月底
    '''
    m=(day.year+years)*12+day.month+months-1
    try:
        day=day.replace(year=m//12,month=m%12+1)
    except:
        m+=1
        days-=1
        day=day.replace(year=m//12,month=m%12+1,day=1) 
    days+=weeks*7
    if days:
        day=day+timedelta(days=days)
    return day
    
def delta(base,target):
    a,b=set(base),set(target)
    return list(a-b),list(b-a)

if __name__=='__main__':
    print(delta(['a','b','c'],['c','d']))

from mylib.pyDes import *
'''
DES加解密库函数
作者：黄涛
创建：2013-7-25
'''
def __get_des():
    return des(key='huangtao',padmode=PAD_PKCS5)
def encrypt(astr):
    b=__get_des().encrypt(astr)
    return "".join(['%02X'%(x)for x in b])
def decrypt(astr):
    b=__get_des().decrypt(bytes.fromhex(astr))
    return b.decode('utf8')

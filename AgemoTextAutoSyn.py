'''
本程序可以自动同步文本，通常用于同一个游戏的不同平台间的文本移植。
版本v1.0:
创建
版本v1.1:
不比较\n,\t,以及空格，替换方式改为字符串map方式。
将已经翻译的文本放到src_eng和src_chs中，必须一一对应，根据此文本生成一个字典。
字典中key为原文文本，value为中文文本。重复文本会使用最后一个中文文本覆盖。
des中放要处理的原文文本，拿文本去比较，相同的用中文文本覆盖。不同的清空。然后覆盖des中文件。
版本v1.2:
des中文件新生成时要保留agemo原标题
增加清空标志，为True时才清空，否则保留
版本v1.3:
对于无法同步的文本，打印出列表，方便翻译直接定位
版本v1.4:
修正不支持文件夹内文件同步的BUG
'''
import fnmatch,os,struct,sys,time

#递归遍历一个目录下所有文件（含子目录），返回包含目录中所有文件的文件名的列表，对于空目录及空子目录不返回任何值。
#增加按模式匹配功能，默认返回所有文件(*)，也可以只返回匹配的文件列表
#参数1:目录名称
#参数2:匹配模式，默认*
def walk(dirname,pattern='*'):
    filelist=[]
    for root,dirs,files in os.walk(dirname):
        for filename in files:
            fullname=os.path.join(root,filename)
            filelist.append(fullname)
    return fnmatch.filter(filelist,pattern)

#将普通agemo格式的文本转化为列表，合并多行，去掉末尾换行符但不处理中间的换行符。并去掉可能有的句子结尾控制符
#参数1:一个包含文件所有行的列表
#参数2:模式，简单模式S(simple)只返回合并后的文本列表，复杂模式F(Full)返回一个包含[agemo标题，文本]的列表，默认简单模式
#参数3:句子结尾控制符，默认{END}，不一定所有文本都有，而且文本中有的话也会被替换掉
#参数4:换行符，默认\n
def agemo2list(lines,mode='S',lastctl='{END}',newline='\n'):
    textlist=[]
    llen=len(lines)
    for index,line in enumerate(lines):
        if ('#### ' in line) and (' ####' in line):
            j=1
            strs=''
            while True:
                if index+j>=llen:
                    break
                if ('#### ' in lines[index+j]) and (' ####' in lines[index+j]):
                    break
                else:
                    strs+=lines[index+j]
                    j+=1
            textlist.append([line.split(' ')[1],strs.rstrip(newline).replace(lastctl,'')])
    if mode=='S':
        return [y for x,y in textlist]
    if mode=='F':
        return textlist

#原文件夹
srceng='eng_text_source'
srcchs='chs_text_source'
#目标文件夹
deseng='eng_text_destination'
deschs='chs_text_destination'
#原始文件编码
srccodec='utf-16'
#目标文件编码
descodec=srccodec
#清空标志
ClearFlag=False
#未翻译文本报表
reportfile='未同步文本报告.txt'

stime=time.time()
#判断src_eng的文件名是否在src_chs中都存在
srcfilelist=walk(srceng)
srcfilelist2=walk(srcchs)

for index,s in enumerate(srcfilelist):
    if srcchs+os.sep+s.split(os.sep,1)[-1] in srcfilelist2:
        continue
    else:
        print('%s中文件(%s)在%s中不存在,程序退出.'%(srceng,s.split(os.sep,1)[-1],srcchs))
        sys.exit()
print('文件夹预校验通过,准备进行文本同步处理.')
#构建不判断的字符字典
dic={'\n':'','\t':'',' ':''}
smap=str.maketrans(dic)
#读取建立数据字典
srcreslist=[]
srcreslist2=[]
textdict={}
for filename in srcfilelist:
    sfile=open(filename,'r',encoding=srccodec)
    sfile2=open(srcchs+os.sep+filename.split(os.sep,1)[-1],'r',encoding=srccodec)
    #解析文本
    srcreslist=agemo2list(sfile.readlines())
    srcreslist2=agemo2list(sfile2.readlines())
    for no,text in enumerate(srcreslist):
        #把文本中不判断的字符去掉
        text=text.translate(smap)
        textdict[text]=srcreslist2[no]
    sfile.close()
    sfile2.close()
    #sys.exit()
#处理des中的文本，完成文本同步
rfile=open(reportfile,'w',encoding=srccodec)
desfilelist=walk(deseng)
for filename in desfilelist:
    dfile=open(filename,'r',encoding=descodec)
    #print(filename)
    #sys.exit()
    #建立目录
    os.makedirs(deschs+os.sep+os.path.dirname(filename.split(os.sep,1)[-1]),exist_ok=True)
    dfile2=open(deschs+os.sep+filename.split(os.sep,1)[-1],'w',encoding=descodec)
    desreslist=agemo2list(dfile.readlines(),mode='F')
    #sys.exit()
    for no,(title,text) in enumerate(desreslist):
        #把文本中不判断的字符去掉
        text=text.translate(smap)
        if text in textdict:
            desreslist[no][-1]=textdict[text]
        else:
            if ClearFlag:
                desreslist[no][-1]=''
            rfile.write('文件%s中有未同步的文本，标题“%s”，内容“%s”。\n'%(deschs+os.sep+filename.split(os.sep,1)[-1],title,text))
            
    #写文件
    for no,(title,text) in enumerate(desreslist):
        dfile2.write('#### %s ####\n'%(title))
        dfile2.write('%s\n'%(text))
        dfile2.write('\n')
    dfile.close()
    dfile2.close()
rfile.close()
print('处理完毕,本次共耗时%d秒.'%(int(time.time()-stime)))
os.system('pause')

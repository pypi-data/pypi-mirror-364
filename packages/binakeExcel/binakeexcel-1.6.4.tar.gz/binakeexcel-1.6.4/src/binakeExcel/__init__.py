import xlrd
import xlwt
import os
import xlsxwriter

alphabet = 'abcdefghijklmnopqrstuvwxyz'

# 获取字母列数
def num(a):
    num = 0
    for i in range(len(a)):
        temnum = alphabet.find(a[i].lower())
        num = (temnum + 1) * 26**(len(a) - i - 1) + num
    return num - 1

#获取表格所有行
def getall(path:'路径'):
    list_value = []
    workbook = xlrd.open_workbook(path)
    for name in workbook.sheet_names():
        sheet = workbook.sheet_by_name(name)
        for row in range(sheet.nrows):
            list_value.append(sheet.row_values(row))
    return list_value

#获取col列的所有值
def getcol(path:'路径' , col:'列数或列字母' ):
    list_value = []
    workbook = xlrd.open_workbook(path)
    for name in workbook.sheet_names():
        sheet = workbook.sheet_by_name(name)
        # 如果col是列名称，转换为列数字
        if isinstance(col, str):
            ncol = num(col)
        else:
            ncol = col
        list_value.append(sheet.col_values(ncol))

    return list_value

#获取row行的所有值
def getrow(path:'路径' , row:'数字' ):
    list_value = []
    workbook = xlrd.open_workbook(path)
    for name in workbook.sheet_names():
        try:
            sheet = workbook.sheet_by_name(name)
            # 如果col是列名称，转换为列数字
            if not isinstance(row, int):
                print("输入行的数字格式有误!")
                break
            list_value.append(sheet.row_values(row))
        except Exception as e:
            pass

    return list_value



#获取value所在的表格位置
def getps(path:str ,value:str ):
    if os.path.exists (path):

        list_ps = []
        
        workbook = xlrd.open_workbook (path)
        for name in workbook.sheet_names():        
            sheet = workbook.sheet_by_name(name)
            list_sheet = []
            list_sheet.append(name)
            for row in range(sheet.nrows):
                if value in sheet.row_values(row):
                    a = row
                    b = sheet.row_values(row).index(value)
                    list_sheet.append((a,b))
            list_ps.append(list_sheet)
            return list_ps
    else:
        print("文件路径错误")

#获取含有value的所有行
def getvl(path:str,value:str):
    if os.path.exists (path):
        list_value = []
        list_ps = []

        workbook = xlrd.open_workbook (path)
        for name in workbook.sheet_names():
            sheet = workbook.sheet_by_name(name)
            list_sheet = []
            list_sheet.append(name)
            for row in range(sheet.nrows):
                #模糊搜索
                for v_r in sheet.row_values(row):
                    if value in str(v_r):
                        a = row
                        b = sheet.row_values(row).index(v_r)
                        list_sheet.append((a,b))
                        break
            list_ps.append(list_sheet)
        #取数据
        for name in list_ps:
            sheet = workbook.sheet_by_name(name[0])
            for pos in name[1:]:
                list_value.append(sheet.row_values(pos[0]))
        return list_value
    else:
        print("文件路径错误")

#获取不含有value的所有行
def getnovl(path:str,value:str):
    if os.path.exists (path):
        list_value = []
        list_ps = []

        workbook = xlrd.open_workbook (path)
        for name in workbook.sheet_names():
            sheet = workbook.sheet_by_name(name)
            list_sheet = []
            list_sheet.append(name)
            for row in range(sheet.nrows):
                #模糊搜索
                biaozhi=0
                for v_r in sheet.row_values(row):
                    if value in str(v_r):
                        biaozhi=1
                        break
                if ( biaozhi == 0) :
                    a = row
                    b = sheet.row_values(row).index(v_r)
                    list_sheet.append((a,b))
            list_ps.append(list_sheet)
        #取数据
        for name in list_ps:
            sheet = workbook.sheet_by_name(name[0])
            for pos in name[1:]:
                list_value.append(sheet.row_values(pos[0]))
        return list_value
    else:
        print("文件路径错误")


#获取col列含有[value1,value2,....]的所有行
def get_col_lv(path:str, col:'列数或列字母', lv:list):
    if isinstance(col, str):
        ncol = num(col)
    list_value = []
    if os.path.exists (path) and type(ncol) == int and type(lv) == list:
        workbook = xlrd.open_workbook (path)
        for name in workbook.sheet_names():
            sheet = workbook.sheet_by_name(name)
            for row in range(sheet.nrows):
                for lsvalue in lv:
                    if lsvalue in sheet.row_values(row)[ncol]:                    
                        list_value.append(sheet.row_values(row))
    else:
        print("参数错误")
    return list_value

#获取col列不含有[value1,value2,....]的所有行
def get_col_nolv(path:str, col:'列数或列字母' , lv:list):
    if isinstance(col, str):
        ncol = num(col)
    list_value = []
    if os.path.exists (path) and type(ncol) == int and type(lv) == list:
        workbook = xlrd.open_workbook (path)
        for name in workbook.sheet_names():
            sheet = workbook.sheet_by_name(name)
            for row in range(sheet.nrows):
                for lsvalue in lv:
                    if lsvalue not in sheet.row_values(row)[ncol]:                    
                        list_value.append(sheet.row_values(row))
    else:
        print("参数错误")
    return list_value


# 写入表格xls格式
def writexls(path:str, list_value:list):
  if os.path.exists(path):
    print("文件已存在，不能重复创建")
  elif '.xlsx' in path:
    wookbook = xlsxwriter.Workbook(path)
    sheet1 = wookbook.add_worksheet('Sheet1')
    for i in range(len(list_value)):
      try:
        sheet1.write_row(i,0,list_value[i])
      except:
        pass
    wookbook.close()
    print("生成文件成功：", path)
  else:
    workbook = xlwt.Workbook ("utf-8")
    my_sheet = workbook.add_sheet("Sheet1")

    i = 0
    for row in list_value:
      j = 0
      for col in row:
        my_sheet.write(i,j,col)
        j += 1
      i += 1
    workbook.save (path)
    print("生成文件成功：",path)



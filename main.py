import requests

# 功能一
def search():
    while True:
        # 输入关键词
        keyword = input('请输入搜索关键词：')

        # 向搜索接口发起请求,获取数据
        params = {
            'keyWord': keyword,
            'maxNum': 10
        }
        #或许可以使用"http://www.cninfo.com.cn/new/information/topSearch/query"
        r = requests.post('which url', params=params)

        # 过滤A股
        data = []
        for i in r.json():
            if i['category'] == 'A股':
                data.append(i)

        # 判断是否无搜索结果，如果无搜索结果就重新循环
        if len(data) == 0:
            print('无搜索结果，请重新输入关键词!')
            continue

        # 将序号与股票绑定，方便后续取出股票信息
        result_dict = {}
        index = 1
        for row in data:
            result_dict[str(index)] = row

            # 顺便打印股票名称和对应序号
            print("【序号-{}】 名称 - {} 代码 - {} ".format(index, row['zwjc'], row['code']))
            index += 1

        print("序号：0 【我想重新输入关键词】\n")

        # 让用户选择序号
        while True:
            choice = input('请输入序号：')

            # 如果输入的序号存在，则返回结果
            if result_dict.get(choice) != None:
                return result_dict[choice]

            # 如果是0则中止这个循环
            elif choice == '0':
                break

            # 否则，打印提示
            else:
                print('输入了不存在的序号，请重新输入!')

# 功能二
def select(code, orgid):

    # 获取报告类型
    while True:
        # 初始化一个类型字典
        category_dict = {
            "1": "category_ndbg_szsh;",
            "2": "category_bndbg_szsh;",
            "3": "category_rcjy_szsh;"
        }

        # 让用户选择需要下载的报告类型
        numbers = input('请输入搜索类型序号：1、年报 2、半年报 3、日常经营：（输入序号，如：1）')
        
        # 判断用户选择的类型是否存在，如果存在，则返回类型
        if category_dict.get(numbers) != None:
            category = category_dict[numbers]
            break
        # 否则，打印提示
        else:
            print('未选择任何搜索类型，请重新输入\n')

    # 获取时间
    start = input('请输入搜索范围起始时间(例如 2021-01-01)：')
    end = input('请输入搜索范围结束时间(例如 2021-07-01)：')

    # 根据股票代码的头文字，判断股票交易所信息
    if str(code)[0] == '6':
        column = 'sse'
        plate = 'sh'
    else:
        column = 'szse'
        plate = 'sz'

    # 设置初始页码
    page_num = 1
    # 设置初始列表存储筛选结果
    pdf_list = []
    while True:
        # 设置报告筛选参数
        params = {
            'stock': '{},{}'.format(code, orgid),
            'tabName': 'fulltext',
            'pageSize': '30',
            'pageNum': str(page_num),
            'category': category,
            'seDate': '{}~{}'.format(start, end),
            'column': column,
            'plate': plate,
            'searchkey': '',
            'secid': '',
            'sortName': '',
            'sortType': '',
            'isHLtitle': ''
        }

        # 发起报告搜索请求
        r = requests.post('http://www.cninfo.com.cn/new/hisAnnouncement/query', params=params)
        r_json = r.json()

        # 判断是否搜索失败、或者无搜索结果，如果无结果则结束
        if r_json['announcements'] == None or len(r_json['announcements']) == 0:
            print('无搜索结果！')
            break

        # 遍历搜索结果
        for i in r_json['announcements']:
            pdf_list.append([i['announcementTitle'], i['adjunctUrl']])

        # 判断是否还有下一页数据，没有的话就结束循环
        if r_json['hasMore'] != True:
            break

        # 如果有的话，让页数加一，开始下一轮循环
        page_num += 1
        
    return pdf_list

# 功能三
def download(pdf_list):
    
    # 循环遍历筛选结果
    for item in pdf_list:

        # 拼接完整 url
        pdf_r = requests.get('http://static.cninfo.com.cn/' + item[1])

        # 拼接文件后缀
        file_path = item[0] + '.pdf'

        # 将报告内容写入文件，保存文件
        with open(file_path, 'wb') as f:
            f.write(pdf_r.content)
        
        # 打印下载提示
        print('已完成{}的下载'.format(item[0]))

# 功能整合
def main():
    # 搜索股票，获取股票id信息等
    info = search()

    # 输入各个参数，筛选报告
    pdf_list = select(info['code'], info['orgId'])

    # 下载报告
    download(pdf_list)

main()
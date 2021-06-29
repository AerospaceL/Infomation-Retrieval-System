from information.models import Animal, Currency
import requests
import base64
import pickle
import copy
import re
import jieba.posseg as pseg
import numpy as np


class API:

    def __init__(self):
        self.pkl_path = r"D:\MyDesktop\信息与知识获取\InfoServer\pkls"
        self.res_path = r"D:\MyDesktop\信息与知识获取\InfoServer\res\animals"

    def query_currency_info(self, query_):
        '''

        :param query_:
        :return:
        '''
        try:
            temp = Currency.objects.filter(real_code=query_["type"], real_denomination=query_["denomination"])

            result = []
            for each in temp:
                print(each)
                print(each.figure_id)
                temp_dict = dict()
                temp_dict["id"] = each.figure_id
                temp_dict["url"] = each.url
                temp_dict["real_type"] = each.real_type
                temp_dict["real_denomination"] = each.real_denomination
                temp_dict["real_code"] = each.real_code
                temp_dict["real_year"] = each.real_year
                temp_dict["view"] = each.view
                temp_dict["predict_type"] = each.predict_type
                temp_dict["predict_denomination"] = each.predict_denomination
                temp_dict["predict_code"] = each.predict_code
                temp_dict["predict_year"] = each.predict_year
                temp_dict["time"] = str(each.time)
                result.append(temp_dict)

            return True, result
        except:
            return False, []

    def extract_animal_info(self, id):
        try:
            temp = Animal.objects.get(file_id=id)

            temp_dict = dict()
            temp_dict["name"] = temp.name
            temp_dict["class"] = temp.claSS
            temp_dict["order"] = temp.order
            temp_dict["family"] = temp.family
            temp_dict["describe"] = temp.describe
            temp_dict["feature"] = temp.feature
            temp_dict["size"] = temp.size
            temp_dict["habitat"] = temp.habitat
            temp_dict["inner"] = temp.inner
            temp_dict["outer"] = temp.outer
            temp_dict["level"] = temp.level
            temp_dict["others"] = temp.others

            return True, temp_dict
        except:
            return False, dict()

    def query_animal_info(self, query_):
        '''

        :param query_:
        :return:
        '''
        method = query_['method']
        keyword = query_['keyword']  # 获得用布尔运算表达式得到的完整的句子

        result = []
        success = False

        if method == "index":
            success, result = self.__get_result_with_index(keyword)
        elif method == "vector1":
            success, result = self.__get_result_with_vector(keyword, 1)
        elif method == "vector2":
            success, result = self.__get_result_with_vector(keyword, 2)

        if success:
            for each in result:
                each['id'] = str(each['id']).split(".")[0]
                temp = Animal.objects.get(file_id=each['id'])
                each['title'] = temp.title
                each['url'] = temp.url
                each['time'] = str(temp.time)

        return success, result

    def __get_result_with_index(self, state):
        result = []
        success = False

        # 存储运算符和界限符
        operations = ['or', 'and', 'not', '(', ')', '#']

        # 运算符优先级表
        # 算符a和b之间的有限关系至多是下面的三种之一:
        # a < b a的优先权高于ｂ
        # a < b a的优先权低于ｂ
        # a = b a的优先权等于ｂ
        # 0表示不存在
        # 优先级 not > and > or
        priority = [['>', '<', '<', '<', '>', '>'],
                    ['>', '>', '<', '<', '>', '>'],
                    ['>', '>', '>', '<', '>', '>'],
                    ['<', '<', '<', '<', '=', '0'],
                    ['>', '>', '>', '0', '>', '>'],
                    ['<', '<', '<', '<', '0', '=']]

        # OPTR和OPND分别为运算符栈和运算数栈
        OPTR = []
        OPND = []
        OPNDD = []

        # 所有文章集合
        data_num = 100
        full_set = set(range(1, data_num + 1))

        # 测试输入字串
        input_str = '黑色 and ( 水中 or 黑龙江 ) or 20厘米'

        # 符号优先级比较
        def pri_cmp(op1, op2):
            i = operations.index(op1)
            j = operations.index(op2)
            return priority[i][j]
            pass

        # 计算
        def compute(op, set1, dlist1, set2=set(), dlist2=[]):
            result = set()
            dresult = []
            if op == 'or':
                result = set1 | set2
                dresult = dlist1 + dlist2
            elif op == 'and':
                result = set1 & set2
                dresult = dlist1 + dlist2
            elif op == 'not':
                result = full_set - set1
            return result, dresult
            pass

        # 读入字典; 参数:存储文件名;
        def load_dict(name):
            name = self.pkl_path + "\\" + name
            with open(name + '.pkl', 'rb') as f:
                return pickle.load(f)

        def index_query(index):
            # 正式版
            answer_set = set()
            this_answer_dict_list = []
            if index in word_dict.keys():
                this_answer_dict_list = word_dict[index]
                for i in this_answer_dict_list:
                    answer_set.add(int(i['id'][0:3]))
                    all_answer_dict_list.append(i)
                    pass

            return answer_set, this_answer_dict_list

            # 测试版
            # if index == 'a':
            #     return {1, 2, 5, 8}
            # elif index == 'b':
            #     return {2, 4, 5, 9}
            # elif index == 'c':
            #     return {7, 1, 5, 9}

            pass

        def evaluate_expression(exp_str):
            exp_str = exp_str + ' #'
            exp_elements = exp_str.split(' ')
            # print(exp_elements)
            OPTR.append('#')
            x = '#'  # x是出栈元素
            pos = 0  # pos是当前读取的exp_elems位置
            while pos < len(exp_elements) and (exp_elements[pos] != '#' or x != '#'):
                if exp_elements[pos] not in operations:
                    answer_set, this_answer_dict_list = index_query(exp_elements[pos])
                    OPND.append(answer_set)
                    OPNDD.append(this_answer_dict_list)
                    pos = pos + 1
                    pass
                else:
                    x = OPTR[-1]
                    prio = pri_cmp(x, exp_elements[pos])
                    if prio == '<':
                        OPTR.append(exp_elements[pos])
                        pos = pos + 1
                        x = OPTR[-1]
                        pass
                    elif prio == '=':
                        x = OPTR.pop()
                        pos = pos + 1
                        pass
                    elif prio == '>':
                        opr = OPTR.pop()
                        if opr == 'not':
                            set1 = OPND.pop()
                            dlist1 = OPNDD.pop()
                            rs, rl = compute(opr, set1, dlist1)
                            OPND.append(rs)
                            OPNDD.append(rl)
                            # print(opr, set1)
                            pass
                        else:
                            set1 = OPND.pop()
                            dlist1 = OPNDD.pop()
                            set2 = OPND.pop()
                            dlist2 = OPNDD.pop()
                            rs, rl = compute(opr, set1, dlist1, set2, dlist2)
                            OPND.append(rs)
                            OPNDD.append(rl)
                            # print(opr, set1, set2)
                            pass
                        pass
                    elif prio == '0':
                        return 'error code 100: illegal boolean expression', []
                    pass
                pass

            if type(OPND[-1]) != set:
                answer_set, this_answer_dict_list = index_query(OPND[-1])
                OPND[-1] = answer_set
                for every in this_answer_dict_list:
                    every['score'] = len(every['match'])
                    pass
                OPNDD[-1] = this_answer_dict_list

                return OPND.pop(), OPNDD.pop()

            else:
                answer_dict_list = []
                for i in OPNDD[-1]:
                    if int(i['id'][0:3]) in OPND[-1]:
                        answer_dict_list.append(i)
                if len(exp_elements) == 2:
                    for every in answer_dict_list:
                        every['score'] = len(every['match'])
                        pass
                    answer_dict_list = sorted(answer_dict_list, key=(lambda ax: ax['score']), reverse=True)
                else:
                    for every in answer_dict_list:
                        every['score'] = '-'
                        pass
                OPNDD[-1] = answer_dict_list

                return OPND.pop(), OPNDD.pop()
            pass

        word_dict = load_dict("location_table")  # 读入索引
        all_answer_dict_list = []

        result_set, result_dict_list = evaluate_expression(state)

        if type(result_set) == set:
            if len(result_set) > 0:
                success = True
                result = result_dict_list
        else:
            success = False
            result = result_set

        return success, result

    def __get_result_with_vector(self, keyword, version):
        '''
        空间向量方法搜索结果
        :return:
        '''
        if version == 1:
            print("vector")

            dist_list = [0 for i in range(0, 100)]
            frag_len = 4  # 保留关键字前后长度为4的字符串

            # 读入字典; 参数:存储文件名; 无返回值
            def load_obj(name):
                name = self.pkl_path + "\\" + name
                print(name)
                with open(name + '.pkl', 'rb') as f:
                    return pickle.load(f)

            # 对查询语句进行分词，获得查询语句的向量(字典)
            def get_query_dict(query):
                q_dict = dict()
                words = pseg.cut(query)
                for word, flag in words:
                    if flag[0] == 'n':
                        # 构建子词典
                        if word in q_dict.keys():
                            q_dict[word] += 1
                        else:
                            q_dict[word] = 1
                        # 总数加1
                        # query_len += 1
                return q_dict

            # 计算查询向量到每篇文章的距离
            def compute_dist(query_dict):
                for query_word in query_dict.keys():
                    for i in range(len(file_path_list)):
                        if query_word in sub_dict_list[i].keys():
                            dist_list[i] += sub_dict_list[i][query_word][1] * query_dict[query_word]
                for i in range(len(dist_list)):
                    dist_list[i] = dist_list[i] / sub_len_list[i]

            # 从检索文章中提取位置信息，构造Json包
            def make_packet(query_dict, answer_list):
                return_list = []
                item_dict = dict()
                for i in range(len(answer_list)):
                    filename = file_path_list[answer_list[i][0]]
                    item_dict['id'] = filename.split('\\')[-1]  # 去掉路径

                    item_dict['score'] = answer_list[i][1] * 1000 / 3  # 计算分数，还没有设置好
                    if item_dict['score'] > 99.9:
                        item_dict['score'] = 99.9

                    item_dict['match'] = []

                    filename = self.res_path + "\\" + filename.split("\\")[-1]
                    print(filename)

                    with open(filename, 'r', encoding='gbk') as f:
                        content = f.read()

                    # 提取出每个词在文中的位置信息
                    for word in query_dict.keys():
                        starts = [each.start() for each in re.finditer(word, content)]
                        # print(word, starts)

                        # 提取上下文信息
                        for s in starts:
                            if s + len(word) + frag_len > len(content):
                                end = len(content)
                            else:
                                end = s + len(word) + frag_len
                            if s < frag_len:
                                begin = 0
                            else:
                                begin = s - frag_len
                            item_dict['match'].append([content[begin:end], frag_len, frag_len + len(word) - 1])

                    return_list.append(copy.deepcopy(item_dict))
                return return_list

            def vector_query(query):
                # 每次查询初始化距离列表
                for i in range(len(dist_list)):
                    dist_list[i] = 0

                # 对查询语句进行分词
                query_dict = get_query_dict(query)
                print("分词结果:")
                print(query_dict)

                # 计算向量空间距离
                compute_dist(query_dict)

                # 获得答案列表
                answer_list = []
                for i in range(0, 100):
                    if dist_list[i] > 0:
                        answer_list.append([i, dist_list[i]])
                answer_list = sorted(answer_list, key=(lambda x: [x[1], x[0]]), reverse=True)
                print(answer_list)

                # 构造Json包
                re_list = make_packet(query_dict, answer_list)

                return re_list

            # 读入各种训练结果
            file_path_list = load_obj("file_path_list")
            sub_dict_list = load_obj("sub_dict_list")
            sub_len_list = load_obj("sub_len_list")

            query = keyword
            print(query)
            result = vector_query(query)
            success = False

            if len(result) > 0:
                success = True
            print(success)

            return success, result


        elif version == 2:
            # 读入字典; 参数:存储文件名; 无返回值
            def load_obj(name):
                name = self.pkl_path + "\\" + name
                print(name)
                with open(name + '.pkl', 'rb') as f:
                    return pickle.load(f)

            # 对查询语句进行分词，获得查询语句的向量(字典)
            def get_query_dict(query):
                q_dict = dict()
                words = pseg.cut(query)
                for word, flag in words:
                    if flag[0] == 'n':
                        # 构建子词典
                        if word in q_dict.keys():
                            q_dict[word] += 1
                        else:
                            q_dict[word] = 1
                        # 总数加1
                        # query_len += 1
                return q_dict

            def compute_dist(q_dict):
                query_vector = [0 for i in range(len(key_list))]
                for key in q_dict.keys():
                    index = key_list.index(key)
                    if index > -1:
                        query_vector[index] = q_dict[key]
                d_list = np.matmul(query_vector, A1)
                return d_list

            def make_packet(query_dict, answer_list):
                return_list = []
                item_dict = dict()
                for i in range(len(answer_list)):
                    filename = file_path_list[answer_list[i][0]]
                    item_dict['id'] = filename.split('\\')[-1]  # 去掉路径

                    item_dict['score'] = answer_list[i][1] * 1000 / 3  # 计算分数，还没有设置好
                    if item_dict['score'] > 99.9:
                        item_dict['score'] = 99.9

                    item_dict['match'] = []

                    filename = self.res_path + "\\" + filename.split("\\")[-1]
                    print(filename)

                    with open(filename, 'r', encoding='gbk') as f:
                        content = f.read()

                    # 提取出每个词在文中的位置信息
                    for word in query_dict.keys():
                        starts = [each.start() for each in re.finditer(word, content)]
                        # print(word, starts)

                        # 提取上下文信息
                        for s in starts:
                            if s + len(word) + frag_len > len(content):
                                end = len(content)
                            else:
                                end = s + len(word) + frag_len
                            if s < frag_len:
                                begin = 0
                            else:
                                begin = s - frag_len
                            item_dict['match'].append([content[begin:end], frag_len, frag_len + len(word) - 1])

                    if len(item_dict['match']) > 0:
                        return_list.append(copy.deepcopy(item_dict))
                return return_list

            frag_len = 4
            file_path_list = load_obj("file_path_list")
            key_list = load_obj("key_list")
            A1 = load_obj("A1")
            query = keyword
            query_dict = get_query_dict(query)
            dist_list = compute_dist(query_dict)
            answer_list = []
            for i in range(len(dist_list)):
                answer_list.append([i, dist_list[i]])

            answer_list = sorted(answer_list, key=(lambda x: [x[1], x[0]]), reverse=True)
            answer_list1 = answer_list[0:20]

            result = make_packet(query_dict, answer_list1)
            success = False
            if len(result) > 0:
                success = True
            print(success)

            return success, result


class InfoProvider(object):

    def __init__(self):

        # 获取access_token
        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=MXY6z8v1MoqjCrQdK5tmGGDI&client_secret=x9GZCi5KYLVWVM21WVbaiUEzdOcGB76i'
        # host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=jyjFQh5VEnOpwXbqToiIwpyL&client_secret=hql83rZB6f8I8xA6fPinLk6qg8bVGxFz'
        response = requests.get(host)
        if response:
            self.__access_token = str(response.json()['access_token'])

        self.__request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/currency"
        self.__header = {'content-type': 'application/x-www-form-urlencoded'}

    # 获得指定路径照片及其信息
    def getInfo(self, path):

        with open(path, 'rb') as f:

            img = base64.b64encode(f.read())
            params = {"image": img}

            request_url = self.__request_url + "?access_token=" + self.__access_token
            headers = self.__header
            response = requests.post(request_url, data=params, headers=headers)
            if response:
                info = response.json()
            else:
                return False, dict()

            try:
                info = info['result']

                result = dict()
                if info['hasdetail'] == 1:
                    result["type"] = info['currencyName']
                    result["denomination"] = info['currencyDenomination']
                    result["code"] = info['currencyCode']
                    result["year"] = info['year']
                else:
                    result["type"] = info['currencyName']
                    result["denomination"] = ""
                    result["code"] = ""
                    result["year"] = ""
            except Exception:
                return False, dict()
            else:
                return True, result

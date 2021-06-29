from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .models import Animal, Currency
from django.core.files import File

from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST
from django.http import HttpResponse
from django.core.files import File
import csv


import requests
import time
import datetime
import random
import json
import os
# Create your views here.
import sys
sys.path.append(r'D:\MyDesktop\信息与知识获取\InfoServer\information')
import apis

NORMAL = 0
DEFAULT = 10000
REQUEST_ERROR = 1
PARAMETER_ERROR = 2
DATABASE_ERROR = 3
FORM_ERROR = 4

currency_extract_info = dict()

def error(message="", type=DEFAULT):
    '''
    出现异常时，返回的报文
    '''
    result = dict()
    result['code'] = type

    if type == DEFAULT:
        result['message'] = message
    elif type == REQUEST_ERROR:
        result['message'] = "请求方式错误"
    elif type == PARAMETER_ERROR:
        result['message'] = "请求参数错误"
    elif type == DATABASE_ERROR:
        result['message'] = "数据库错误"
    elif type == FORM_ERROR:
        result['message'] = "包格式错误"

    return JsonResponse(result)

def randomstr(prefix=""):
    return str(prefix) + str(int(time.time()))+str(random.randint(10000, 99999))


def search(request):
    # 请求方式检验
    if request.method != 'POST':
        return error(type=REQUEST_ERROR)

    # 参数获取
    post_body = request.body
    #print(post_body)
    try:
        json_result = json.loads(post_body)
        #print(json_result)
    except json.decoder.JSONDecodeError:
        return error(type=FORM_ERROR)

    try:
        class_ = json_result['classes']
        query_ = json_result['query']
    except KeyError:
        return error(type=PARAMETER_ERROR)

    # 数据操作
    query_api = apis.API()
    if class_ == "animal":
        success, answer = query_api.query_animal_info(query_)
    elif class_ == "currency":
        success, answer = query_api.query_currency_info(query_)
    else:
        return error(type=PARAMETER_ERROR)

    if not success:
        return error("信息不存在，请检查关键词是否合法")

    # 构造回复报文
    result = dict()
    result['code'] = NORMAL
    result['message'] = "查询成功"
    result['answer'] = answer
    return JsonResponse(result)


def extract(request):
    # 请求方式检验
    if request.method != 'POST':
        return error(type=REQUEST_ERROR)

    # 参数获取
    post_body = request.body
    print(post_body)
    try:
        json_result = json.loads(post_body)
        print(json_result)
    except json.decoder.JSONDecodeError:
        return error(type=FORM_ERROR)

    try:
        class_ = json_result['classes']
        id_ = json_result['id']
    except KeyError:
        return error(type=PARAMETER_ERROR)

    # 数据操作
    query_api = apis.API()
    if class_ == "animal":
        print("AAAAAAAAAAAA")
        success, answer = query_api.extract_animal_info(id_)
    elif class_ == "currency":
        try:
            answer = currency_extract_info[id_]
            success = True
        except Exception:
            success = False
    else:
        return error(type=PARAMETER_ERROR)

    if not success:
        return error("信息不存在")

    # 构造回复报文
    result = dict()
    result['code'] = NORMAL
    result['message'] = "抽取成功"
    result['answer'] = answer
    return JsonResponse(result)




def upload(request):
    file = request.FILES.get("file", None)
    if not file:
        return error(type=FORM_ERROR)
    print(str(file))

    fid = randomstr("f")
    file_name = "upload\\"+ fid + "." + str(file).split(".")[-1]


    with open(file_name, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    # 这里需要把刚上传的照片的信息送到远端服务器，然后直接把信息存在服务器
    info_provider = apis.InfoProvider()
    success, answer = info_provider.getInfo(file_name)
    print(answer)

    if not success:
        return error("图片不可识别， 请确认图片中是否包含钱币")
    else:
        currency_extract_info[fid] = answer

    # 构造回复报文
    result = dict()
    result['code'] = NORMAL
    result['message'] = "上传成功"
    result['id'] = fid

    return JsonResponse(result)


def download(request, path):
    #  请求方式/身份信息检验
    if request.method != 'GET':
        return error(type=REQUEST_ERROR)

    print(path)
    file_pathname = os.path.join(r'D:\MyDesktop\信息与知识获取\InfoServer\res', path)
    print(file_pathname)

    try:
        with open(file_pathname, 'rb') as f:
            file = File(f)

            response = HttpResponse(file.chunks(),
                                    content_type='APPLICATION/OCTET-STREAM')
            response['Content-Disposition'] = 'attachment; filename=' + path
            response['Content-Length'] = os.path.getsize(file_pathname)
    except Exception:

        result = dict()
        result['code'] = DEFAULT
        result['message'] = "服务器忙，请稍后重试"
        response = JsonResponse(result)

    return response

def submit(request):
    currency_list = []
    animal_list = []

    try:

        # with open(r'D:\MyDesktop\信息与知识获取\InfoServer\data\all_currency_info.csv') as f:
        #     f_csv = csv.reader(f)
        #     headers = next(f_csv)
        #
        #     for row in f_csv:
        #         print(row)
        #
        #         [figure_id, url, real_type, real_denomination, real_code, real_year, view,
        #          predict_type, predict_denomination, predict_code, predict_year] = row
        #
        #         currency_list.append(Currency(figure_id=figure_id, url=url, real_type=real_type,
        #                                       real_denomination=real_denomination, real_code=real_code,
        #                                       real_year=real_year, view=view, predict_type=predict_type,
        #                                       predict_denomination=predict_denomination, predict_code=predict_code,
        #                                       predict_year=predict_year, time=timezone.now()))
        # Currency.objects.bulk_create(currency_list)


        with open(r'D:\MyDesktop\信息与知识获取\InfoServer\data\all_animal_info.csv') as f:
            f_csv = csv.reader(f)
            headers = next(f_csv)

            for row in f_csv:
                print(row)

                [file_id, url, title, name, claSS, order, family, describe, feature,
                 size, habitat, inner, outer, level, others] = row

                animal_list.append(Animal(file_id=file_id, url=url, title=title, name=name, claSS=claSS, order=order,
                                          family=family, describe=describe, feature=feature, size=size, habitat=habitat,
                                          inner=inner, outer=outer, level=level, others=others, time=timezone.now()))
        Animal.objects.bulk_create(animal_list)

    except Exception:
        return error("导入失败！")
    else:

        result = dict()
        result['code'] = DEFAULT
        result['message'] = "导入成功！"
        response = JsonResponse(result)
        return response

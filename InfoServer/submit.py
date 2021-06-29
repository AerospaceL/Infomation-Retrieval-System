
import csv
'''
django数据库导入脚本
'''

'''
for i in range(1000):
    models.Book.objects.create(title=f'第{i}本书')
'''

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "infoServer.settings")

'''
Django 版本大于等于1.7的时候，需要加上下面两句
import django
django.setup()
否则会抛出错误 django.core.exceptions.AppRegistryNotReady: Models aren't loaded yet.
'''

import django

if django.VERSION >= (1, 7):  # 自动判断版本
    django.setup()

from information.models import Currency
def main():
    currency_list = []

    with open('currency_result.csv') as f:
        f_csv = csv.reader(f)
        headers = next(f_csv)

        for row in f_csv:
            print(row)

            [figure_id, url, real_type, real_denomination, real_code, real_year, view,
             predict_type, predict_denomination, predict_code, predict_year] = row

            currency_list.append(Currency(figure_id=figure_id, url=url, real_type=real_type,
                                          real_denomination=real_denomination, real_code=real_code,
                                          real_year=real_year, view=view, predict_type=predict_type,
                                          predict_denomination=predict_denomination, predict_code=predict_code,
                                          predict_year=predict_year))

    # bulk_create
    #Currency.objects.bulk_create(currency_list)
if __name__ == "__main__":
    main()
    print('Done!')
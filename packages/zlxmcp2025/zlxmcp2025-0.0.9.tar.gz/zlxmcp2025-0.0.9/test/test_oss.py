import os
import io
import unittest
import pandas as pd
from zlxmcp.utils.oss import *
import dotenv

dotenv.load_dotenv()


class TestOss(unittest.TestCase):
    """"""
    def setUp(self):
        """"""
        oss_key = os.getenv("OSS_KEY")
        self.oss = OSS(
            access_key_id=oss_key.split("-")[0],
            access_key_secret=oss_key.split("-")[1],
            bucket_name="-".join(oss_key.split("-")[2:]),
        )


    def test_put_file(self):
        """"""
        file_path = r"C:\Users\chensy\zlxmcp\charts\各省份企业数量分布.html"
        with open(file_path, 'rb') as f:
            data = f.read()
        print(type(data))
        path = "zlxmcp/charts/各省份企业数量分布.html"
        # path = "zlxmcp/data/碳排放量汇总.xlsx"
        msg, _ = self.oss.put_file(object_name=path, data=data)
        print(msg)

    def test_put_file2(self):
        """"""
        file_path = r"C:\Users\chensy\zlxmcp\data\碳排放量汇总.xlsx"
        with open(file_path, 'rb') as f:
            data = f.read()
        path = "zlxmcp/data/碳排放量汇总.xlsx"
        msg, _ = self.oss.put_file(object_name=path, data=data)

        print(msg)

    def test_load(self):
        """"""
        path = "zlxmcp/data/碳排放量汇总.xlsx"
        msg, b_data = self.oss.download_file(path)

        # 将二进制数据转为DataFrame
        try:
            df = pd.read_excel(io.BytesIO(b_data))  # 自动识别xls/xlsx
            print("Excel文件解析成功！")
            print(df.head())  # 打印前5行数据
        except Exception as e:
            print(f"解析失败，错误: {e}")

    def test_list_files(self):
        """"""
        # msg, data = self.oss.list_objects(prefix="zlxmcp/", n=30)
        # msg, data = self.oss.list_objects(prefix="zlxmcp/data/", n=30)
        msg, data = self.oss.list_objects(prefix="zlxmcp/charts/", n=30)
        print(msg)
        print(data)

    def test_obj_exist(self):
        """"""
        # print(self.oss.object_exist(object_name="zlxmcp/charts/test.html"))
        # print(self.oss.object_exist(object_name="zlxmcp/char/test.html"))
        print(self.oss.object_exist(object_name="zlxmcp/charts/各省份企业数量分布.html"))


    def test_list_obj(self):
        """"""
        print(self.oss.sign_url(key="zlxmcp/charts/各省份企业数量分布.html"))
        # print()

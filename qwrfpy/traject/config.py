# 標準ライブラリ
import datetime

# 外部ライブラリ
import numpy as np

# config===================================================
# 基本的にこの部分のみを変更したらよい
s_tmp = datetime.datetime(2017,7,4,21,00)
e_tmp = datetime.datetime(2017,7,5, 3,00)
# path = f"./wrfout_d01_2017-07-04_06:00:00"
path = f"/home1/nakamura_kento/WRF/work/TR_Nkyushu_20170705/WDM7/wrfout_d03_2017-07-04_12:00:00"
output = f"test03.csv"
s_lat = np.arange(32.25, 33, 0.05)
s_lon = np.arange(129.25, 129.5, 0.05)
s_height = 500 #(m) 
ana_varis = {"QVAPOR":None}
time_delta = 60 # second(秒単位)
backward = False #後方流跡線解析にする場合はTrue
# 後方流跡線解析の場合でもs_tmp<e_tmpで設定する
core_num = 25 #実行コア数
# ==========================================================
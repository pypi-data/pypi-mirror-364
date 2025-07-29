import pandas as pd
pd.options.display.float_format = '{:.2f}'.format
def convert_to_int(x):
    """将客户ID转为整数（去除小数点）"""
    return int(float(x)) if pd.notnull(x) else x

def format_price(x):
    """将产品单价格式化为两位小数"""
    return round(float(x), 2) if pd.notnull(x) else x

def get_order(start_time="",end_time=""):
    df=pd.read_excel("https://v.hbgro.com/salesorderdata.xls",converters={
                        '订单号':str,
                        '客户ID': convert_to_int,
                        '城市ID': convert_to_int,
                        '产品ID': convert_to_int,
                        '产品销售数量':convert_to_int,
                        '产品单价': format_price,
                        '产品单件成本': format_price,
                   })
    # df.style.format({
    #     '产品单价': '{:.2f}',  # 2位小数
    #     '产品单件成本': '{:.2f}',  # 3位小数
    # })
    if start_time and end_time:
        df=df[(df["订单日期"].dt.strftime('%Y-%m-%d')>=start_time) & (df['订单日期'].dt.strftime('%Y-%m-%d')<=end_time)]
    return df

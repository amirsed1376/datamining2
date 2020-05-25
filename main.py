import pandas as pd
from pandas.core.frame import DataFrame
import numpy as np
import sqlite3


class SqlManager:
    def __init__(self, file):
        self.conn = sqlite3.connect(file)
        self.crs = self.conn.cursor()



def preprocess(df:DataFrame):
    sql_manager = SqlManager("information.sqlite")
    df.replace('?', np.NaN, inplace=True)
    df2 = missing_data(df)
    df2.to_excel(excel_writer="missing_information.xlsx" , sheet_name="sheet1",engine='xlsxwriter')
    main_df = df.dropna()
    main_df.to_sql(name="information", con=sql_manager.conn, index=False,if_exists='replace')
    main_df.describe().to_sql(name="describe" , con=sql_manager.conn,if_exists='replace')
    with open("dtypes.txt","w") as file :
        file.write(str(main_df.dtypes))
    return df


def missing_data(data):
    total = data.isnull().sum()
    percent = (data.isnull().sum() / data.isnull().count() * 100)
    tt = pd.concat([total, percent], axis=1, keys=['Total', 'Percent'])
    types = []
    for col in data.columns:
        dtype = str(data[col].dtype)
        types.append(dtype)
    tt['Types'] = types
    return (np.transpose(tt))




if __name__ == '__main__':
    csv_file="fout.csv"
    df = pd.read_csv(csv_file,
                     names=['age', 'workclass', 'fnlwgt', 'education', 'education_num', 'marital_status', 'post',
                            'relationship', 'nation', 'gender', 'capital_gain', 'capital_loss', 'hours_per_week',
                            'country', 'wealth'],skipinitialspace=True)
    df = preprocess(df=df)

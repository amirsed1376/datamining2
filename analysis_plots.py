import pandas as pd
from pandas.core.frame import DataFrame
from SqlManager import SqlManager
from classification import label_encode, combine_features_tuples
import matplotlib.pyplot as plt
import seaborn as sn


if __name__ == '__main__':

    columns_name = ['age', 'workclass', 'education_num', 'marital_status', 'post',
                    'relationship', 'nation', 'gender', 'capital', 'hours_per_week',
                    'country']

    sql_manager = SqlManager("information.sqlite")
    try:
        sql_manager.crs.execute("delete from encoding_guide")
        sql_manager.conn.commit()
    except:
        pass
    label_encode_features = []
    columns_name = ['age', 'workclass', 'education_num', 'marital_status', 'post',
                    'relationship', 'nation', 'gender', 'capital', 'hours_per_week',
                    'country', 'wealth']
    for column in columns_name:
        encode_labels = label_encode(column)
        label_encode_features.append(encode_labels)

    data = combine_features_tuples(label_encode_features)
    df = DataFrame(data, columns=columns_name)

    df.cumsum().plot()
    plt.savefig("outs\\cumsum.png")
    plt.close()

    df.diff().hist()
    plt.savefig("outs\\diff_hist.png")
    plt.close()

    for col in columns_name:
        df[col].plot.box()
        plt.savefig("outs\\boxes\\{}.png".format(col))
        plt.close()

    for col in columns_name:
        result = sql_manager.crs.execute(("select distinct {},count({}) from information group by {}".format(col,col,col))).fetchall()
        counts = [x[1] for x in result]
        attr = [x[0] for x in result]
        fig1, ax1 = plt.subplots()
        ax1.pie(counts, labels=attr, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        plt.savefig("outs\\pie_plots\\{}.png".format(col))
        plt.close()

    corrMatrix = df.corr()

    sn.heatmap(corrMatrix, annot=True)
    plt.show()
    # plt.savefig("outs\\corr_table.pdf",dpi=400)
    plt.close()
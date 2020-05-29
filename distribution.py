import matplotlib.pyplot as plt
import matplotlib
from preprocess import SqlManager


def make_plots():
    matplotlib.use('PS')
    columns = ['age', 'workclass', 'education_num', 'marital_status', 'post',
               'relationship', 'nation', 'gender', 'capital', 'hours_per_week',
               'country']

    sql_manager = SqlManager("information.sqlite")
    for col in columns:

        result = sql_manager.crs.execute(
            "select {},{},count({}) from information group by {},{} ".format(col, "wealth",col, col,
                                                                           "wealth")).fetchall()
        counts = [x[2] for x in result]
        minimum = min(counts)
        maximum = max(counts)
        print("_________________\n",col)
        print(result)
        plt.rcParams["figure.figsize"] = (20, 3)
        for row in result:
            dark_number = 1-((row[2]-minimum)/(maximum-minimum))
            plt.scatter(row[0], row[1],color=(dark_number,0,0))
        plt.xticks(rotation=60)
        plt.savefig("distribution_plots\\"+col+".png",bbox_inches='tight')
        plt.close()
        # plt.show()

if __name__ == '__main__':
    make_plots()

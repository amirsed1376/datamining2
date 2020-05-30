from preprocess import SqlManager
import numpy as np
import matplotlib.pyplot as plt


def get_information(column):
    """this function get information of column and wealth from database and return up_count and low_count and labels"""
    sql_manager = SqlManager("information.sqlite")
    column_value = sql_manager.crs.execute(
        'select DISTINCT {} from information ORDER BY {}'.format(column, column)).fetchall()
    low_column_count = sql_manager.crs. \
        execute('select {}, count({}) from information where wealth="lowerCase" GROUP by {} '
                .format(column, column, column)).fetchall()
    up_column_count = sql_manager.crs. \
        execute('select {}, count({}) from information where wealth="upperCase" GROUP by {} '
                .format(column, column, column)).fetchall()

    labels = [x[0] for x in column_value]

    low_column_label = [x[0] for x in low_column_count]
    up_column_label = [x[0] for x in up_column_count]
    low_column_count = list(low_column_count)
    up_column_count = list(up_column_count)
    for i in low_column_label:
        if i not in up_column_label:
            up_column_count.append((i, 0))
    for i in up_column_label:
        if i not in low_column_label:
            low_column_count.append((i, 0))


    up_column_count.sort(key=lambda x: x[0])
    low_column_count.sort(key=lambda x: x[0])

    print(up_column_count)
    print(low_column_count)


    up_count = [item[1] for item in up_column_count]
    low_count = [item[1] for item in low_column_count]
    return up_count, low_count, labels


def grouping(up_count, low_count, labels, group_num):
    """grouping lists and return information of each group"""
    # print(up_count)
    # print(low_count)
    # print(labels)
    minimum = min(labels)
    maximum = max(labels)
    Range = maximum - minimum
    range_list = []
    for i in range(group_num):
        range_list.append((int(minimum + i * Range / group_num), int(minimum + (i + 1) * Range / group_num)))
    # print(range_list)
    labels_dict = dict()

    for r_index, r in enumerate(range_list):
        if r_index == group_num - 1:
            range_str = "{}<=x<={}".format(r[0], r[1])

        else:
            range_str = "{}<=x<{}".format(r[0], r[1])
        labels_dict[range_str] = ([], [])
        for index, label in enumerate(labels):
            if label in range(r[0], r[1]) or (r_index == group_num - 1 and label == r[1]):
                labels_dict[range_str][0].append(up_count[index])
                labels_dict[range_str][1].append(low_count[index])

    new_labels = [str(key) for key in labels_dict]
    new_up_count = [sum(labels_dict[key][0]) for key in labels_dict]
    new_low_count = [sum(labels_dict[key][1]) for key in labels_dict]
    return new_up_count, new_low_count, new_labels

def autolabel(rects, ax):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

def make_plot(up_count, low_count, labels,column,address, histogram_group=0 ):
    """
        input : a column name
        outputs:
                    save plots depend on low and high income
                    and number of them
        Description:
                    x axi is for all distinct values of column
                    and y axi is number of value who have low or high income


        """

    if histogram_group != 0:
        up_count, low_count, labels = grouping(up_count, low_count, labels, histogram_group)
        print("ok")

    x = np.arange(len(labels)) * 100  # the label locations
    width = 30  # the width of the bars
    try:
        fig, ax = plt.subplots(figsize=(200, 100))
        plt.xticks(rotation=50, fontsize=60)
        # plt.xticks(rotation=50)
        plt.yticks(fontsize=60)
        # plt.yticks()
        rects1 = ax.bar(x - width / 2, low_count, width, label='Low Income')
        rects2 = ax.bar(x + width / 2, up_count, width, label='High Income')
        ax.set_ylabel('Counts')
        ax.set_title('Scores by income and {}'.format(column))
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        # plt.show()
        plt.savefig(address)
        plt.close()
        fig.tight_layout()
        print(address, "  finished")
    except Exception as e:
        print("EXCEPT", e)





def run_plots():
    names = ['age', 'workclass', 'education_num', 'marital_status', 'post',
             'relationship', 'nation', 'gender', 'capital', 'hours_per_week',
             'country']
    for col in names:
        histogram_group = 0
        if col == "capital":
            histogram_group = 40
        up_count, low_count, labels = get_information(col)
        make_plot(up_count, low_count, labels,col,'plots\\' + col + '__ income', histogram_group=histogram_group)
        sum_up_count=sum(up_count)
        sum_low_count=sum(low_count)
        up_count_percent=[x/sum_up_count for x in up_count]
        low_count_percent=[x/sum_low_count for x in low_count]
        make_plot(up_count_percent, low_count_percent, labels,col,'plots_percent\\' + col + '__ income', histogram_group=histogram_group)


if __name__ == '__main__':
    run_plots()

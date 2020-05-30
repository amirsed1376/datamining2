from preprocess import SqlManager
import numpy as np
import matplotlib.pyplot as plt


def get_information(column):
    """this function get information of column and wealth from database and return up_count and low_count and labels"""
    sql_manager = SqlManager("information.sqlite")
    column_value = sql_manager.crs.execute(
        'select DISTINCT {} from information ORDER BY {}'.format(column, column)).fetchall()
    low_column_count = sql_manager.crs. \
        execute('select {}, count({}) from information  GROUP by {} having wealth="lowerCase"'
                .format(column, column, column)).fetchall()
    up_column_count = sql_manager.crs. \
        execute('select {}, count({}) from information  GROUP by {} having wealth="upperCase"'
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
    up_count = [item[1] for item in up_column_count]
    low_count = [item[1] for item in low_column_count]

    return up_count, low_count, labels


def grouping(up_count, low_count, labels, group_num):
    """grouping lists and return information of each group"""
    print(up_count)
    print(low_count)
    print(labels)
    minimum=min(labels)
    maximum=max(labels)
    Range=maximum-minimum
    range_list=[]
    for i in range(group_num):
        range_list.append((int(minimum+i*Range/group_num), int(minimum+(i+1)*Range/group_num)))
    print(range_list)
    labels_dict =dict()

    for r_index , r in enumerate(range_list):
        if r_index == group_num-1:
            range_str="{}<=x<={}".format(r[0],r[1])

        else:
            range_str="{}<=x<{}".format(r[0], r[1])
        labels_dict[range_str] = ([],[])
        for index , label in enumerate(labels):
            if label in range(r[0],r[1]) or (r_index==group_num-1 and label==r[1]):
                labels_dict[range_str][0].append(up_count[index])
                labels_dict[range_str][1].append(low_count[index])

    new_labels=[str(key) for key in labels_dict]
    new_up_count=[sum(labels_dict[key][0]) for key in labels_dict]
    new_low_count=[sum(labels_dict[key][1]) for key in labels_dict]
    return new_up_count, new_low_count, new_labels


def make_plot(column, histogram_group=0):
    """
        input : a column name
        outputs:
                    save plots depend on low and high income
                    and number of them
        Description:
                    x axi is for all distinct values of column
                    and y axi is number of value who have low or high income


        """

    up_count, low_count, labels = get_information(column)

    if histogram_group != 0:
        up_count, low_count, labels = grouping(up_count, low_count, labels, histogram_group)
        print("ok")
    print(up_count)
    print(low_count)
    print(labels)

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
        plt.savefig('plots\\' + column + '__ income')
        plt.close()
        fig.tight_layout()
        print(column, " plot finished")
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
        make_plot(column=col, histogram_group=histogram_group)


if __name__ == '__main__':
    run_plots()

from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn import tree
import graphviz
from pandas.core.frame import DataFrame
import os
from SqlManager import SqlManager
from sklearn import preprocessing


def cal_accuracy(y_test, y_pred):
    """
    calculate accuracy
    :param y_test: test label
    :param y_pred: predict label
    output:
            save accuracy_decision_tree_report.txt file has report of accuracy
    """
    confusionMatrix = confusion_matrix(y_test, y_pred)
    accuracy = accuracy_score(y_test, y_pred) * 100
    print("Confusion Matrix: ",
          confusionMatrix)

    print("Accuracy : ", accuracy)

    report = classification_report(y_test, y_pred)
    print("Report : ", report)
    accuracy_file = open("outs\\accuracy_decision_tree_report.txt", "w")
    accuracy_file.write(
        "Confusion Matrix:\n{}\n\nAccuracy : \n{}\n\nReport : \n{}".format(str(confusionMatrix), str(accuracy),
                                                                           str(report)))
    accuracy_file.close()


def combine_features_tuples(label_encode_features):
    features = tuple(zip(*label_encode_features))
    return features


def label_encode(column):
    """
    become nominal value to number value
    :param column: each column
    :return: label encoded
    """
    sql_manager = SqlManager("information.sqlite")
    column_value = sql_manager.crs.execute(
        'select  {} from information '.format(column)).fetchall()

    labels = [x[0] for x in list(column_value)]
    if type(labels[0]) == int:
        label_encoded = labels
    else:
        le = preprocessing.LabelEncoder()
        label_encoded = le.fit_transform(labels)
    col_list = []
    for i in range(len(label_encoded)):
        col_list.append(column)
    df = DataFrame({"Lable": labels, "encode": label_encoded, "column": column})
    df = df.drop_duplicates()
    df.to_sql(name="encoding_guide", con=sql_manager.conn, if_exists="append")
    return label_encoded


def decision_tree(X_train, y_train, column_names):
    """
    make decision tree and show tree and return tree
    """
    clf_gini = DecisionTreeClassifier(criterion="gini",
                                      random_state=100, max_depth=10, min_samples_leaf=5)
    clf_gini.fit(X_train, y_train)
    try:
        dot_data = tree.export_graphviz(clf_gini, out_file=None, feature_names=column_names, class_names=["LOW", "UP"])
        graph = graphviz.Source(dot_data)
        graph.render("image", view=True)
    except:
        pass
    return clf_gini


def run_decision_tree():
    """main function of this file """
    sql_manager = SqlManager("information.sqlite")
    try:
        sql_manager.crs.execute("delete from encoding_guide")
        sql_manager.conn.commit()
    except:
        pass
    label_encode_features = []
    columns_name = ['age', 'workclass', 'education_num', 'marital_status', 'post',
                    'relationship', 'nation', 'gender', 'capital', 'hours_per_week',
                    'country']
    for column in columns_name:
        encode_labels = label_encode(column)
        label_encode_features.append(encode_labels)

    data = combine_features_tuples(label_encode_features)
    target = label_encode('wealth')
    X_train, X_test, y_train, y_test = train_test_split(data, target, test_size=0.3,
                                                        random_state=1)

    clf = decision_tree(X_train, y_train, columns_name)

    y_pred_gini = clf.predict(X_test)
    cal_accuracy(y_test, y_pred_gini)

    print("Results Using Entropy:")


if __name__ == "__main__":
    os.environ["PATH"] += os.pathsep + 'C:\\Users\\user\\Desktop\\graphviz-2.38\\release\\bin'
    run_decision_tree()

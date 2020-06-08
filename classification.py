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
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.naive_bayes import BernoulliNB
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt



def cal_accuracy(y_test, y_pred, report_file):
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
    accuracy_file = open(report_file, "w")
    accuracy_file.write(
        "Confusion Matrix:\n{}\n\nAccuracy : \n{}\n\nReport : \n{}".format(str(confusionMatrix), str(accuracy),
                                                                           str(report)))
    accuracy_file.close()
    return accuracy


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


def gaussian(X_train, y_train):
    gnb = GaussianNB()
    gnb.fit(X_train, y_train)
    return gnb


def svc(X_train, y_train):
    svclassifier = SVC(gamma='auto')
    svclassifier.fit(X_train, y_train)
    return svclassifier


def bernoulli(X_train, y_train):
    clf = BernoulliNB()
    clf.fit(X_train, y_train)
    return clf


def random_forest(X_train, y_train):
    clf = RandomForestClassifier(max_depth=2, random_state=0)
    clf.fit(X_train, y_train)
    return clf


def predict_save(x_test, y_test, y_predict, classification_type, conn):
    # print(type(x_test))
    columns_names = ['age', 'workclass', 'education_num', 'marital_status', 'post',
                     'relationship', 'nation', 'gender', 'capital', 'hours_per_week',
                     'country']
    save_list = x_test.copy()
    df = DataFrame(save_list, columns=columns_names)
    df["y"] = y_test
    df["y_predict"] = y_predict
    df.to_sql(name=classification_type + "_predict", con=conn, if_exists="replace")


def run_classification():
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
    accuracy_list = [0]

    # decision tree algorithm
    clf = decision_tree(X_train, y_train, columns_name)
    y_pred_gini = clf.predict(X_test)
    accuracy = cal_accuracy(y_test, y_pred_gini, "outs\\accuracy_decision_tree_report.txt")
    accuracy_list.append(accuracy)
    predict_save(x_test=X_test, y_test=y_test, y_predict=y_pred_gini, classification_type="decision_tree",
                 conn=sql_manager.conn)
    print("decision_tree finish")

    # gaussian algorithm
    gnb = gaussian(X_train, y_train)
    y_pred_gaussian = gnb.predict(X_test)
    accuracy = cal_accuracy(y_test, y_pred_gaussian, "outs\\accuracy_gaussian_report.txt")
    accuracy_list.append(accuracy)
    predict_save(X_test, y_test, y_pred_gaussian, "gaussian", sql_manager.conn)
    print("gaussian finish")

    # bernoulli algorithm
    clf = bernoulli(X_train, y_train)
    y_pred_bernoulli = clf.predict(X_test)
    accuracy = cal_accuracy(y_test, y_pred_bernoulli, report_file="outs\\accuracy_Bernoulli_report.txt")
    accuracy_list.append(accuracy)
    predict_save(X_test, y_test, y_pred_bernoulli, "Bernoulli", sql_manager.conn)
    print("bernoulli finish")

    # svc algorithm
    svclassifier = svc(X_train, y_train)
    y_pred_SVC = svclassifier.predict(X_test)
    accuracy = cal_accuracy(y_test, y_pred_SVC, report_file="outs\\accuracy_SVC_report.txt")
    accuracy_list.append(accuracy)
    predict_save(X_test, y_test, y_pred_SVC, "SVC", sql_manager.conn)
    print("SVC finish")

    # random_forest algorithm
    clf = random_forest(X_train, y_train)
    y_pred_random_forest = clf.predict(X_test)
    accuracy = cal_accuracy(y_test, y_pred_random_forest, report_file="outs\\accuracy_random_forest_report.txt")
    accuracy_list.append(accuracy)
    predict_save(X_test, y_test, y_pred_random_forest, "random_forest", sql_manager.conn)
    print("random_forest finish")

    # make accuracy plot and table
    classifications=["","decision_tree","gaussian","Bernoulli","SVC","random_forest"]
    accuracy_df = DataFrame({"classification_name":classifications , "accuracy":accuracy_list})
    accuracy_df.to_sql(name="accuracies",con=sql_manager.conn,if_exists="replace")
    plt.bar(classifications,accuracy_list)
    plt.savefig("outs\\accuracy_plot.png")

if __name__ == "__main__":
    os.environ["PATH"] += os.pathsep + 'C:\\Users\\user\\Desktop\\graphviz-2.38\\release\\bin'
    run_classification()

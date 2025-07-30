import inspect

# ===================== 📦 ML and Visualization Programs ===================== #

def program1():
    from sklearn.linear_model import LinearRegression
    import numpy as np
    import matplotlib.pyplot as plt

    X = np.array([[1], [2], [3], [4], [5]])
    y = np.array([1, 4, 3, 6, 8])

    model = LinearRegression()
    model.fit(X, y)

    y_pred = model.predict(X)

    plt.scatter(X, y, color='blue', label='Actual')
    plt.plot(X, y_pred, color='red', label='Predicted')
    plt.title('Linear Regression')
    plt.legend()
    plt.show()


def program2():
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn.linear_model import LinearRegression

    months = np.array([1, 2, 3, 4, 5]).reshape(-1, 1)
    sales = np.array([150, 200, 250, 300, 330])

    model = LinearRegression()
    model.fit(months, sales)

    future_months = np.array([7, 8]).reshape(-1, 1)
    predicted_sales = model.predict(future_months)

    print(f"Predicted Sales for 7th Month: {predicted_sales[0]:.2f}")
    print(f"Predicted Sales for 8th Month: {predicted_sales[1]:.2f}")

    plt.scatter(months, sales, color='blue', label='Actual Sales')
    plt.plot(months, model.predict(months), color='green', label='Regression Line')
    plt.scatter(future_months, predicted_sales, color='red', label='Predicted Sales')
    plt.xlabel('Month')
    plt.ylabel('Sales')
    plt.title('Sales Prediction using Linear Regression')
    plt.legend()
    plt.grid(True)
    plt.show()


def program3():
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.datasets import load_iris
    from sklearn import tree
    import matplotlib.pyplot as plt

    iris = load_iris()
    clf = DecisionTreeClassifier()
    clf.fit(iris.data, iris.target)

    plt.figure(figsize=(10, 6))
    tree.plot_tree(clf, filled=True, feature_names=iris.feature_names, class_names=iris.target_names)
    plt.title("Decision Tree for Iris Dataset")
    plt.show()


def program4():
    import pandas as pd
    from sklearn.preprocessing import LabelEncoder
    from sklearn.naive_bayes import CategoricalNB
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score

    data = {
        'GPA': ['High', 'Low', 'Medium', 'High', 'Low', 'Medium', 'High'],
        'Internships': ['Yes', 'No', 'Yes', 'No', 'No', 'No', 'Yes'],
        'Projects': ['Good', 'Poor', 'Good', 'Average', 'Poor', 'Average', 'Good'],
        'Communication': ['Good', 'Poor', 'Average', 'Good', 'Poor', 'Average', 'Good'],
        'JobOffer': ['Yes', 'No', 'Yes', 'Yes', 'No', 'No', 'Yes']
    }

    df = pd.DataFrame(data)
    le = LabelEncoder()
    for col in df.columns:
        df[col] = le.fit_transform(df[col])

    X = df.drop('JobOffer', axis=1)
    y = df['JobOffer']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    model = CategoricalNB()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, y_pred))

    sample = pd.DataFrame([[2, 1, 1, 1]])
    prediction = model.predict(sample)
    print("Job Offer Prediction (0=No, 1=Yes):", prediction[0])


def program5():
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.metrics import accuracy_score, precision_score, f1_score, confusion_matrix, classification_report
    import matplotlib.pyplot as plt
    import seaborn as sns

    data = load_iris()
    X = data.data
    y = data.target

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    knn = KNeighborsClassifier(n_neighbors=3)
    knn.fit(X_train, y_train)
    y_pred = knn.predict(X_test)

    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Precision:", precision_score(y_test, y_pred, average='macro'))
    print("F1 Score:", f1_score(y_test, y_pred, average='macro'))

    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 4))
    sns.heatmap(cm, annot=True, cmap='Blues', fmt='d',
                xticklabels=data.target_names, yticklabels=data.target_names)
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.show()

    print("\nClassification Report:\n", classification_report(y_test, y_pred, target_names=data.target_names))



# ===================== 🔍 Source Code Introspection Functions ===================== #

def print_program1(): print(inspect.getsource(program1))
def print_program2(): print(inspect.getsource(program2))
def print_program3(): print(inspect.getsource(program3))
def print_program4(): print(inspect.getsource(program4))
def print_program5(): print(inspect.getsource(program5))


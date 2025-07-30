
import inspect

# 📦 Program 1: Frequency Table and Bar Plot
def program1():
    from sklearn.linear_model import LinearRegression
    import numpy as np
    import matplotlib.pyplot as plt

    # Sample data
    X = np.array([[1], [2], [3], [4], [5]])
    y = np.array([1, 4, 3, 6, 8])

    # Model
    model = LinearRegression()
    model.fit(X, y)

    # Prediction
    y_pred = model.predict(X)

    # Plot
    plt.scatter(X, y, color='blue', label='Actual')
    plt.plot(X, y_pred, color='red', label='Predicted')
    plt.title('Linear Regression')
    plt.legend()
    plt.show()


# 📊 Program 2: Histogram, Frequency Polygon, Ogive
def program2():
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn.linear_model import LinearRegression

    # Months (1 to 5)
    months = np.array([1, 2, 3, 4, 5]).reshape(-1, 1)

    # Sales
    sales = np.array([150, 200, 250, 300, 330])

    # Model
    model = LinearRegression()
    model.fit(months, sales)

    # Predict 7th and 8th month sales
    future_months = np.array([7, 8]).reshape(-1, 1)
    predicted_sales = model.predict(future_months)

    print(f"Predicted Sales for 7th Month: {predicted_sales[0]:.2f}")
    print(f"Predicted Sales for 8th Month: {predicted_sales[1]:.2f}")

    # Plotting
    plt.scatter(months, sales, color='blue', label='Actual Sales')
    plt.plot(months, model.predict(months), color='green', label='Regression Line')
    plt.scatter(future_months, predicted_sales, color='red', label='Predicted Sales')
    plt.xlabel('Month')
    plt.ylabel('Sales')
    plt.title('Sales Prediction using Linear Regression')
    plt.legend()
    plt.grid(True)
    plt.show()

# 📈 Program 3: Mean, Median, Mode
def program3():
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.datasets import load_iris
    from sklearn import tree
    import matplotlib.pyplot as plt

    # Load dataset
    iris = load_iris()
    clf = DecisionTreeClassifier()
    clf.fit(iris.data, iris.target)

    # Visualize the tree
    plt.figure(figsize=(10, 6))
    tree.plot_tree(clf, filled=True, feature_names=iris.feature_names, class_names=iris.target_names)
    plt.title("Decision Tree for Iris Dataset")
    plt.show()


# 📉 Program 4: Quartiles, Percentiles, Box Plot
def program4():
    import pandas as pd
    from sklearn.preprocessing import LabelEncoder
    from sklearn.naive_bayes import CategoricalNB
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score

    # Sample dataset
    data = {
        'GPA': ['High', 'Low', 'Medium', 'High', 'Low', 'Medium', 'High'],
        'Internships': ['Yes', 'No', 'Yes', 'No', 'No', 'No', 'Yes'],
        'Projects': ['Good', 'Poor', 'Good', 'Average', 'Poor', 'Average', 'Good'],
        'Communication': ['Good', 'Poor', 'Average', 'Good', 'Poor', 'Average', 'Good'],
        'JobOffer': ['Yes', 'No', 'Yes', 'Yes', 'No', 'No', 'Yes']
    }

    df = pd.DataFrame(data)

    # Encode categorical features
    le = LabelEncoder()
    for col in df.columns:
        df[col] = le.fit_transform(df[col])

    # Features and target
    X = df.drop('JobOffer', axis=1)
    y = df['JobOffer']

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Naive Bayes model
    model = CategoricalNB()
    model.fit(X_train, y_train)

    # Predict and evaluate
    y_pred = model.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, y_pred))

    # Predict for new student [High, Yes, Good, Good]
    sample = pd.DataFrame([[2, 1, 1, 1]])
    prediction = model.predict(sample)
    print("Job Offer Prediction (0=No, 1=Yes):", prediction[0])


# 📐 Program 5: Geometric, Harmonic, Weighted Mean
def program5():
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.metrics import accuracy_score, precision_score, f1_score, confusion_matrix, classification_report
    import matplotlib.pyplot as plt
    import seaborn as sns

    # Load dataset
    data = load_iris()
    X = data.data
    y = data.target

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Train KNN
    knn = KNeighborsClassifier(n_neighbors=3)
    knn.fit(X_train, y_train)

    # Predict
    y_pred = knn.predict(X_test)

    # Metrics
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average='macro')
    f1 = f1_score(y_test, y_pred, average='macro')
    cm = confusion_matrix(y_test, y_pred)

    # Output
    print("Accuracy:", acc)
    print("Precision:", prec)
    print("F1 Score:", f1)
    print("Confusion Matrix:\n", cm)

    # Heatmap
    plt.figure(figsize=(6, 4))
    sns.heatmap(cm, annot=True, cmap='Blues', fmt='d',
                xticklabels=data.target_names, yticklabels=data.target_names)
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.show()

    # Classification report
    print("\nClassification Report:\n", classification_report(y_test, y_pred, target_names=data.target_names))

def python():
    #1
    m1 = int(input("Enter the marks in the first test: "))
    m2 = int(input("Enter the marks in the second test: "))
    m3 = int(input("Enter the marks in the third test: "))

    # Calculate the total of the best two marks
    if m1 > m2:
        if m2 > m3:
            total = m1 + m2
        else:
            total = m1 + m3
    elif m1 > m3:
        total = m1 + m2
    else:
        total = m2 + m3

    avg = total / 2
    print("The average of the best two test marks is:", avg)


    #2
    number = int(input("Enter the Number: "))
    temp = number
    reverse = 0

    while number > 0:
        dig = number % 10
        reverse = reverse * 10 + dig
        number = number // 10

    print("The Reverse Number is:", reverse)

    if temp == reverse:
        print("The reverse number is a palindrome")
    else:
        print("The number is not a palindrome")



    #3
    def fn(n):
        if n == 1:
            return 0
        elif n == 2:
            return 1
        else:
            return fn(n - 1) + fn(n - 2)

    num = int(input("Enter a Number: "))

    if num > 0:
        print("fn(", num, ") = ", fn(num), sep="")
    else:
        print("Error in input")



    #4
    s = input("Enter a sentence: ")
    w, d, u, l = 0, 0, 0, 0

    # Count words
    l_w = s.split()
    w = len(l_w)

    # Count digits, uppercase letters, and lowercase letters
    for c in s:
        if c.isdigit():
            d += 1
        elif c.isupper():
            u += 1
        elif c.islower():
            l += 1

    # Output the results
    print("No of Words: ", w)
    print("No of Digits: ", d)
    print("No of Uppercase letters: ", u)
    print("No of Lowercase letters: ", l)


    #5
    def insertion_sort(alist):
        for i in range(1, len(alist)):
            temp = alist[i]
            j = i - 1
            while j >= 0 and temp < alist[j]:
                alist[j + 1] = alist[j]
                j -= 1
            alist[j + 1] = temp

    # Get input from user
    alist = input("Enter the list of numbers: ").split()
    alist = [int(x) for x in alist]

    # Perform sorting
    insertion_sort(alist)

    # Display sorted list
    print("Sorted List:", alist)



    #7
    import re

    # Without using regular expressions
    def isphonenumber(numStr):
        if len(numStr) != 12:
            return False
        for i in range(len(numStr)):
            if i == 3 or i == 7:
                if numStr[i] != "-":
                    return False
            else:
                if not numStr[i].isdigit():
                    return False
        return True

    # Using regular expressions
    def chkphonenumber(numStr):
        ph_no_pattern = re.compile(r'^\d{3}-\d{3}-\d{4}$')
        if ph_no_pattern.match(numStr):
            return True
        else:
            return False

    # Input
    ph_num = input("Enter a phone number (format: XXX-XXX-XXXX): ")

    # Without using regular expressions
    print("\nWithout using Regular Expression:")
    if isphonenumber(ph_num):
        print("Valid phone number")
    else:
        print("Invalid phone number")

    # Using regular expressions
    print("\nUsing Regular Expression:")
    if chkphonenumber(ph_num):
        print("Valid phone number")
    else:
        print("Invalid phone number")


    #11
    class Employee:
        def __init__(self):  # Correct constructor name
            self.name = ""
            self.empId = ""
            self.dept = ""
            self.salary = 0

        def getEmpDetails(self):
            self.name = input("Enter Employee name: ")
            self.empId = input("Enter Employee ID: ")
            self.dept = input("Enter Employee Dept: ")
            self.salary = int(input("Enter Employee Salary: "))

        def showEmpDetails(self):
            print("\nEmployee Details")
            print("Name   : ", self.name)
            print("ID     : ", self.empId)
            print("Dept   : ", self.dept)
            print("Salary : ", self.salary)

        def updtSalary(self):
            self.salary = int(input("\nEnter new Salary: "))
            print("Updated Salary:", self.salary)

    # Create and use the object
    e1 = Employee()
    e1.getEmpDetails()
    e1.showEmpDetails()
    e1.updtSalary()



def print_program1():
    print("Source code for program1:")
    print(inspect.getsource(program1))

def print_program2():
    print("\nSource code for program2:")
    print(inspect.getsource(program2))

def print_program3():
    print("\nSource code for program3:")
    print(inspect.getsource(program3))

def print_program4():
    print("\nSource code for program4:")
    print(inspect.getsource(program4))

def print_program5():
    print("\nSource code for program5:")
    print(inspect.getsource(program5))

def print_python():
    print("\nSource code for program5:")
    print(inspect.getsource(python))


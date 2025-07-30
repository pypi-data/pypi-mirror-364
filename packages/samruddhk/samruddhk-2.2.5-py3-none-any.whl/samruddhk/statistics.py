import inspect

# ===================== 📦 ML and Visualization Programs ===================== #

def program1():
    from sklearn import datasets
    from sklearn.model_selection import train_test_split
    from sklearn.svm import SVC
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
    import matplotlib.pyplot as plt
    import seaborn as sns

    # Load Iris dataset
    iris = datasets.load_iris()
    X = iris.data
    y = iris.target

    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Train SVM classifier (linear kernel)
    svm = SVC(kernel='linear')
    svm.fit(X_train, y_train)

    # Predict on test set
    y_pred = svm.predict(X_test)

    # Evaluation metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='macro')
    recall = recall_score(y_test, y_pred, average='macro')
    f1 = f1_score(y_test, y_pred, average='macro')
    conf_matrix = confusion_matrix(y_test, y_pred)

    # Print metrics
    print("Accuracy:", accuracy)
    print("Precision:", precision)
    print("Recall:", recall)
    print("F1 Score:", f1)
    print("\nClassification Report:\n", classification_report(y_test, y_pred, target_names=iris.target_names))

    # Plot confusion matrix
    plt.figure(figsize=(6, 4))
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues',
                xticklabels=iris.target_names,
                yticklabels=iris.target_names)
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Confusion Matrix')
    plt.show()



def program2():
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.cluster.hierarchy import linkage, dendrogram

    # Data points
    points = np.array([
        [1, 2],
        [2, 3],
        [5, 8],
        [6, 9],
        [3, 3]
    ])
    labels = ['A', 'B', 'C', 'D', 'E']

    # Single linkage clustering
    linked = linkage(points, method='single')

    # Dendrogram
    plt.figure(figsize=(8, 5))
    dendrogram(linked, labels=labels, distance_sort='ascending')
    plt.title('Single Linkage Hierarchical Clustering')
    plt.xlabel('Points')
    plt.ylabel('Euclidean Distance')
    plt.grid(True)
    plt.show()



def program3():
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.cluster.hierarchy import linkage, dendrogram

    # Sample 2D points
    points = np.array([
        [1, 2],
        [2, 3],
        [3, 3],
        [8, 7],
        [8, 8],
        [25, 80]
    ])

    # Average linkage
    linked = linkage(points, method='average')

    # Dendrogram
    plt.figure(figsize=(8, 5))
    dendrogram(linked,
            labels=np.arange(1, len(points)+1),
            distance_sort='ascending',
            show_leaf_counts=True)
    plt.title('Average Linkage Hierarchical Clustering')
    plt.xlabel('Point Index')
    plt.ylabel('Distance')
    plt.grid(True)
    plt.show()



def program4():
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.cluster.hierarchy import linkage, dendrogram

    # Data points
    points = np.array([
        [1, 2],
        [2, 3],
        [3, 3],
        [5, 8],
        [6, 8],
        [7, 9]
    ])

    # Complete linkage clustering
    linked = linkage(points, method='complete')

    # Dendrogram
    plt.figure(figsize=(8, 5))
    dendrogram(linked, labels=range(1, len(points)+1))
    plt.title('Complete Linkage Hierarchical Clustering')
    plt.xlabel('Data Point Index')
    plt.ylabel('Distance')
    plt.grid(True)
    plt.show()



def program5():
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn.cluster import KMeans
    from sklearn.datasets import make_blobs

    # Generate synthetic data
    X, _ = make_blobs(n_samples=300, centers=3, cluster_std=0.60, random_state=0)

    # K-Means clustering
    kmeans = KMeans(n_clusters=3, random_state=0)
    kmeans.fit(X)
    y_kmeans = kmeans.predict(X)

    # Plot clusters and centroids
    plt.scatter(X[:, 0], X[:, 1], c=y_kmeans, s=50, cmap='viridis')
    centers = kmeans.cluster_centers_
    plt.scatter(centers[:, 0], centers[:, 1], c='red', s=200, alpha=0.75, marker='X')
    plt.title("K-Means Clustering")
    plt.xlabel("Feature 1")
    plt.ylabel("Feature 2")
    plt.grid(True)
    plt.show()


# ===================== 🔍 Source Code Introspection Functions ===================== #

def print_program1(): print(inspect.getsource(program1))
def print_program2(): print(inspect.getsource(program2))
def print_program3(): print(inspect.getsource(program3))
def print_program4(): print(inspect.getsource(program4))
def print_program5(): print(inspect.getsource(program5))


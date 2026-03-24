import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# =======================
# 1. LOAD DATA
# =======================
dataset = pd.read_csv("Credit_Card_Applications.csv")

X = dataset.iloc[:, :-1]
y = dataset.iloc[:, -1]

print("Dataset shape:", dataset.shape)

# =======================
# 2. EDA (basic)
# =======================
print("\nINFO:")
print(dataset.info())

print("\nDESCRIPTION:")
print(dataset.describe())

print("\nCLASS DISTRIBUTION:")
print(dataset["Class"].value_counts())

plt.figure()
plt.hist(dataset["A2"])
plt.title("Feature A2 Distribution")
plt.show()

# =======================
# 3. SPLIT
# =======================
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =======================
# 4. SCALING
# =======================
from sklearn.preprocessing import StandardScaler

sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

# =======================
# 5. TRAIN MODELS
# =======================
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

lr = LogisticRegression(max_iter=1000)
rf = RandomForestClassifier(n_estimators=100)

lr.fit(X_train, y_train)
rf.fit(X_train, y_train)

models = {
    "Logistic Regression": lr,
    "Random Forest": rf
}

# =======================
# 6. EVALUATION
# =======================
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, roc_auc_score, roc_curve

for name, model in models.items():
    print(f"\n===== {name} =====")

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_prob)

    print("Accuracy:", acc)
    print("ROC AUC:", roc_auc)
    print("Confusion Matrix:\n", cm)
    print("Classification Report:\n", report)

    # =======================
    # 7. CONFUSION MATRIX PLOT
    # =======================
    plt.figure()
    plt.imshow(cm)
    plt.title(f"{name} - Confusion Matrix")
    plt.colorbar()

    for i in range(len(cm)):
        for j in range(len(cm[0])):
            plt.text(j, i, cm[i][j])

    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.show()

    # =======================
    # 8. ROC CURVE
    # =======================
    fpr, tpr, _ = roc_curve(y_test, y_prob)

    plt.figure()
    plt.plot(fpr, tpr)
    plt.title(f"{name} - ROC Curve")
    plt.xlabel("FPR")
    plt.ylabel("TPR")
    plt.show()

    # =======================
    # 9. FEATURE IMPORTANCE
    # =======================
    if hasattr(model, "coef_"):
        importance = model.coef_[0]
    else:
        importance = model.feature_importances_

    plt.figure()
    plt.barh(dataset.columns[:-1], importance)
    plt.title(f"{name} - Feature Importance")
    plt.show()
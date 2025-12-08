import re, random, numpy as np, pandas as pd, unicodedata
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.pipeline import make_pipeline
import joblib

random.seed(42)
np.random.seed(42)

positivos = [
    "Excelente servicio","Muy buena atención","Me encantó el producto",
    "Rápido y confiable","Todo llegó perfecto","Calidad superior",
    "Lo recomiendo totalmente","Volveré a comprar","Precio justo y buena calidad",
    "El soporte fue amable","Experiencia increíble","Funcionó mejor de lo esperado",
    "Entregado a tiempo","Muy satisfecho","Cinco estrellas"
]

negativos = [
    "Pésimo servicio","Muy mala atención","Odio este producto",
    "Lento y poco confiable","Llegó dañado","Calidad terrible",
    "No lo recomiendo","No vuelvo a comprar","Caro y mala calidad",
    "El soporte fue grosero","Experiencia horrible","Peor de lo esperado",
    "Entregado tarde","Muy decepcionado","Una estrella"
]

def variantes(frase):
    extras = ["!", "!!", " 🙂", " 😡", " de verdad", " súper", " 10/10", " 1/10"]
    return frase + random.choice(extras)

pos = [variantes(p) for _ in range(10) for p in positivos]
neg = [variantes(n) for _ in range(10) for n in negativos]

df = pd.DataFrame({
    "texto": pos + neg,
    "etiqueta": [1]*len(pos) + [0]*len(neg)
}).sample(frac=1, random_state=42).reset_index(drop=True)

def limpiar(s: str) -> str:
    s = s.lower()
    s = re.sub(r"http\S+|www\S+", " ", s)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("utf-8")
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

df["texto_clean"] = df["texto"].apply(limpiar)

X_train_text, X_test_text, y_train, y_test = train_test_split(
    df["texto_clean"], df["etiqueta"], test_size=0.2, random_state=42, stratify=df["etiqueta"]
)

baseline = (y_test == int(round(y_train.mean()))).mean()

vectorizer = TfidfVectorizer(max_features=20000, ngram_range=(1,2), min_df=2)
X_train = vectorizer.fit_transform(X_train_text)
X_test = vectorizer.transform(X_test_text)

models = {
    "LinearSVC": LinearSVC(class_weight="balanced", random_state=42),
    "LogisticRegression": LogisticRegression(max_iter=2000),
    "SGDClassifier": SGDClassifier(loss="hinge", max_iter=2000, random_state=42)
}

metrics = {}

for name, model in models.items():
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    acc = accuracy_score(y_test, pred)
    metrics[name] = acc

    cm = confusion_matrix(y_test, pred)
    plt.figure()
    plt.imshow(cm)
    plt.title(f"Matriz de Confusión - {name}")
    plt.xlabel("Predicho")
    plt.ylabel("Real")
    plt.colorbar()
    plt.savefig(f"cm_{name}.png")
    plt.close()


plt.figure()
plt.bar(metrics.keys(), metrics.values())
plt.axhline(baseline)
plt.title("Comparación de modelos (Accuracy)")
plt.ylabel("Accuracy")
plt.savefig("comparacion_modelos.png")
plt.close()


param_grid = {
    "tfidfvectorizer__ngram_range": [(1,1), (1,2)],
    "tfidfvectorizer__min_df": [1, 2],
    "linearsvc__C": [0.1, 1, 3]
}

pipe = make_pipeline(
    TfidfVectorizer(),
    LinearSVC()
)

grid = GridSearchCV(pipe, param_grid, cv=3, scoring="f1_macro")
grid.fit(df["texto_clean"], df["etiqueta"])

plt.figure(figsize=(10, 4))
plt.axis("off")
plt.text(
    0.01, 0.5,
    f"Mejores parámetros:\n{grid.best_params_}\nMejor F1: {grid.best_score_:.3f}",
    fontsize=12
)
plt.savefig("gridsearch_resultados.png")
plt.close()

joblib.dump(vectorizer, "tfidf.joblib")
joblib.dump(models["LinearSVC"], "modelo.joblib")

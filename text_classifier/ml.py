import numpy as np
from asgiref.sync import async_to_sync
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC

from ml_api.django import connect

RANDOM_SEED = 5894

CLASSIFIERS = {
    'RandomForestClassifier': {
        'classifier': [RandomForestClassifier(random_state=RANDOM_SEED)],
        'classifier__n_estimators': [100, 200, 50],
    },
    'GradientBoostingClassifier': {
        'classifier': [GradientBoostingClassifier(random_state=RANDOM_SEED)],
        'classifier__loss': ['log_loss', 'exponential'],
        'classifier__n_estimators': [100, 200, 50],
        'classifier__subsample': [1.0, 0.2, 0.1],
    },
    'SVC': {
        'classifier': [SVC(random_state=RANDOM_SEED, probability=True)],
        'classifier__kernel': ['linear', 'poly', 'rbf', 'sigmoid'],
    },
    'KNeighborsClassifier': {
        'classifier': [KNeighborsClassifier()]
    },
    'MLPClassifier': {
        'classifier': [MLPClassifier(random_state=RANDOM_SEED)],
        'classifier__activation': ['identity', 'logistic', 'reul'],
        'classifier__alpha': [0, 0.0001, 0.01],
        'classifier__learning_rate': ['constant', 'adaptive'],
    },
}


async def get_embeddings(texts, model):
    async with connect() as client:
        return await client.sentence_embeddings(model, texts)


def optimize_model(texts, classes, sbert_models, classifiers, n_jobs=None):
    train_texts, test_texts, train_classes, test_classes = train_test_split(
        texts,
        classes,
        random_state=RANDOM_SEED,
    )

    pipeline = Pipeline([('classifier', SVC())])

    params = [CLASSIFIERS[classifier] for classifier in classifiers]

    search_scores = []
    search_models = []
    for sbert_model in sbert_models:
        train_embeddings = async_to_sync(get_embeddings)(train_texts, sbert_model).embeddings
        search = GridSearchCV(pipeline, params, n_jobs=n_jobs)
        search.fit(train_embeddings, train_classes)

        search_models.append(search.best_estimator_)
        search_scores.append(search.best_score_)

    idx = np.argmax(search_scores)
    model = search_models[idx]

    test_embeddings = async_to_sync(get_embeddings)(test_texts, sbert_models[idx]).embeddings

    prediction = model.predict(test_embeddings)
    report = classification_report(test_classes, prediction, output_dict=True)
    return model, sbert_models[idx], report

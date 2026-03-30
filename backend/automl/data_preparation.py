import pandas as pd
from sklearn.pipeline import Pipeline
import automl.tuple as t
import automl.data_info as Di


def data_preparation(train_df: pd.DataFrame, test_df: pd.DataFrame, dev_df: pd.DataFrame) -> t.Data_set:

    # Supprimer les doublons
    train_df = train_df.drop_duplicates()
    test_df  = test_df.drop_duplicates()
    dev_df   = dev_df.drop_duplicates()

    train_df = train_df.sample(frac=1, random_state=42).reset_index(drop=True)
    test_df  = test_df.sample(frac=1, random_state=42).reset_index(drop=True)
    dev_df   = dev_df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Séparer X et Y pour chaque split
    x_train = train_df.drop(columns=["target"])
    y_train = train_df[["target"]]

    x_test = test_df.drop(columns=["target"])
    y_test = test_df[["target"]]

    x_dev = dev_df.drop(columns=["target"])
    y_dev = dev_df[["target"]]

    type_problem, equilibre_labels = Di.data_info(train_df)

    data_set = t.Data_set(
        x_train,
        y_train,
        x_dev,
        y_dev,
        x_test,
        y_test,
        type_problem,
        equilibre_labels,
        preprocessing_pipeline=None
    )

    return data_set
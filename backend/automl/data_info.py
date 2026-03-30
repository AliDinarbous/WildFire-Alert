import automl.data_retrive as dr
import automl.tuple as t

"""
Prends un dataframe et retourne une liste des labels
"""
def get_labels(df):
    labels = [col for col in df.columns if col.startswith('target')]
    return labels

"""
Prends un dataframe et retourne une le type du probleme
"""
def determine_problem_type(df, labels):

    if len(labels) == 1:
        col = labels[0]
        unique_values = df[col].unique()
        if set(unique_values).issubset({0, 1}):
            return "classification_binaire"
        else:
            return "regression"

    else:
        rows = df[labels].head(3)
        if (rows.sum(axis=1) > 1).any():
            return "multilabel"
        else:
            return "multiclass"

"""
Prends un dataframe et la liste des labels, Verifie si la proporton d'une label 
inferieur 40% , si oui indique DESIQUILIBRE sinon EQUILIBRE
"""
def check_balance(df, labels):
    """
    Vérifie si le dataset est équilibré.
    Retourne True si équilibré, False si déséquilibré.
    Un label est considéré déséquilibré si la classe minoritaire < 40%.
    """
    for label in labels:
        counts = df[label].value_counts(normalize=True)
        if len(counts) > 1:
            minor_class_percent = counts.min()
            if minor_class_percent < 0.4:
                # Dataset déséquilibré
                return False
            else:
                # Dataset équilibré
                return True
    # Par défaut, considérer comme équilibré si pas assez d'info
    return True

"""
Prends un dataframe, indique le type de probleme et l'equilibre des labels
"""
def data_info(df):
    # Recuperer les labels du df
    labels = get_labels(df)

    # Indique le type du probleme
    type_probleme =  t.type_enum(determine_problem_type(df, labels))

    # Retourne si dataset equilibre pour non
    equilibre_labels = check_balance(df, labels)

    return (type_probleme, equilibre_labels)


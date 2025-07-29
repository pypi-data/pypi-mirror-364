import pandas as pd
import numpy as np

class DefectDataVectorizer:
    def __init__(self, csv_path: str, category_column: str = 'category_predicted', features: list = None):
        """
        Inicializa el vectorizador de datos de defectos.

        :param csv_path: Ruta al archivo CSV con datos de defectos classificados.
        :param category_column: Nombre de la columna de categoría.
        :param features: Lista de columnas numéricas a extraer; si None, se inferirán todas las numéricas excepto la de categoría.
        """
        self.csv_path = csv_path
        self.category_column = category_column
        self.features = features
        self.df = None
        self.vectors = {}

    def load_data(self):
        """
        Carga el CSV en un DataFrame.
        """
        self.df = pd.read_csv(self.csv_path)
        if self.features is None:
            # Tomar todas menos la categoría y columnas no numéricas
            numeric = self.df.select_dtypes(include=[np.number]).columns.tolist()
            self.features = [col for col in numeric if col != self.category_column]
        return self.df

    def extract_vectors(self):
        """
        Filtra y convierte en arrays numpy por cada categoría encontrada.

        :return: Diccionario mapping categoría -> numpy array de shape (n_samples, n_features)
        """
        if self.df is None:
            raise ValueError("Carga los datos primero con load_data().")

        categories = self.df[self.category_column].unique()
        for cat in categories:
            subset = self.df[self.df[self.category_column] == cat]
            self.vectors[cat] = subset[self.features].to_numpy()
        return self.vectors

    def print_shapes(self):
        """
        Muestra la forma de cada vector extraído.
        """
        for cat, arr in self.vectors.items():
            print(f"{cat}: {arr.shape}")

# Ejemplo de uso:
# vectorizer = DefectDataVectorizer(csv_path='outputs/csv/defect_data_classified.csv')
# df = vectorizer.load_data()
# vectors = vectorizer.extract_vectors()
# vectorizer.print_shapes()
# Ahora vectors['1-4'], vectors['5-10'], vectors['11-15'] contienen los arrays numpy.

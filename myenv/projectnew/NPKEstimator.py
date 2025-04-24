import warnings
import numpy as np
import pandas as pd
import category_encoders as ce
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

warnings.filterwarnings('ignore')

class NPKEstimator:
    def __init__(self, data='Nutrient_recommendation.csv'):
        self.df = pd.read_csv(data, header=None)
        self.rename_columns()
        self.preprocess_data()
        self.mapping, self.encoder = self.crop_mapper()
        self.models = {}
        self.train_models()

    def rename_columns(self):
        self.df.columns = ['Crop', 'Temperature', 'Humidity', 'Rainfall', 'Label_N', 'Label_P', 'Label_K']
        self.df.drop(self.df.index[:1], inplace=True)

    def preprocess_data(self):
        cols_numeric = ['Temperature', 'Humidity', 'Rainfall', 'Label_N', 'Label_P', 'Label_K']
        self.df[cols_numeric] = self.df[cols_numeric].apply(pd.to_numeric)

        median_n = self.df[self.df['Label_N'] > 0]['Label_N'].median()
        self.df['Label_N'] = self.df['Label_N'].replace(0, median_n)

        for col in ['Label_N', 'Label_P', 'Label_K']:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            self.df = self.df[(self.df[col] >= lower_bound) & (self.df[col] <= upper_bound)]

    def crop_mapper(self):
        crops_unique = np.unique(self.df['Crop'].str.strip().str.lower())
        mapping = {crop: idx for idx, crop in enumerate(crops_unique, start=1)}
        ordinal_cols_mapping = [{"col": "Crop", "mapping": mapping}]
        encoder = ce.OrdinalEncoder(cols='Crop', mapping=ordinal_cols_mapping, return_df=True)
        return mapping, encoder

    def train_models(self):
        X = self.df[['Crop', 'Temperature', 'Humidity', 'Rainfall']]
        X_encoded = self.encoder.fit_transform(X)
        
        for nutrient in ['Label_N', 'Label_P', 'Label_K']:
            y = self.df[nutrient]
            X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)
            model = RandomForestRegressor(n_estimators=50, random_state=42)
            model.fit(X_train, y_train)
            self.models[nutrient] = model

    def estimate_npk(self, crop_name, temperature, humidity, rainfall):
        crop_key = crop_name.strip().lower()
        
        if crop_key not in self.mapping:
            raise ValueError(f"Crop '{crop_name}' not found in dataset. Available crops: {list(self.mapping.keys())}")

        crop_encoded_value = self.mapping[crop_key]
        query_input = [[crop_encoded_value, temperature, humidity, rainfall]]

        result = {}
        for nutrient_label in ['Label_N', 'Label_P', 'Label_K']:
            prediction = self.models[nutrient_label].predict(query_input)[0]
            result[nutrient_label] = round(prediction, 2)

        return result

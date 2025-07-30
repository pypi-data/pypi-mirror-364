import os
import os.path
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler  

class Dataset():
    def __init__(self, dataset_name):
        self.dataset_name = dataset_name
        self.set_dataset_path()
    
    def get_dataset_name(self):
        return self.dataset_name
        
    def get_dataset_path(self):
        return self.dataset_path
    
    def set_dataset_path(self):
        lib_path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(lib_path, 'datasets', f'{self.dataset_name}.csv')
        if os.path.exists(path):
            self.dataset_path = path
        else:
            raise OSError(f"File '{path}' not found.")
    
    @staticmethod
    def path_datasets():
        lib_path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(lib_path, 'datasets')
        #path = os.path.join(os.getcwd(), 'datasets')
        if os.path.exists(path):
            return path
        else:
            raise OSError(f"Directory '{path}' not found.")
    
    
    def load_dataset(self, split_target=False, normalize=False, scaler_type="minmax"):
        try:
            df = pd.read_csv(self.dataset_path)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Dataset not found at {self.dataset_path}.") from e

        if normalize:
            X, y = self.split_target(df)
            if scaler_type == "minmax":
                scaler = MinMaxScaler()
            elif scaler_type == "standard":
                scaler = StandardScaler()
            elif scaler_type == "robust":
                scaler = RobustScaler()
            else:
                raise ValueError(f"Unsupported scaler_type: {scaler_type}")

            X_scaled = scaler.fit_transform(X)
            X_scaled_df = pd.DataFrame(X_scaled, columns=X.columns)
            df = pd.concat([X_scaled_df, y], axis=1)

        if split_target:
            return self.split_target(df)

        return df
    
    @staticmethod
    def split_target(dataset):
        if not isinstance(dataset, pd.DataFrame):
            raise TypeError(f'Dataset must be a DataFrame. {type(dataset)} was provided.')
        
        X = dataset.drop(columns=dataset.columns[-1])
        y = dataset.iloc[:, -1:]
        
        return X, y
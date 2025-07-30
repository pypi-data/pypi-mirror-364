import pandas as pd
from sp00kyvectors.core import Vector
from collections import defaultdict
import pandas as pd
from typing import *


class SpookyDF(Vector):
    '''
    Vector stats and cleaning for pandas DataFrames.
    '''
    def __init__(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Expected a pandas DataFrame.")
        super().__init__()
        self.df = df
        self.time = df['Timestamp']
        self.df = self.df.drop(axis=1, labels='Timestamp')
        self.vectors = defaultdict()

    def drop_nulls(self, threshold=0.5):
        '''Drop columns with more than threshold proportion of nulls'''
        limit = int(threshold * len(self.df))
        self.df = self.df.dropna(axis=1, thresh=limit)

    def fill_nulls(self, strategy='mean'):
        '''Fill null values in numeric columns'''
        for col in self.df.select_dtypes(include='number').columns:
            if strategy == 'mean':
                self.df[col] = self.df[col].fillna(self.df[col].mean())
            elif strategy == 'median':
                self.df[col] = self.df[col].fillna(self.df[col].median())
            elif strategy == 'zero':
                self.df[col] = self.df[col].fillna(0)
            elif strategy == 'drop':
                self.df.dropna()

    def standardize_column_names(self):
        '''Lowercase, strip spaces, replace spaces with underscores'''
        self.df.columns = self.df.columns.str.strip().str.lower().str.replace(' ', '_')

    def convert_dates(self, columns):
        '''Convert columns to datetime'''
        for col in columns:
            self.df[col] = pd.to_datetime(self.df[col], errors='coerce')

    def remove_duplicates(self):
        '''Drop duplicate rows'''
        self.df = self.df.drop_duplicates()

    def clip_outliers(self, z_thresh=3):
        '''Clip values outside of z_thresh standard deviations'''
        from scipy.stats import zscore
        num_cols = self.df.select_dtypes(include='number')
        z_scores = zscore(num_cols, nan_policy='omit')
        mask = (abs(z_scores) < z_thresh).all(axis=1)
        self.df = self.df[mask]

    def get_clean_df(self):
        '''Return cleaned DataFrame'''
        self.remove_duplicates()
        #self.drop_nulls()
        self.remove_duplicates()
        self.clip_outliers()
        self.standardize_column_names()
        return self.df
    
    def drop_outliers_iqr(self,col: str) -> pd.DataFrame:
        """
        Remove outliers from a DataFrame column using the IQR method.
        
        Args:
            df (pd.DataFrame): The input DataFrame.
            col (str): The column name to check for outliers.
            
        Returns:
            pd.DataFrame: A new DataFrame with outliers removed for that column.
        """
        df = self.df 
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]

    def load_cols_into_vectors(self):
        df = self.get_clean_df()
        for col in range(len(df.columns)):
            df_column_name = df.columns[col]
            self.vectors[df_column_name] = Vector(
                label=df_column_name,
                data_points = df[df_column_name]
            )
        return self.vectors
    

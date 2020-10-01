import pandas as pd
import sqlite3 
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re
from warnings import filterwarnings
# Pandas will give a lot of warning while I am mutating data frames in functions.
filterwarnings('ignore')


"""
The following code to clean up the budgets titles and movies basics table to get it 
to a place where the genres are their own seperate boolean series
"""

def string_cleaner(series):
    return series.str.strip().str.lower()

def list_to_string(df, column):
    return df[column].apply(lambda x: " ".join(x))

def string_from_list(df, column):
    things = ["'", "[","]"]
    for thing in things:
        df[column] = df[column].apply(lambda x: x.replace(f"{thing}",""))
    return df[column].apply(lambda x: ",".join([x.strip() for x in x.split(",")]))


def remove_null_genre(df, column):
    """
    df --> datafram
    column --> str
    
    returns dataframe with no missing null values for that particular column name
    """
    return df[df[column].notnull()]

def genre_set_list(df):
    """
    df --> dataframe
    return --> list
    
    returns a list of all unique genre's in the dataframe
    """
    all_genres = list(df)
    return list(set([item for sublist in all_genres for item in sublist]))

def create_boolean_series(series, genre):
        """
        series --> panda's series
        genre --> string
        
        return boolean list 
        
        given a series and a particular genre, this function will return whether that row has that genre
        """
        return [genre in genres for genres in series]

def genre_list_to_series(df, L, genre):
    """
    df --> dataframe (scaffold)
    L --> boolean list or series generated by create_boolean_series
    genre --> str
    
    given a dataframe, series and a genre, this function will create a new column in the data frame using the list
    this mutates the original data frame
    
    """
    df[genre] = L 
    
    
def coerce_to_list(df, column):
    """
    df --> dataframe
    column --> string containing commas 
    
    returns a series where the string has been coerced into a list
    """
    return df[column].apply(lambda x: x.split(','))

def coerce_to_list_by_space(df, column):
    """
    df --> dataframe
    column --> string seperated by space
    
    returns a series where the string has been coerced into a list
    """
    return df[column].apply(lambda x: x.split(' '))



def generate_genre_dataframe(df):
    """
    df --> dataframe
    
    returns --> dataframe
    
    given a scaffold dataframe with a genres column will return that same data frame mutated such that each 
    genre is a new column and each row in that column is a boolean indicating if that observation has that genre in 
    it's list
    """
    # generate the list of genres
    L = genre_set_list(df.genres)
    # Loops through the list of genres
    for genre in L:
        # Create a boolean series for each genre
        boolean_series = create_boolean_series(df.genres,genre)
        # Append that genre to the dataframe
        genre_list_to_series(df, boolean_series, genre)
    return df

def lower_column_names(df):
    """
    df --> dataframe
    returns a list of the column names as lower case
    """
    return [x.lower() for x in df.columns]


def make_scaffold(df):
    """
    Takes a data frame and returns a stripped down version of that data frame for further processing
    """
    scaffold = df[(df.start_year>2000)&(df.start_year<2020) & (df.numvotes > 1000)]
    scaffold = scaffold[['tconst',
                           'primary_title', 
                           'genres', 
                           'numvotes', 
                           'averagerating',
                           'start_year', 
                           'runtime_minutes']]
    return scaffold

def genre_dict_mean(df, feature):
    """
    df -- > dataframe containing all genres as columns
    feature --> the name of the column, should be in list form already
    genre_list --> List, containing a complete of all genres in the dataframe
    """
    genre_list = list(df.genres)
    feature_dict = {}
    for genre in genre_list:
        feature_dict.update({genre:df[df[f'{genre}'] == True][f'{feature}'].mean()})
        # Sort dictionary by value
    return {k: v for k, v in sorted(feature_dict.items(), key=lambda item: item[1],reverse=True)}

def dict_to_pandas(dictionary):
    """
    Given a dictionary, returns a datafame indexed by the keys of the dataframe
    """
    return pd.DataFrame.from_dict(dictionary, orient='index')


def genre_pandas_mean(df, feature):
    """
    This is documentation
    df --> dataframe containing a genre column in list form
    feature --> string 
    
    """
    genre_list = genre_set_list(df.genres)
    feature_dict = {}
    for genre in genre_list:
        feature_dict.update({genre:df[df[f'{genre}'] == True][f'{feature}'].mean()})
        # Sort dictionary by value
    return dict_to_pandas({k: v for k, v in sorted(feature_dict.items(), key=lambda item: item[1],reverse=True)})


"""
The following function are with dealing with money, outliers and timeseries analysis
"""
    
def string_to_float(series):
    return series.str.strip().str.replace("$", "").str.replace(",","").astype(float)
    
    
    


def get_iqr_median(df, col_name):
    """
    Given a column name and a data frame, returns the median and the iqr of the series
    """
    hq = df[col_name].quantile(0.75) 
    median = df[col_name].quantile(0.5)
    lq = df[col_name].quantile(0.25)
    iqr = hq-lq
    return iqr, median

def is_outlier(x, iqr, median):
    """
    Given an input x, the iqr and median of the column
    returns to the user the a boolean value whether or not the the 
    value is outside of 1.5 times the IQR
    """
    if x > median + iqr*1.5:
        return True
    elif x < median - 1.5*iqr:
        return True
    else:
        return False

def find_outliers(df, column):
    """
    Returns a boolean series. True if outside IQR*1.5 range, False otherwise
    """
    IQR , median  = get_iqr_median(df, column)
    return df[column].apply(lambda x: is_outlier(x, IQR, median))

          
def categorize_production(x):
    m = int(x)
    k=''
    if m < 5000000:
        k = 'small'
    if 5000000 <= m <= 100000000:
        k = 'medium'
    if m > 100000000:
        k = 'large'
    return k


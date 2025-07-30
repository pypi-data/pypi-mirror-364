import os
import warnings
warnings.filterwarnings('ignore')

from flask import Flask, render_template, request
import pandas as pd

from . import tree_fitter


app = Flask(
    __name__,
    template_folder='build',
    static_folder='build/static',
)


def prepare_train_df():
    df = pd.read_parquet('train_df.parquet')
    target_column = os.environ['TARGET_COLUMN']
    
    for column in df.columns:
        if column == target_column:
            continue
        
        if pd.api.types.is_numeric_dtype(df[column]):
            if df[column].isna().any():
                df[column] = df[column].fillna(-1)
            continue

        for unique_value in df[column].drop_duplicates():
            if pd.isna(unique_value):
                df[f'{column}==np.nan'] = df[column].isna() * 1
            else:
                df[f'{column}=={unique_value}'] = (df[column]==unique_value) * 1

    train_df = df.drop(columns=target_column).select_dtypes('number')
    target = df[target_column]
    return train_df, target

train_df, target = prepare_train_df()


@app.route('/get_tree')
def get_tree():
    max_depth = int(request.args.get('maxDepth'))
    return tree_fitter.fit(train_df, target, max_depth)


@app.route('/node_analytics')
def show_node_analytics():
    return render_template('node_analytics.html')


@app.after_request
def enable_cors(response):
    response.headers.add("Access-Control-Allow-Headers", "authorization,content-type")
    response.headers.add("Access-Control-Allow-Methods", "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT")
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route('/')
def index():
    return render_template('index.html')

import os

import pandas as pd


def run(df: pd.DataFrame, target_column: str):
    df.to_parquet('train_df.parquet', index=False)
    os.environ['TARGET_COLUMN'] = target_column
    
    from interactive_dtree import app
    app.run(host='0.0.0.0', port=5003)

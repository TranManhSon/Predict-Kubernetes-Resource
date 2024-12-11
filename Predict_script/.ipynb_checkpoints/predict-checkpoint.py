from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import joblib
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# Mapping Service Label -> Label
service_mapping = {
    "emailservice": 1,
    "checkoutservice": 2,
    "recommendationservice": 3,
    "frontend": 4,
    "paymentservice": 5,
    "productcatalogservice": 6,
    "cartservice": 7,
    "redis-cart": 8,
    "currencyservice": 9,
    "shippingservice": 10,
    "adservice": 11,
}

output_file_path_final = 'final_service_metrics.xlsx'
output_file_path_limit_cpu = 'CPU_limit_per_pod.xlsx'
last_timestamp = pd.Timestamp('04:25:36.519536972')
end_timestamp_define = pd.Timestamp('09:45:00')  

# Load the scaler
scaler = joblib.load('scaler.pkl')

# Load the model
model_ann = load_model('model_ann.h5', custom_objects={'mse': 'mean_squared_error'}, compile=False)

print("Model and scaler loaded successfully.")

def handle_output(result_df):
# Flatten the values based on their structure
    if isinstance(result_df['CPU(t)'].iloc[0], list):
    # Handle lists
        result_df['CPU(t)'] = result_df['CPU(t)'].apply(lambda x: x[0][0] if isinstance(x[0], list) else x[0])
    elif isinstance(result_df['CPU(t)'].iloc[0], np.ndarray):
    # Handle numpy arrays
        result_df['CPU(t)'] = result_df['CPU(t)'].apply(lambda x: x.item())
    else:
    # Ensure numeric
        result_df['CPU(t)'] = pd.to_numeric(result_df['CPU(t)'], errors='coerce')
    return result_df

def load_last_data_metric(path):
    df = pd.read_excel(output_file_path_final)
    df_1 = df.tail(300)
    print(df_1.tail())
    df_1 = df_1.reset_index()
    df_1['TimeDate'] = pd.to_datetime(df_1['Timestamp'], unit= 's')  # Nếu Timestamp là Unix timestamp

    #min_timestamp = df_1['TimeDate'].min()
    #max_timestamp = df_1['TimeDate'].max()
    #print(f"Range of Timestamp: {min_timestamp} to {max_timestamp}")
    last_values = df_1[df_1['TimeDate'] <= last_timestamp].groupby('Label').tail(1)

    return last_values

def predict_future_resources(last_timestamp, end_timestamp, last_values, scaler, model):
    future_timestamps = []
    predictions = []

    while last_timestamp < end_timestamp:
        # Update to the next timestamp
        last_timestamp += pd.Timedelta(minutes=1)
        future_timestamps.append(last_timestamp)

        predicted_row = []  # Store predictions for this timestamp

        # Predict for each service
        for label in last_values['Label'].unique():
            # Get historical data for the service
            service_data = last_values[last_values['Label'] == label][
                ['CPU(t-1)', 'CPU(t-2)', 'CPU(t-3)', 'CPU(t-4)', 'CPU(t-5)']].iloc[0].values
            service_data = service_data.reshape(1, -1)  # Reshape to (1, 5)

            # Scale the data
            service_data_scaled = scaler.transform(service_data)

            # Make a prediction
            prediction_scaled = model.predict(service_data_scaled)

            # Store the prediction
            predicted_row.append({
                'Label': label,
                'CPU(t)': prediction_scaled
            })

            # Update historical data
            last_values.loc[last_values['Label'] == label, 'CPU(t-5)'] = last_values.loc[
                last_values['Label'] == label, 'CPU(t-4)']
            last_values.loc[last_values['Label'] == label, 'CPU(t-4)'] = last_values.loc[
                last_values['Label'] == label, 'CPU(t-3)']
            last_values.loc[last_values['Label'] == label, 'CPU(t-3)'] = last_values.loc[
                last_values['Label'] == label, 'CPU(t-2)']
            last_values.loc[last_values['Label'] == label, 'CPU(t-2)'] = last_values.loc[
                last_values['Label'] == label, 'CPU(t-1)']
            last_values.loc[last_values['Label'] == label, 'CPU(t-1)'] = prediction_scaled  # Update with prediction

        # Save predictions for this timestamp
        predictions.extend([{
            'Timestamp': last_timestamp,
            'Label': row['Label'],
            'CPU(t)': row['CPU(t)']
        } for row in predicted_row])

    # Create the result DataFrame
    result_df = pd.DataFrame(predictions)
    handle_output(result_df)
    return result_df

def mapping_number_pods( result_df, last_values):    
    # Step 1: Extract the last 11 rows from result_df and last_values
    last_11_result_df = result_df.tail(11)  # Get the last 11 rows
    
    # Step 2: Ensure both DataFrames have matching 'Label' for merging
    last_11_result_df = last_11_result_df.sort_values(by='Label').reset_index(drop=True)
    last_values = last_values.sort_values(by='Label').reset_index(drop=True)
    
    # Assuming 'current pod' column exists in last_values or can be calculated
    last_11_result_df['Current Pods'] = last_values['Current Pods']  # Replace 'current pod' with the actual column name
    
    df_mapping = pd.read_excel(output_file_path_limit_cpu)
    df_mapping['Label'] = df_mapping['Service Label'].map(service_mapping)

    label_to_limit_mapping = df_mapping.set_index('Label')['Limit per Pod'].to_dict()

    last_11_result_df.insert(
    last_11_result_df.columns.get_loc('Label') + 1,  # Position: After 'Label'
    'Service Name',  # Column name
    last_11_result_df['Label'].map({v: k for k, v in service_mapping.items()})  # Mapped values
    )

    last_11_result_df['Limit per Pod'] = last_11_result_df['Label'].map(label_to_limit_mapping)
    last_11_result_df['Predict Pods'] = (last_11_result_df['CPU(t)'] / last_11_result_df['Limit per Pod']).apply(np.ceil).astype(int)
    print(last_11_result_df)
    
def pred(end_timestamp):
    fn_df = load_last_data_metric(output_file_path_final)    
    result_df = predict_future_resources(last_timestamp, end_timestamp, fn_df, scaler, model_ann)
    mapping_number_pods(result_df, fn_df)

pred(end_timestamp_define)
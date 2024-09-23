import os 
import argparse
import numpy as np
import pandas as pd
from tqdm import tqdm
import nibabel as nib
from pyment.models import RegressionSFCN

def load_model(weights: str = 'brain-age-2022'):
    """Load the pre-trained RegressionSFCN model."""
    return(RegressionSFCN(weights))

def preprocess_image(wd_in:str): 
    """Preprocess T1w image."""
    img = nib.load(wd_in)
    img = img.get_fdata()
    img /= 255 #Normalize as in predict.py.
    img = np.expand_dims(img, 0)
    return(img)

def predict_age(model, img): 
    """Prediction of age from image."""
    prediction = model.predict(img, verbose=0)[0]
    return(model.postprocess(prediction))

def main(wd_in:str, wd_age:str):
    """Given preprocessed T1w image, predict the age.
    INPUTS: 
        - wd_in: folder path with preprocessed T1w.
        - wd_age: path to csv containing ID and age. Expected structure: 
            - 2 columns. 
            - One column named ID. 
            - One column named Age."""
    
    ref = pd.read_csv(wd_age) #Import clinical refference file.
    model = load_model() #Import model.
    predictions = [] #Define predictions.

    log_file = os.path.join(wd_in, 'log.txt') #Generate log file.
    #Read clinical support file.

    for imageid in tqdm(os.listdir(wd_in)):
        try:
            #Extract chronologic age from ID.
            name, _ = os.path.splitext(imageid)
            age = ref.loc[ref['ID'] == name, 'Age'].values[0]

            #Import, normalize and reshape preprocessed T1w. 
            wd_img = os.path.join(wd_in, imageid)
            img = preprocess_image(wd_img)

            #Predict biological age.
            prediction = predict_age(model, img)
            ae = abs(prediction-age)


            #Append to pandas.
            predictions.append({
                'imageid': imageid,
                'age':age,
                'prediction': prediction, 
                'absolute_error': ae
            })
        except Exception as e: 
            with open(log_file, "a") as log_file: 
                log_file.write(f"Error in file {imageid}:\t")
                log_file.write(str(e) + "\n")
            print(f"Error logged for {imageid}")
    
    #Generate prediction file.
    predictions = pd.DataFrame(predictions)
    predictions.to_csv(os.path.join(wd_in, "predict.csv"))
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Predict biological age of preprocessed T1w images using BrainAge (2022).')
    parser.add_argument('-i', '--input', help='Input directory containing preprocessed T1w files.', required=True)
    parser.add_argument('-r', '--ref', help='Path to clinical csv with ID and chronological age.', required=True)
    args = parser.parse_args()

    main(args.input, args.ref)






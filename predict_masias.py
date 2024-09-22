#PENDING: Add real age, code with main and correct subfunctions.
import os 
import numpy as np
import pandas as pd
from tqdm import tqdm
import nibabel as nib
from pyment.models import RegressionSFCN

model = RegressionSFCN(weights='brain-age-2022') #Seems like things have been moved around.

wd_in = '/home/mireia/Desktop/01_PreprocessedData'
predictions = []

for imageid in tqdm(os.listdir(wd_in)):
    path = os.path.join(wd_in, imageid)
    img = nib.load(path)
    img = img.get_fdata()
    
    img /= 255 #Normalize as in predict.py.
    img = np.expand_dims(img, 0)
    
    prediction = model.predict(img, verbose=0)[0]
    prediction = model.postprocess(prediction)
    predictions.append({
        'imageid': imageid,
        'prediction': prediction
    })

predictions = pd.DataFrame(predictions)
predictions.to_csv(os.path.join(wd_in, "predict.xlsx"))


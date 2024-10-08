import os 
import random
import argparse
import numpy as np
import pandas as pd
from tqdm import tqdm
import nibabel as nib
import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
from pyment.models import RegressionSFCN


def load_data(wd, data_set):
    X = []; y = []

    for i in range(len(data_set)): 
        name = data_set[i].split('.')[0]
        file = os.path.join(wd, data_set[i])

        try:
            age = df[df['ID'].str.strip() == name]['Age'].values[0]
            img = nib.load(file)
            img = img.get_fdata()/255

            y.append(age)
            X.append(img)

        except Exception as e: 
            print(f'Problems with ID {name}.')

    dataset = tf.data.Dataset.from_tensor_slices((X,y))        
    return(dataset)



wd = '/home/mireia/Desktop/01_BrainAge/03_FineTuning'
df = '/home/mireia/Desktop/01_BrainAge/demographics_HC.csv'
df = pd.read_csv(df, header=0)
imgs = os.listdir(wd)

#Log file analysis.
log = os.path.join(wd, "fine_tuning.txt")
f = open(log,"a")
f.write('Cases \t Training \t Validation \t Testing \n')
f.close()

#Parameters
unfreezed = 5
bs = 15
min_age = 0
max_age = 95
test_size = int(np.round(len(imgs)*0.25))


for imageid in range(test_size, len(imgs)-test_size,2): #We must leave at least one element out for validation.
    f = open(log, 'a')

    #Select cases to split.
    random.shuffle(imgs)
    imgs_train = imgs[:max(1,imageid)]
    imgs_val = imgs[imageid:imageid + test_size]
    imgs_test = imgs[-test_size:] 

    #Select biological age for these cases, and import data for training.
    train_dataset = load_data(wd, imgs_train)
    val_dataset = load_data(wd, imgs_val)
    test_dataset = load_data(wd, imgs_test)

    train_dataset = train_dataset.shuffle(buffer_size=50).batch(batch_size=bs).prefetch(buffer_size=tf.data.experimental.AUTOTUNE)
    val_dataset = val_dataset.batch(batch_size=bs)
    test_dataset = test_dataset.batch(batch_size=bs)


    # Import the model.
    model = RegressionSFCN(weights='brain-age-2022', prediction_range=(min_age, max_age))

    #Freeze necessary layers (Optional).
    if unfreezed: 
        for layer in model.layers[:-unfreezed]: 
            layer.trainable = False
        print(f'Freeze layers except {str(unfreezed)} last.')

    else: 
        print('No layers freezed in the process. Be careful with overfitting!')


    model.compile(optimizer=keras.optimizers.Adam(learning_rate=1e-3), loss='mean_absolute_error')
    history = model.fit(train_dataset, validation_data = val_dataset, epochs=5, batch_size=bs)
    
    # Access MAE for both training and validation
    train_mae = history.history['loss']
    val_mae = history.history['val_loss']
    test_loss = model.evaluate(test_dataset)

    # Reports saving. 
    cases = str(imageid+1)

    plt.figure()
    plt.plot(train_mae, label='Train MAE')
    plt.plot(val_mae, label='Validation MAE')
    plt.xlabel('Epochs')
    plt.ylabel('MAE')
    plt.title(f"Fine-tuned test MAE {str(np.round(test_loss,2))}")
    plt.legend()
    plt.savefig(os.path.join(wd,f'MAE_FineTune_{cases}.png'))

    train_mae = str(np.round(train_mae[-1],2))
    val_mae = str(np.round(val_mae[-1],2))
    test_mae = str(np.round(test_loss,2))

    f.write(f'{cases} \t {train_mae} \t {val_mae} \t {test_mae} \n')
    f.close()













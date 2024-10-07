from predict_masias import preprocess_image
from pyment.models import RegressionSFCN
from tensorflow.keras.models import Model
from tensorflow.keras import layers
import matplotlib.pyplot as plt
import tensorflow as tf
from tqdm import tqdm
import numpy as np
import scipy.ndimage
import os


def main(wd_in:str, wd_age:str=None):

    wd_in = '/home/mireia/Desktop/01_BrainAge/02_Preprocessed/'

    model = RegressionSFCN(weights='brain-age-2022')    
    grad_model = Model(inputs=model.inputs, outputs=[model.get_layer("sfcn-reg_block-1_relu").output, model.output])
    #grad_model = Model(inputs=model.inputs, outputs=[model.get_layer("sfcn-reg_top_relu").output, model.output])

    for imageid in tqdm(os.listdir(wd_in)):
        try:
            #Import, normalize and reshape preprocessed T1w. 
            wd_img = os.path.join(wd_in, imageid)
            img = preprocess_image(wd_img)

            #Make the prediction and extract last layer maps.
            with tf.GradientTape() as tape:
                 map, out = grad_model(img)
                 tape.watch(map)

            grads = tape.gradient(out, map)
            pooled_grads = tf.reduce_mean(grads, axis=(1,2,3))
            heatmap = tf.reduce_sum(tf.multiply(pooled_grads, map), axis=-1)
            heatmap = layers.Activation('relu')(heatmap) #Only positive values.
        
            #Resize. 
            new_size = img.shape
            zoom_factors = (1, new_size[1] / heatmap.shape[1], new_size[2] / heatmap.shape[2], new_size[3] / heatmap.shape[3])  #Keep the channels unchanged
            heatmap = scipy.ndimage.zoom(heatmap, zoom_factors, order=1)

 
            plt.figure(dpi = 200); idx = 80
            plt.imshow(np.rot90(img[0,:,:,idx]), cmap='gray')
            plt.imshow(np.rot90(heatmap[0,:,:,idx]), cmap = 'jet', alpha = 0.5)
            plt.axis('off'); 
            plt.show()

        except: 
            print('Error in excecution of subject {}'.format(str(imageid)))
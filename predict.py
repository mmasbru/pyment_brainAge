import os
import yaml

batch_size = 2
threads = 4

config='config.yaml'

with open(config) as y_file:
    proj_parameters = yaml.safe_load(y_file)

y_file.close()

dataset_folder = proj_parameters['oDir']
dataset_folder = os.path.join(dataset_folder, 'cropped')

from pyment.data import AsyncNiftiGenerator, NiftiDataset

dataset = NiftiDataset.from_folder(dataset_folder, target='age')

# Set up a preprocessor to normalize the voxel values
preprocessor = lambda x: x/255

generator = AsyncNiftiGenerator(dataset, preprocessor=preprocessor, 
                                batch_size=batch_size, threads=threads)


from pyment.models import RegressionSFCN

model = RegressionSFCN(weights='brain-age')

generator.reset()

preds, labels = model.predict(generator, return_labels=True)

import numpy as np

preds = preds.squeeze()
mae = np.mean(np.abs(preds - labels))

np.savetxt('/home/genr/queues/pyment/genr/pyment_predictions.csv', preds, delimiter=',')
np.savetxt('/home/genr/queues/pyment/genr/labelsPyment.csv', labels, delimiter=',')


#print(preds)
print('mae', mae)


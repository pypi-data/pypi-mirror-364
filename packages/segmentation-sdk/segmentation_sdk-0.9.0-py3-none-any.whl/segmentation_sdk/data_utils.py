import keras
import cv2
import numpy as np
import os
from sklearn.model_selection import train_test_split

def get_data_generators(df, params):

    data = extract_split(df)

    train_generator = DataGenerator(data['train']['images'], data['train']['masks'], batch_size=params['BATCH_SIZE'], shuffle=True, augment=True, image_size=params['IMAGE_SIZE'], input_depth=params['INPUT_DEPTH'])
    dev_generator = DataGenerator(data['dev']['images'], data['dev']['masks'], batch_size=params['BATCH_SIZE'], shuffle=False, augment=False, image_size=params['IMAGE_SIZE'], input_depth=params['INPUT_DEPTH'])
    test_generator = DataGenerator(data['test']['images'], data['test']['masks'], batch_size=params['BATCH_SIZE'], shuffle=False, augment=False, image_size=params['IMAGE_SIZE'], input_depth=params['INPUT_DEPTH'])
    
    return train_generator, dev_generator, test_generator

def extract_split(df):

    data = {}
    for split in ['train', 'dev', 'test']:
        data[split] = {}
        df_split = df[df['split'] == split]        
        data[split]['images'] = list(df_split['img'])
        data[split]['masks'] = list(df_split['mask'])
        
    return data

def get_paths(paths):
    
    images, masks = list(zip(*paths))
    
    return list(images), list(masks)

def split_data(images_paths, masks_paths, test_size=0.1, dev_size=0.1, random_seed=42):
    
    paths = [x for x in zip(images_paths, masks_paths)]
    
    paths_train_dev, paths_test = train_test_split(paths, test_size=test_size, random_state=random_seed)
    paths_train, paths_dev = train_test_split(paths_train_dev, test_size=dev_size, random_state=random_seed)
    
    images_paths_train, masks_paths_train = get_paths(paths_train)
    images_paths_dev, masks_paths_dev = get_paths(paths_dev)
    images_paths_test, masks_paths_test = get_paths(paths_test)
    
    ret= {'train':{'images': images_paths_train, 'masks': masks_paths_train},
          'dev':{'images':images_paths_dev, 'masks': masks_paths_dev},
          'test':{'images':images_paths_test, 'masks': masks_paths_test}}
    
    return ret

def rotate_image(image, angle, translation=None):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    if translation is not None:
        rot_mat[0][2] += translation[0]
        rot_mat[1][2] += translation[1]
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result

class DataGenerator(keras.utils.Sequence):
    def __init__(self, images_paths, masks_paths, batch_size, shuffle=False, augment=False, image_size=None, input_depth=1, augment_probability=0.98):
        
        assert len(images_paths) == len(masks_paths)
        self.batch_size = batch_size        
        self.elements = list(zip(images_paths, masks_paths))
        self.length = len(self.elements)
        self.shuffle = shuffle
        self.augment = augment
        self.on_epoch_end()
        self.input_depth = input_depth
        self.image_size = image_size
        self.augment_probability = augment_probability

    def on_epoch_end(self):
        if self.shuffle:
            np.random.shuffle(self.elements)
  
    def load_image(self, filepath, read_grayscale=False):
        if read_grayscale:
            img = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
        else:
            img = cv2.imread(filepath)
        return img
    
    def __len__(self):
        return self.length//self.batch_size
    
    def _get_batch_elements(self, index):
        batch_index_start = index*self.batch_size
        batch_index_end = min((index+1)*self.batch_size, self.length)
        return self.elements[batch_index_start:batch_index_end]
    
    def load_images(self, paths):
        return [self.load_image(path) for path in paths]
    
    def __getitem__(self, index):
        
        batch_elements = self._get_batch_elements(index)
        
        images_batch = []
        masks_batch = []
        
        for x in batch_elements:
            img = self.load_image(x[0])
            msk = self.load_image(x[1], read_grayscale=True)
            
            if self.image_size:
                img=cv2.resize(img, (self.image_size[1], self.image_size[0]))
                msk=cv2.resize(msk, (self.image_size[1], self.image_size[0]), interpolation = cv2.INTER_NEAREST)
                #msk = (msk+0.5).astype(np.int32).astype(np.float32)
                msk = msk.astype(np.uint8)
            
            msk = msk.astype(np.float32)
            img = (img/255.0).astype(np.float32)
            
            if self.augment:
                if np.random.uniform(0, 1) < self.augment_probability:
                    
                    # transform
                    #angle = np.random.uniform(0, 360)
                    #translation = np.random.uniform(-80, 80, size=(2))
                    #img = rotate_image(img, angle, translation)
                    #msk = rotate_image(msk, angle, translation)
                    #msk = (msk+0.5).astype(np.int32).astype(np.float32)
                    
                    # flip
                    if np.random.uniform(0, 1) < 0.5:
                        img = cv2.flip(img, 0)
                        msk = cv2.flip(msk, 0)

                    # flop
                    if np.random.uniform(0, 1) < 0.5:
                        img = cv2.flip(img, 1)
                        msk = cv2.flip(msk, 1)
                          
                    # brightness and contrast
                    contrast = np.random.uniform(0.9, 1.1)
                    img = img * contrast
                    brightness = np.random.uniform(-0.1, 0.1)
                    img = img + brightness
                    img = np.minimum(np.maximum(img, 0.0), 1.0)

            images_batch.append(img)
            masks_batch.append(msk)
            
        masks_batch = np.array(masks_batch)
        images_batch = np.array(images_batch)

        masks_batch = np.expand_dims(masks_batch, axis=-1)
        #images_batch = np.expand_dims(images_batch, axis=-1)
        #images_batch = np.repeat(images_batch, self.input_depth, axis=3)
        
        return images_batch, masks_batch#, np.full(masks_batch.shape, 0.0)
        

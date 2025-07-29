import keras
import cv2
import numpy as np
import os
from sklearn.model_selection import train_test_split
 
class DataGenerator(keras.utils.Sequence):
    def __init__(self, images_paths, masks_paths, batch_size, shuffle=False, augment=False, image_size=None, input_depth=1, augment_probability=0.98):
        assert len(images_paths) == len(masks_paths), "Mismatch between number of images and masks"
        self.batch_size = batch_size
        self.elements = list(zip(images_paths, masks_paths))
        self.length = len(self.elements)
        self.shuffle = shuffle
        self.augment = augment
        self.image_size = image_size
        self.input_depth = input_depth
        self.augment_probability = augment_probability
        self.on_epoch_end()
 
    def on_epoch_end(self):
        if self.shuffle:
            np.random.shuffle(self.elements)
 
    def __len__(self):
        return max(1, self.length // self.batch_size)
 
    def _get_batch_elements(self, index):
        start = index * self.batch_size
        end = min((index + 1) * self.batch_size, self.length)
        return self.elements[start:end]
 
    def load_image(self, filepath, read_grayscale=False):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        flag = cv2.IMREAD_GRAYSCALE if read_grayscale else cv2.IMREAD_COLOR
        img = cv2.imread(filepath, flag)
        if img is None:
            raise ValueError(f"cv2 failed to read image: {filepath}")
        return img
 
    def __getitem__(self, index):
        batch_elements = self._get_batch_elements(index)
        images_batch = []
        masks_batch = []
        for img_path, mask_path in batch_elements:
            img = self.load_image(img_path)
            msk = self.load_image(mask_path, read_grayscale=True)
            if self.image_size:
                img = cv2.resize(img, (self.image_size[1], self.image_size[0]))
                msk = cv2.resize(msk, (self.image_size[1], self.image_size[0]), interpolation=cv2.INTER_NEAREST)
 
            msk = msk.astype(np.uint8).astype(np.float32)
            img = (img / 255.0).astype(np.float32)
 
            if self.augment and np.random.uniform(0, 1) < self.augment_probability:
                if np.random.rand() < 0.5:
                    img = cv2.flip(img, 0)
                    msk = cv2.flip(msk, 0)
                if np.random.rand() < 0.5:
                    img = cv2.flip(img, 1)
                    msk = cv2.flip(msk, 1)
                contrast = np.random.uniform(0.9, 1.1)
                brightness = np.random.uniform(-0.1, 0.1)
                img = np.clip(img * contrast + brightness, 0.0, 1.0)
 
            if self.input_depth == 1 and img.ndim == 3:
                img = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
                img = np.expand_dims(img, axis=-1)
            elif self.input_depth == 3 and img.ndim == 2:
                img = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_GRAY2BGR).astype(np.float32) / 255.0
 
            images_batch.append(img)
            masks_batch.append(msk)
 
        images_batch = np.array(images_batch)
        masks_batch = np.expand_dims(np.array(masks_batch), axis=-1)
        return images_batch, masks_batch
 
def extract_split(df, zip_folder_name):
    data = {}
    for split in ['train', 'dev', 'test']:
        data[split] = {'images': [], 'masks': []}
        df_split = df[df['split'] == split]
        for _, row in df_split.iterrows():
            img_path = os.path.join(zip_folder_name, row['img'])
            mask_path = os.path.join(zip_folder_name, row['mask'])
            data[split]['images'].append(img_path)
            data[split]['masks'].append(mask_path)
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
    return {
        'train': {'images': images_paths_train, 'masks': masks_paths_train},
        'dev': {'images': images_paths_dev, 'masks': masks_paths_dev},
        'test': {'images': images_paths_test, 'masks': masks_paths_test}
    }
 
def rotate_image(image, angle, translation=None):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    if translation is not None:
        rot_mat[0][2] += translation[0]
        rot_mat[1][2] += translation[1]
    return cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
 
def get_data_generators(df, params):
    zip_folder_name = params.get('ZIP_FOLDER_NAME', '')  # You must pass this in your params dictionary
    data = extract_split(df, zip_folder_name)
 
    train_generator = DataGenerator(
        data['train']['images'], data['train']['masks'],
        batch_size=params['BATCH_SIZE'], shuffle=True, augment=True,
        image_size=params['IMAGE_SIZE'], input_depth=params['INPUT_DEPTH']
    )
    dev_generator = DataGenerator(
        data['dev']['images'], data['dev']['masks'],
        batch_size=params['BATCH_SIZE'], shuffle=False, augment=False,
        image_size=params['IMAGE_SIZE'], input_depth=params['INPUT_DEPTH']
    )
    test_generator = DataGenerator(
        data['test']['images'], data['test']['masks'],
        batch_size=params['BATCH_SIZE'], shuffle=False, augment=False,
        image_size=params['IMAGE_SIZE'], input_depth=params['INPUT_DEPTH']
    )
    return train_generator, dev_generator, test_generator
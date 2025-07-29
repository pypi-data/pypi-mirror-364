import tensorflow as tf
from . import viz_utils
import os
import cv2
import shutil
import json
from keras.callbacks import CSVLogger
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from neuroedge_sdk.tracking_model import TrackModel

def log_results(experiment_name, records):
        
    with TrackModel(experiment_name=experiment_name) as ml_logger:
        for record in records:
            if record['type'] == 'param':
                ml_logger.log_param(record['name'], record['value'])
            elif record['type'] == 'metric':
                ml_logger.log_metric(record['name'], record['value'])
            elif record['type'] == 'artifact':
                ml_logger.log_artifact(record['filepath'])
            else:
                raise Exception('Result type unknown.')


def save_metrics(metrics, artifacts_dir):

    with open(os.path.join(artifacts_dir, 'metrics.json'), "w") as outfile:
        outfile.write(json.dumps(metrics))

def train(directory, model, train_generator, dev_generator, params):
    
    ret_data = []
    
    os.makedirs(directory, exist_ok=True)
    train_artifacts_dir = os.path.join(directory, 'artifacts', 'train')
    os.makedirs(train_artifacts_dir, exist_ok=True)
    
    code_dir = os.path.join(directory, 'code')
    os.makedirs(code_dir, exist_ok=True)
    shutil.copytree("./", code_dir, dirs_exist_ok=True)

    #metadata = {'comment': params['COMMENT']}
    #metadata_filepath = os.path.join(directory, 'metadata.json')
    #with open(metadata_filepath, 'w') as f:
    #    json.dump(metadata, f)
    
    filepath = os.path.join(train_artifacts_dir, 'cp.weights.h5')
    ret_data.append({'type': 'artifact', 'filepath': filepath})
    cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=filepath,
                                                     save_weights_only=True,
                                                     save_best_only=True,
                                                     monitor='val_loss',
                                                     verbose=1)
    #es_callback = tf.keras.callbacks.EarlyStopping(patience=100, monitor='val_loss')

    csv_logger = CSVLogger(os.path.join(directory, 'log.csv'), append=True, separator=';')

    _ = model.fit(
        train_generator,
        validation_data = dev_generator,
        epochs=params['NUM_EPOCHS'],
        callbacks=[cp_callback, csv_logger],
        verbose=1
    )
    
    df = pd.read_csv(os.path.join(directory, "log.csv"), delimiter=';')
    
    filepath = save_train_plot(df, train_artifacts_dir)
    ret_data.append({'type': 'artifact', 'filepath': filepath})
    metrics = get_train_metrics(df, train_artifacts_dir)
    for metric_key in metrics.keys():
        ret_data.append({'type': 'metric', 'name': '{}'.format(metric_key), 'value': metrics[metric_key]})
    #save_metrics(metrics, train_artifacts_dir)

    return ret_data

def save_train_plot(df, train_artifacts_dir):

    fig, ax = plt.subplots(figsize=(8,4))

    for key in ['loss', 'val_loss']:
        ax.plot(df['epoch'], df[key], label=key)

    plt.legend(loc='upper right')
    plt.xlabel("epoch", fontsize=12)
    plt.ylabel("loss", fontsize=12)
    plt.grid()
    fig.tight_layout()
    plt.close()

    image = viz_utils.get_plt_canvas(fig)
    image = image[:,:,1:4]
    image = np.flip(image,axis=2)
    #jcv2.imshow("image", image)
    filepath = os.path.join(train_artifacts_dir, 'training_plot.png')
    cv2.imwrite(filepath, image)
    
    return filepath

def get_train_metrics(df, train_artifacts_dir):
    
    best_epoch_idx = np.argmin(list(df['val_loss']))
    tmp_metrics = df.iloc[best_epoch_idx].to_dict()

    metrics = {
      #'best_epoch': int(tmp_metrics['epoch']),
      'train/loss': tmp_metrics['loss'],
      'dev/loss': tmp_metrics['val_loss'],
      'train/accuracy': tmp_metrics['sparse_categorical_accuracy'],
      'dev/accuracy': tmp_metrics['val_sparse_categorical_accuracy'],   
    }
                
    return metrics
     
def get_metrics(masks_test, preds_test, class_names):

    metrics = {}

    accuracy = np.sum(preds_test == masks_test)/np.prod(preds_test.shape)
    metrics['all'] = {}
    metrics['all']['accuracy'] = accuracy

    for category in class_names:
        class_idx = category['id']
        name = category['name']
        pred = (preds_test == class_idx).astype(np.float32)
        mask = (masks_test == class_idx).astype(np.float32)

        intersection = np.logical_and(pred, mask).sum()
        union = np.logical_or(pred, mask).sum()
        mask_sum = np.sum(mask)
        pred_sum = np.sum(pred)
        recall = intersection / (mask_sum + 1e-6)
        precision = intersection / (pred_sum + 1e-6)
        iou = intersection / (union + 1e-6)

        if name not in metrics:
            metrics[name]= {}

        metrics[name]['recall'] = recall
        metrics[name]['precision'] = precision 
        if recall == 0.0 and precision==0.0:
            f1 = 0.0
        else:
            f1 = 2*precision*recall/(precision+recall)
        metrics[name]['f1'] = f1
        metrics[name]['iou'] = iou
    
    return metrics

def get_confusion_matrix(masks_test, preds_test, class_names):

    preds_test_flatten = preds_test.reshape(-1)
    masks_test_flatten = masks_test.reshape(-1)

    cm = confusion_matrix(masks_test_flatten, preds_test_flatten, labels=list(range(len(class_names))))
    return cm

def save_confusion_matrix(cm, test_artifacts_dir, class_names, normalized):

    if normalized:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    fig, ax = plt.subplots(figsize=(14,14))
    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    #ax.figure.colorbar(im, ax=ax)

    if normalized:
        title = 'Normalized Confusion Matrix [%]'
    else:
        title = 'Confusion Matrix'
    plt.title(title, fontsize=18)
    plt.xlabel('Predicted label', fontsize=16)
    plt.ylabel('True label', fontsize=16)

    plt.xticks(np.arange(cm.shape[1]),class_names, fontsize=14, rotation=90)
    plt.yticks(np.arange(cm.shape[0]),class_names, fontsize=14)

    #plt.setp(ax.get_xticklabels(), rotation=90, ha="right",rotation_mode="anchor")

    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            if normalized:
                text = '{:.1f}'.format(float(cm[i, j])*100.0)
                size=16
            else:
                text = '{:d}'.format(int(cm[i, j]))
                size=10
            ax.text(j, i, text,
                    ha="center", va="center", size=size,
                    color="white" if cm[i, j] > thresh else "black")
    fig.tight_layout()
    plt.close()

    image = viz_utils.get_plt_canvas(fig)
    image = image[:,:,1:4]
    image = np.flip(image,axis=2)
    #jcv2.imshow("image", image)
    if normalized:
        filename = 'confusion_matrix_normalized.png'
    else:
        filename = 'confusion_matrix.png'
    filepath = os.path.join(test_artifacts_dir, filename)
    cv2.imwrite(filepath, image)
    return filepath
    
def save_examples(test_artifacts_dir, images_test, masks_test, preds_test, params, metadata, select_num_samples):

    filepaths = []
    test_examples_dir = os.path.join(test_artifacts_dir, 'examples')
    os.makedirs(test_examples_dir, exist_ok=True)

    COLORS = viz_utils.get_class_colors(params['NUM_CLASSES'])

    num_examples = preds_test.shape[0]
    np.random.seed(42)
    IDXS = list(np.random.choice(list(range(num_examples)), select_num_samples))
    for idx in IDXS:
        pred = preds_test[idx]
        mask = masks_test[idx]
        img = images_test[idx]*255.0

        mask = COLORS[mask[:,:,0].astype(np.int32)]
        pred = COLORS[pred[:,:,0].astype(np.int32)]

        img = viz_utils.pad_with_text(img, 'image')
        mask = viz_utils.pad_with_text(mask, 'mask')
        pred = viz_utils.pad_with_text(pred, 'prediction')

        x = np.concatenate([img, pred, mask], axis=1)
        #x = cv2.resize(x, None, fx=2.0, fy=2.0, interpolation = cv2.INTER_NEAREST)

        #text = 'idx={:d}'.format(idx)
        #utils.viz_img(x, text, None)
        filepath = os.path.join(test_examples_dir, 'example_{:d}.png'.format(idx))
        cv2.imwrite(filepath, x)
        filepaths.append(filepath)

    class_names_img = viz_utils.get_class_names_img(metadata['class_names'], COLORS)
    #jcv2.imshow("class_names", class_names_img)
    filepath = os.path.join(test_examples_dir, 'color_mapping.png')
    cv2.imwrite(filepath, class_names_img)
    filepaths.append(filepath)
    
    return filepaths

def get_preds(test_generator, model, params):

    test_data = []
    for idx in range(test_generator.__len__()):
        x = test_generator.__getitem__(idx)
        test_data.append(x)

    images_test = np.concatenate([x[0] for x in test_data], axis=0)
    masks_test = np.concatenate([x[1] for x in test_data], axis=0)

    preds_test = []
    for i in range(0, images_test.shape[0], params['BATCH_SIZE']):
        x= images_test[i:i+params['BATCH_SIZE']]
        y = model.predict(x, verbose=0)
        y = np.argmax(y, axis=-1, keepdims=True)
        preds_test.append(y)
    preds_test = np.concatenate(preds_test, axis=0)
        
    #masks_logits = model.predict(images_test, batch_size=params['BATCH_SIZE'])
    #preds_test = np.argmax(masks_logits, axis=-1, keepdims=True)
    
    #print(images_test.shape, masks_test.shape, preds_test.shape)
    
    return images_test, masks_test, preds_test

def test(directory, test_generator, model, params, metadata):
    
    ret_data = []
    images_test, masks_test, preds_test = get_preds(test_generator, model, params)
    
    test_artifacts_dir = os.path.join(directory, 'artifacts', 'test')
    os.makedirs(test_artifacts_dir, exist_ok=True)
            
    metrics = get_metrics(masks_test, preds_test, metadata['class_names'])
    for class_key in metrics.keys():
        
        for metric_key in metrics[class_key].keys():
            ret_data.append({'type': 'metric', 'name': '{}/{}'.format(class_key, metric_key), 'value': metrics[class_key][metric_key]})
    #save_metrics(metrics, test_artifacts_dir)
    
    class_names = [x['name'] for x in metadata['class_names']]
    cm = get_confusion_matrix(masks_test, preds_test, class_names)
    filepath = save_confusion_matrix(cm, test_artifacts_dir, class_names, normalized=True)
    ret_data.append({'type': 'artifact', 'filepath': filepath})
    filepath = save_confusion_matrix(cm, test_artifacts_dir, class_names, normalized=False)
    ret_data.append({'type': 'artifact', 'filepath': filepath})
    
    filepaths = save_examples(test_artifacts_dir, images_test, masks_test, preds_test, params, metadata, select_num_samples = 5)
    for filepath in filepaths:
        ret_data.append({'type': 'artifact', 'filepath': filepath})
        
    return ret_data
    
    
    
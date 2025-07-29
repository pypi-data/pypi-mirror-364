from tensorflow.keras.applications import ResNet50
import tensorflow as tf
from tensorflow.keras import layers, Model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, UpSampling2D, Input, concatenate
from tensorflow_examples.models.pix2pix import pix2pix
import keras

def get_model(params):
    
    input_shape = params['IMAGE_SIZE'] + [params['INPUT_DEPTH']]

    if params['MODEL'] == 'mobilenetv2_unet':
        model = mobilenetv2_unet(input_shape=input_shape, output_channels=params['NUM_CLASSES'])
    elif params['MODEL'] == 'deeplabv3plus_resnet':
        model = deeplabv3plus_resnet(input_shape=input_shape, num_classes=params['NUM_CLASSES'])
    else:
        raise Exception('Model not implemented.')
    
    if 'OPTIMIZER' in params:
        if params['OPTIMIZER'] == 'adam':
            optimizer=tf.keras.optimizers.Adam(learning_rate=params['LEARNING_RATE'])    
        else:
            raise Exception('Model not implemented.')
    else:
        optimizer=tf.keras.optimizers.SGD(0.001)#None

    model.compile(optimizer=optimizer,
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=[keras.metrics.SparseCategoricalAccuracy()])
    
    return model

def crop(x, dx, dy):

    dx_start, dx_end = 0, x.shape[1]
    dy_start, dy_end = 0, x.shape[2]
    
    if dx>0:
        dx_start = 0 + int(dx/2)
        dx_end = dx_end - int(dx/2)  
        if dx%2==1:
            dx_end = dx_end  - 1 
    if dy>0:
        dy_start = 0 + int(dy/2)
        dy_end = dy_end - int(dy/2)  
        if dy%2==1:
            dy_end = dy_end  - 1 
    x = x[:, dx_start:dx_end, dy_start:dy_end] 
    
    return x

def mobilenetv2_unet(input_shape, output_channels):

    base_model = tf.keras.applications.MobileNetV2(input_shape=input_shape, include_top=False)

    # Use the activations of these layers
    layer_names = [
        'block_1_expand_relu',   # 64x64
        'block_3_expand_relu',   # 32x32
        'block_6_expand_relu',   # 16x16
        'block_13_expand_relu',  # 8x8
        'block_16_project',      # 4x4
    ]
    base_model_outputs = [base_model.get_layer(name).output for name in layer_names]

    # Create the feature extraction model
    down_stack = tf.keras.Model(inputs=base_model.input, outputs=base_model_outputs)

    down_stack.trainable = False

    up_stack = [
        pix2pix.upsample(512, 3),  # 4x4 -> 8x8
        pix2pix.upsample(256, 3),  # 8x8 -> 16x16
        pix2pix.upsample(128, 3),  # 16x16 -> 32x32
        pix2pix.upsample(64, 3),   # 32x32 -> 64x64
    ]

    inputs = tf.keras.layers.Input(shape=input_shape)

    # Downsampling through the model
    skips = down_stack(inputs)
    x = skips[-1]
    skips = reversed(skips[:-1])

    # Upsampling and establishing the skip connections
    for up, skip in zip(up_stack, skips):
        x = up(x)
        concat = tf.keras.layers.Concatenate()

        dx = x.shape[1] - skip.shape[1]
        dy = x.shape[2] - skip.shape[2]
        
        x = crop(x, dx, dy)   
        x = concat([x, skip])

    # This is the last layer of the model
    last = tf.keras.layers.Conv2DTranspose(
      filters=output_channels, kernel_size=3, strides=2,
      padding='same')  #64x64 -> 128x128

    x = last(x)

    return tf.keras.Model(inputs=inputs, outputs=x)

def deeplabv3plus_resnet(input_shape, num_classes):
    inputs = tf.keras.Input(shape=input_shape)

    # Backbone: ResNet50
    backbone = ResNet50(input_tensor=inputs, include_top=False, weights="imagenet")

    # Low-level features
    low_level_features = backbone.get_layer("conv2_block3_out").output
    low_level_features = layers.Conv2D(48, 1, padding="same", activation="relu")(low_level_features)

    # Backbone output
    backbone_output = backbone.output
    x = layers.Conv2D(480, 1, padding="same", activation="relu")(backbone_output)
    x = layers.UpSampling2D(size=(8, 8), interpolation="bilinear")(x)

    # Concatenate and refine
    dx = x.shape[1] - low_level_features.shape[1]
    dy = x.shape[2] - low_level_features.shape[2]
    x = crop(x, dx, dy)
            
    x = layers.Concatenate()([x, low_level_features])
    x = layers.Conv2D(480, 3, padding="same", activation="relu")(x)
    x = layers.Conv2D(480, 3, padding="same", activation="relu")(x)
    x = layers.UpSampling2D(size=(4, 4), interpolation="bilinear")(x)

    #outputs = layers.Conv2D(num_classes, 1, activation="sigmoid")(x)
    outputs = layers.Conv2D(num_classes, 1)(x)
    return Model(inputs, outputs)

def dice_loss(y_true, y_pred):    
    smooth = 1.0
    y_true_f = tf.keras.backend.flatten(y_true)
    y_pred_f = tf.keras.backend.flatten(y_pred)
    intersection = tf.keras.backend.sum(y_true_f * y_pred_f)
    return 1 - (2. * intersection + smooth) / (tf.keras.backend.sum(y_true_f) + tf.keras.backend.sum(y_pred_f) + smooth)

def dice_loss_multilabel(y_true, y_pred, number_of_classes=1):
    dice = 0
    for index in range(number_of_classes):
        dice += dice_loss(y_true[:,:,:,index], y_pred[:,:,:,index])
    return dice
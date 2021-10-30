from keras.applications.inception_v3 import InceptionV3
from keras.applications.inception_resnet_v2 import InceptionResNetV2
from keras.preprocessing import image
from keras.layers import Dense,GlobalAveragePooling2D,BatchNormalization
from keras import applications
from keras.preprocessing.image import ImageDataGenerator
from keras import optimizers
from keras import backend as K
from keras.models import Sequential, Model
import numpy as np


def feature_extraction_InV3(img_width, img_height,
                        train_data_dir,
                        num_image,
                        epochs):
    base_model = InceptionV3(input_shape=(299, 299, 3),
                              weights='imagenet', include_top=False)
    x = base_model.output
    x = GlobalAveragePooling2D()(x)

    model = Model(inputs=base_model.input, outputs=x)


    train_generator = ImageDataGenerator(rescale=1. / 255).flow_from_directory(train_data_dir,
    target_size = (299, 299),
    batch_size = 15,
    class_mode = "categorical",
    shuffle=False)

    y_train=train_generator.classes
    y_train1 = np.zeros((num_image, 4))
    y_train1[np.arange(num_image), y_train] = 1

    train_generator.reset
    X_train=model.predict(train_generator,verbose=1)
    print (X_train.shape,y_train1.shape)
    return X_train,y_train1,model

def feature_extraction_InRNV2(img_width, img_height,
                        train_data_dir,
                        num_image,
                        epochs):
    base_model = InceptionResNetV2(input_shape=(img_width, img_height, 3),
                              weights='imagenet', include_top=False)
    x = base_model.output
    x = GlobalAveragePooling2D()(x)

    model = Model(inputs=base_model.input, outputs=x)

    model.save('InRNV2_'+str(img_height)+'.h5')

    train_generator = ImageDataGenerator(rescale=1. / 255).flow_from_directory(train_data_dir,
    target_size = (img_width, img_height),
    batch_size = 15,
    class_mode = "categorical",
    shuffle=False)

    y_train=train_generator.classes
    y_train1 = np.zeros((num_image, 4))
    y_train1[np.arange(num_image), y_train] = 1

    train_generator.reset
    X_train=model.predict(train_generator,verbose=1)
    print (X_train.shape,y_train1.shape)
    return X_train,y_train1,model

def train_last_layer_InRNV2(img_width, img_height,
                        train_data_dir,
                        num_image,
                        epochs = 50):
    X_train,y_train,model=feature_extraction_InRNV2(img_width, img_height,
                            train_data_dir,
                            num_image,
                            epochs)
    my_model = Sequential()
    my_model.add(BatchNormalization(input_shape=X_train.shape[1:]))
    my_model.add(Dense(1024, activation = "relu"))
    my_model.add(Dense(4, activation='softmax')) #number of neurons equals number of classes
    my_model.compile(optimizer="SGD", loss='categorical_crossentropy',metrics=['accuracy'])
    #early = EarlyStopping(monitor='val_loss', min_delta=0, patience=10, verbose=1, mode='auto')
    my_model.fit(X_train, y_train,epochs=88,batch_size=30,verbose=1)
    return my_model

def train_last_layer_InV3(img_width, img_height,
                        train_data_dir,
                        num_image,
                        epochs = 50):
    X_train,y_train,model=feature_extraction_InV3(img_width, img_height,
                            train_data_dir,
                            num_image,
                            epochs)
    my_model = Sequential()
    my_model.add(BatchNormalization(input_shape=X_train.shape[1:]))
    my_model.add(Dense(1024, activation = "relu"))
    my_model.add(Dense(4, activation='softmax'))
    my_model.compile(optimizer="SGD", loss='categorical_crossentropy',metrics=['accuracy'])
    #early = EarlyStopping(monitor='val_loss', min_delta=0, patience=10, verbose=1, mode='auto')
    my_model.fit(X_train, y_train,epochs=18,batch_size=30,verbose=1)
    return my_model

if __name__=="__main__":
    img_width=499
    img_height = 499
    train_data_dir = "../test"
    num_image=1800
    epochs = 10
    model=train_last_layer_InRNV2(img_width, img_height,
                            train_data_dir,
                            num_image,epochs)

    model.save('InRNV2_last_layer_'+str(img_height)+'.h5')

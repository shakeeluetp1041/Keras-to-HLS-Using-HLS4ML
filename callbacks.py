'''
Created on 7 Apr 2017

@author: jkiesele
'''

import json

# loss per epoch
from time import time

from tensorflow.keras.callbacks import Callback, ModelCheckpoint,ReduceLROnPlateau,EarlyStopping,TensorBoard,History

#from tensorflow.keras.callbacks import Callback, EarlyStopping, History, ReduceLROnPlateau, TensorBoard
class newline_callbacks_begin(Callback):
    def __init__(self, outputDir):
        self.outputDir = outputDir
        self.loss = []
        self.val_loss = []
        self.full_logs = []
        import os
       # Create directory if not exists
        if not os.path.exists(self.outputDir):
            os.makedirs(self.outputDir)


    def on_epoch_end(self, epoch, epoch_logs={}):  # noqa: B006
        import os
        lossfile = os.path.join(self.outputDir, 'losses.log')
        print('\n***callbacks***\nsaving losses to ' + lossfile)
        self.loss.append(epoch_logs.get('loss'))
        self.val_loss.append(epoch_logs.get('val_loss'))
        f = open(lossfile, 'w')
        for i in range(len(self.loss)):
            f.write(str(self.loss[i]))
            f.write(" ")
            f.write(str(self.val_loss[i]))
            f.write("\n")
        f.close()
        normed = {}
        for vv in epoch_logs:
            normed[vv] = float(epoch_logs[vv])
        self.full_logs.append(normed)
        lossfile = os.path.join(self.outputDir, 'full_info.log')
        with open(lossfile, 'w') as out:
            out.write(json.dumps(self.full_logs))

class newline_callbacks_end(Callback):
    def on_epoch_end(self, epoch, epoch_logs={}):  # noqa: B006
        print('\n***callbacks end***\n')

class Losstimer(Callback):
    def __init__(self, every=5):
        self.points = []
        self.every = every

    def on_train_begin(self, logs):
        self.start = time()
        print("TRAIN EPOCH TIME STARTED")

    def on_batch_end(self, batch, logs):
        if (batch % self.every) != 0:
            return
        elapsed = time() - self.start
        cop = {}
        for i, j in logs.items():
            cop[i] = float(j)
        cop['elapsed'] = elapsed
        self.points.append(cop)

class all_callbacks:
    def __init__(self, stop_patience=5, lr_factor=0.5, lr_patience=2, 
        lr_epsilon=0.001, lr_cooldown=1, lr_minimum=1e-5, outputDir=''):
        self.nl_begin = newline_callbacks_begin(outputDir)
        self.modelbestcheck = ModelCheckpoint(outputDir + "/KERAS_check_best_model.h5", monitor='val_loss', verbose=1, save_best_only=True)
        self.reduce_lr = ReduceLROnPlateau(
            monitor='val_loss',
            factor=lr_factor,
            patience=lr_patience,
            mode='min',
            verbose=1,
            epsilon=lr_epsilon,
            cooldown=lr_cooldown,
            min_lr=lr_minimum,
        )
        self.nl_end = newline_callbacks_end()
        self.stopping = EarlyStopping(monitor='val_loss', patience=stop_patience, verbose=1, mode='min')
        self.tb = TensorBoard(log_dir=outputDir + '/logs')
        self.history = History()
        self.timer = Losstimer()
        self.callbacks_list = [self.nl_begin,self.modelbestcheck,
                               self.reduce_lr,self.stopping,self.nl_end,
                               self.tb,self.history,self.timer]
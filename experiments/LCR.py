from artiq.experiment import *
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

class LCR(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.sampler = self.get_device("sampler0")
        self.LCR=self.get_device("zotino0")
        self.setattr_argument("Voltage", NumberValue(default=0))

        self.sample = [0.0]*8

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()

        self.LCR.init()
        self.sampler.init()

        delay(1000*ms)

        self.sampler.sample(self.sample)
        self.voltage = self.sample[0]

        X_train, X_test, y_train, y_test = train_test_split(self.voltage, test_size=0.2, random_state=42)

        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        model = tf.keras.models.Sequential([
            tf.keras.layers.Dense(32, activation='relu', input_shape=(X_train.shape[1],)),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(1)
        ])

        model.compile(optimizer='adam', loss='mse', metrics=['mae'])

        history = model.fit(X_train, y_train, epochs=100, batch_size=16, validation_data=(X_test, y_test))

        test_loss, test_mae = model.evaluate(X_test, y_test)

        voltages = model.predict(X_test)
        voltages_scaled = scaler.transform(voltages)
        corrected_voltages = model.predict(voltages_scaled)

        self.LCR.write_dac(3, self.corrected_voltages[0])

        self.LCR.load()

import numpy as np
from time import time
from os import environ, mkdir, listdir
from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo
environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from .distribution import RandomDistributionReform
from .preparation1 import read_model, load_midi_file


class FormateError(TypeError):
    pass


class Predict:
    def __init__(self,
                 seed,
                 epoch: int,
                 model_version,
                 instrument_code: int = 0,
                 ):
        """
        The main class, called to predict scores.
        :param seed: the start score, need an array in size (1, 8, 4)
        :param epoch: the total length of the generated score will be 8(seed length) + epoch

        #Warning:
        Copy the model files (*.keras) in the package path to your programme directory before call Predict!
        """
        self.model = read_model(version=model_version)
        self.seed = seed
        self.epoch = epoch
        self.instrument = instrument_code
        self.prediction = None
        self.sequence = []
        self.save_file_name = f'{int(time())}-ß'
        self.mid = MidiFile()
        self.track0 = MidiTrack()
        self.track1 = MidiTrack()
        self.mid.tracks.append(self.track0)
        self.mid.tracks.append(self.track1)
        self.cycle()
        self.save_track0()
        self.save_track1()
        self.mid.save(f'{self.save_file_name}.mid')

    def cycle(self):
        for i in range(0, self.epoch):
            self.prediction = self.model.predict(self.seed)
            print(self.seed[0, -1, :])
            self.prediction = RandomDistributionReform(self.prediction, args=(5, 5))
            self.prediction = self.prediction.beta_distribution()
            for j in range(0, 7):
                self.seed[0, j, :] = self.seed[0, j + 1, :]
            self.seed[0, 7, :] = self.prediction[0, :]
            self.sequence.append(self.prediction[0])

    def save_track0(self):
        self.track0.append(MetaMessage('time_signature', numerator=4, denominator=4, time=0))
        self.track0.append(MetaMessage('key_signature', key='C', time=0))
        self.track0.append(MetaMessage('set_tempo', tempo=bpm2tempo(80), time=0))
        self.track0.append(MetaMessage('track_name', name=self.save_file_name, time=0))
        self.track0.append(MetaMessage('end_of_track', time=1))

    def save_track1(self):
        self.track1.append(MetaMessage('track_name', name='Instrument', time=0))
        self.track1.append(Message(type='program_change', program=self.instrument, time=0))
        middle = []
        for i in self.sequence:
            if i[0] < 0.5:
                i[0] = 0
            else:
                i[0] = 1
            args = (int(i[0]), int(i[1] * 128), int(i[2] * 128), int(i[3] * 128))
            if args[1] > 127 or args[2] > 127:
                continue
            elif args[3] > 1000:
                continue
            middle.append(args)
        middle = np.array(middle).T
        a, b= middle[0].T, middle[1].T
        count = 0
        for i, j in enumerate(b):
            if a[i] == 1:
                c = middle.T[i + 1:]
                if np.array([0, j]) not in c[:, :2]:
                    middle_f = np.delete(middle, obj=i, axis=1)
                    middle = middle_f
                    print(middle_f)
                    continue
            count += 1
        middle = middle.T
        for i in middle:
            if i[0] < 0.5:
               event_flag = 'note_off'
            else:
               event_flag = 'note_on'
            self.track1.append(Message(type=event_flag, note=i[1], velocity=i[2], time=i[3]))
        self.track1.append(MetaMessage('end_of_track', time=1))


class Seed:
    def __init__(self, midi_file: str):
        self.midi = midi_file
        self.check_formate()
        self.seed = np.zeros(shape=(1, 8, 4))
        self.score = load_midi_file(self.midi)
        self.form_seed_array(self.score)

    def check_formate(self):
        if '.mid' not in self.midi:
            fe = FormateError()
            fe.add_note(f'{self.midi} is not a correct input formate.')
            raise fe

    def form_seed_array(self, score: list):
        for i in range(0, 8):
            for j in range(0, 4):
                self.seed[0, i, j] = score[i][j]

    def get_seed(self):
        return self.seed


if __name__ == '__main__':
    s = Seed(midi_file='example_seed.mid')
    Predict(seed=s.get_seed(),epoch=128, model_version=1751770203)

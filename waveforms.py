import numpy as np

class Waveforms:
    @staticmethod
    def sine(frequency: float, sample_rate: int, num_samples: int) -> np.ndarray:
        t = np.linspace(0, num_samples/sample_rate, num_samples, False)
        return np.sin(2 * np.pi * frequency * t)
    
    @staticmethod
    def square(frequency: float, sample_rate: int, num_samples: int) -> np.ndarray:
        t = np.linspace(0, num_samples/sample_rate, num_samples, False)
        return np.sign(np.sin(2 * np.pi * frequency * t))
    
    @staticmethod
    def saw(frequency: float, sample_rate: int, num_samples: int) -> np.ndarray:
        t = np.linspace(0, num_samples/sample_rate, num_samples, False)
        return 2 * (frequency * t % 1) - 1

def midi_to_frequency(midi_note: int) -> float:
    return 440 * (2 ** ((midi_note - 69) / 12))

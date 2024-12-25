import numpy as np
from typing import Dict
from envelope import EnvelopeGenerator, ADSRParams
from waveforms import Waveforms, midi_to_frequency

class Voice:
    def __init__(self, sample_rate: int, waveform_type: str):
        self.sample_rate = sample_rate
        self.waveform_type = waveform_type
        self.frequency = 440.0
        self.envelope = EnvelopeGenerator(sample_rate, ADSRParams(0.1, 0.1, 0.7, 0.2))
        self.is_active = False
        
    def generate_samples(self, num_samples: int) -> np.ndarray:
        if not self.is_active:
            return np.zeros(num_samples)
            
        if self.waveform_type == 'sine':
            waveform = Waveforms.sine(self.frequency, self.sample_rate, num_samples)
        elif self.waveform_type == 'square':
            waveform = Waveforms.square(self.frequency, self.sample_rate, num_samples)
        else:  # saw
            waveform = Waveforms.saw(self.frequency, self.sample_rate, num_samples)
            
        envelope_values = np.array([self.envelope.get_next_value() for _ in range(num_samples)])
        return waveform * envelope_values

class Synthesizer:
    def __init__(self, sample_rate: int):
        self.sample_rate = sample_rate
        self.voices: Dict[int, Voice] = {}
        self.waveform_type = 'sine'
        self.max_voices = 16
        
    def note_on(self, note: int, velocity: int):
        if len(self.voices) >= self.max_voices:
            return
            
        if note not in self.voices:
            voice = Voice(self.sample_rate, self.waveform_type)
            voice.frequency = midi_to_frequency(note)
            voice.is_active = True
            voice.envelope.note_on()
            self.voices[note] = voice
            
    def note_off(self, note: int):
        if note in self.voices:
            self.voices[note].envelope.note_off()
            
    def generate_samples(self, num_samples: int) -> np.ndarray:
        output = np.zeros(num_samples)
        finished_notes = []
        
        for note, voice in self.voices.items():
            samples = voice.generate_samples(num_samples)
            output += samples
            
            if voice.envelope.state == 'idle':
                finished_notes.append(note)
                
        # Remove finished voices
        for note in finished_notes:
            del self.voices[note]
            
        # Normalize output
        if len(self.voices) > 0:
            output /= len(self.voices)
            
        return output
            
    def set_waveform(self, waveform_type: str):
        if waveform_type in ['sine', 'square', 'saw']:
            self.waveform_type = waveform_type

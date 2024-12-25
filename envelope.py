import numpy as np
from dataclasses import dataclass

@dataclass
class ADSRParams:
    attack: float  # seconds
    decay: float   # seconds
    sustain: float # level (0-1)
    release: float # seconds

class EnvelopeGenerator:
    def __init__(self, sample_rate: int, params: ADSRParams):
        self.sample_rate = sample_rate
        self.params = params
        self.current_value = 0.0
        self.state = 'idle'
        self.release_from = 0.0
        self.time_in_state = 0
        
    def get_next_value(self) -> float:
        if self.state == 'idle':
            return 0.0
            
        self.time_in_state += 1.0 / self.sample_rate
        
        if self.state == 'attack':
            self.current_value = min(1.0, self.time_in_state / self.params.attack)
            if self.current_value >= 1.0:
                self.state = 'decay'
                self.time_in_state = 0
                
        elif self.state == 'decay':
            self.current_value = 1.0 + (self.params.sustain - 1.0) * (self.time_in_state / self.params.decay)
            if self.time_in_state >= self.params.decay:
                self.state = 'sustain'
                self.current_value = self.params.sustain
                
        elif self.state == 'release':
            self.current_value = self.release_from * (1.0 - self.time_in_state / self.params.release)
            if self.time_in_state >= self.params.release:
                self.state = 'idle'
                self.current_value = 0.0
                
        return max(0.0, self.current_value)
    
    def note_on(self):
        self.state = 'attack'
        self.time_in_state = 0
        
    def note_off(self):
        self.state = 'release'
        self.release_from = self.current_value
        self.time_in_state = 0

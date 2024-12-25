from typing import Callable, Dict, List
from dataclasses import dataclass

@dataclass
class MidiEvent:
    type: str  # 'note_on' or 'note_off'
    note: int
    velocity: int
    channel: int

class EventDispatcher:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
    
    def dispatch(self, event_type: str, event: MidiEvent):
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                callback(event)

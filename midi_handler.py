
import pygame.midi
from event_system import EventDispatcher, MidiEvent
import threading
import time

class MidiHandler:
    def __init__(self, dispatcher: EventDispatcher):
        self.dispatcher = dispatcher
        self.midi_in = None
        self._port = None
        self._virtual_mode = False
        self._running = False
        self._thread = None

    def init_midi(self):
        try:
            pygame.midi.init()
            if pygame.midi.get_count() > 0:
                self.midi_in = pygame.midi.Input(0)  # Try to open the first MIDI device
                print("MIDI device connected")
                self._thread = threading.Thread(target=self._midi_polling_loop)
                self._running = True
                self._thread.start()
            else:
                raise Exception("No MIDI devices found")
        except Exception as e:
            print(f"Could not initialize MIDI device: {str(e)}")
            print("Falling back to keyboard input mode...")
            self._init_keyboard_mode()

    def _init_keyboard_mode(self):
        self._virtual_mode = True
        print("Keyboard mode activated - You can use your computer keyboard to play notes")

    def _midi_polling_loop(self):
        while self._running:
            if self.midi_in.poll():
                midi_events = self.midi_in.read(10)
                for event in midi_events:
                    self._handle_midi_event(event[0])
            time.sleep(0.001)  # Small sleep to prevent CPU hogging

    def _handle_midi_event(self, event):
        status = event[0][0]
        note = event[0][1]
        velocity = event[0][2]

        if (status & 0xF0) == 0x90 and velocity > 0:
            midi_event = MidiEvent('note_on', note, velocity, status & 0x0F)
            self.dispatcher.dispatch('note_on', midi_event)
        elif (status & 0xF0) == 0x80 or ((status & 0xF0) == 0x90 and velocity == 0):
            midi_event = MidiEvent('note_off', note, velocity, status & 0x0F)
            self.dispatcher.dispatch('note_off', midi_event)

    def send_virtual_note_on(self, note: int, velocity: int = 64):
        midi_event = MidiEvent('note_on', note, velocity, 0)
        self.dispatcher.dispatch('note_on', midi_event)

    def send_virtual_note_off(self, note: int):
        midi_event = MidiEvent('note_off', note, 0, 0)
        self.dispatcher.dispatch('note_off', midi_event)

    def cleanup(self):
        self._running = False
        if self._thread:
            self._thread.join()
        if self.midi_in:
            self.midi_in.close()
        pygame.midi.quit()

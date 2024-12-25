
import mididevice
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
            self.midi_in = mididevice.MIDIDevice()  # Try to open the first MIDI device
            print("MIDI device connected")
            self._thread = threading.Thread(target=self._midi_polling_loop)
            self._running = True
            self._thread.start()
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
                events = self.midi_in.read(1)
                for event in events:
                    self._handle_midi_event(event)
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
            del self.midi_in

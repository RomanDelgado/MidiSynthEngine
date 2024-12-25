import rtmidi
from rtmidi.midiutil import open_midiinput
from event_system import EventDispatcher, MidiEvent

class MidiHandler:
    def __init__(self, dispatcher: EventDispatcher):
        self.dispatcher = dispatcher
        self.midi_in = None
        self._port = None
        self._virtual_mode = False

    def init_midi(self):
        """Initialize MIDI input with Windows compatibility in mind"""
        try:
            self.midi_in = rtmidi.MidiIn()
            available_ports = self.midi_in.get_ports()

            if available_ports:
                # Try to open the first available port
                self._port, port_name = open_midiinput(0)
                self._port.set_callback(self._midi_callback)
                print(f"Connected to MIDI device: {port_name}")
            else:
                print("No MIDI devices found. The synthesizer will accept keyboard input only.")
                self._init_keyboard_mode()

        except Exception as e:
            print(f"Could not initialize MIDI device: {str(e)}")
            print("Falling back to keyboard input mode...")
            self._init_keyboard_mode()

    def _init_keyboard_mode(self):
        """Initialize keyboard input mode when no MIDI devices are available"""
        self._virtual_mode = True
        print("Keyboard mode activated - You can use your computer keyboard to play notes")

    def _midi_callback(self, event, data=None):
        message, deltatime = event

        if len(message) == 3:  # Standard MIDI message format
            status, note, velocity = message

            # Note on event (status & 0xF0 = 144)
            if (status & 0xF0) == 0x90 and velocity > 0:
                midi_event = MidiEvent('note_on', note, velocity, status & 0x0F)
                self.dispatcher.dispatch('note_on', midi_event)

            # Note off event (status & 0xF0 = 128 or note on with velocity 0)
            elif (status & 0xF0) == 0x80 or ((status & 0xF0) == 0x90 and velocity == 0):
                midi_event = MidiEvent('note_off', note, velocity, status & 0x0F)
                self.dispatcher.dispatch('note_off', midi_event)

    def send_virtual_note_on(self, note: int, velocity: int = 64):
        """Send a virtual note-on event (for keyboard input)"""
        midi_event = MidiEvent('note_on', note, velocity, 0)
        self.dispatcher.dispatch('note_on', midi_event)

    def send_virtual_note_off(self, note: int):
        """Send a virtual note-off event (for keyboard input)"""
        midi_event = MidiEvent('note_off', note, 0, 0)
        self.dispatcher.dispatch('note_off', midi_event)

    def cleanup(self):
        if self._port:
            self._port.close_port()
        if self.midi_in:
            del self.midi_in
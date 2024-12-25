from typing import Optional, Dict
from event_system import EventDispatcher, MidiEvent
from midi_handler import MidiHandler
from synthesizer import Synthesizer
from audio_output import AudioOutput
import threading
import time

class MIDISynth:
    """
    High-level interface for the MIDI synthesizer that combines all components
    into a single, easy-to-use class. Cross-platform compatible with keyboard input support.
    """

    # Map computer keyboard keys to MIDI note numbers (middle C = 60)
    KEY_TO_NOTE = {
        'a': 60,  # C4
        'w': 61,  # C#4
        's': 62,  # D4
        'e': 63,  # D#4
        'd': 64,  # E4
        'f': 65,  # F4
        't': 66,  # F#4
        'g': 67,  # G4
        'y': 68,  # G#4
        'h': 69,  # A4
        'u': 70,  # A#4
        'j': 71,  # B4
        'k': 72,  # C5
    }

    def __init__(self, sample_rate: int = 44100, block_size: int = 256):
        self.sample_rate = sample_rate
        self.block_size = block_size

        # Initialize all components
        self.dispatcher = EventDispatcher()
        self.synthesizer = Synthesizer(sample_rate)
        self.audio = AudioOutput(sample_rate, block_size)
        self.midi = MidiHandler(self.dispatcher)

        # Set up default event handlers
        self._setup_default_handlers()

        self._is_running = False
        self._active_notes: Dict[str, int] = {}  # Track active notes

    def _setup_default_handlers(self):
        """Set up the default MIDI event handlers."""
        self.dispatcher.subscribe('note_on', 
                                lambda event: self.synthesizer.note_on(event.note, event.velocity))
        self.dispatcher.subscribe('note_off', 
                                lambda event: self.synthesizer.note_off(event.note))

    def handle_key_press(self, key: str):
        """Handle a key press event"""
        if key in self.KEY_TO_NOTE and key not in self._active_notes:
            note = self.KEY_TO_NOTE[key]
            self._active_notes[key] = note
            self.midi.send_virtual_note_on(note)
            return True
        return False

    def handle_key_release(self, key: str):
        """Handle a key release event"""
        if key in self._active_notes:
            note = self._active_notes.pop(key)
            self.midi.send_virtual_note_off(note)
            return True
        return False

    def set_waveform(self, waveform_type: str):
        """
        Set the synthesizer waveform type.

        Args:
            waveform_type: One of 'sine', 'square', or 'saw'
        """
        if waveform_type not in ['sine', 'square', 'saw']:
            raise ValueError("Waveform type must be one of: sine, square, saw")
        self.synthesizer.set_waveform(waveform_type)

    def start(self):
        """
        Start the synthesizer and begin processing MIDI/keyboard input.

        Raises:
            RuntimeError: If the synthesizer is already running
            Exception: If audio initialization fails
        """
        if self._is_running:
            raise RuntimeError("Synthesizer is already running")

        try:
            # Initialize MIDI input
            self.midi.init_midi()

            # Start audio output
            self.audio.start(lambda frames: self.synthesizer.generate_samples(frames))

            self._is_running = True

        except Exception as e:
            self.stop()
            raise Exception(f"Failed to start synthesizer: {str(e)}")

    def stop(self):
        """Stop the synthesizer and clean up resources."""
        if self._is_running:
            self._is_running = False
            self.audio.stop()
            self.midi.cleanup()

    @property
    def is_running(self) -> bool:
        """Return whether the synthesizer is currently running."""
        return self._is_running

    def __enter__(self):
        """Context manager entry point."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        self.stop()

# Example usage:
if __name__ == "__main__":
    print("Starting MIDI Synthesizer...")
    print("\nKeyboard Controls:")
    print("  A,W,S,E,D,F,T,G,Y,H,U,J,K - Play notes (C4 through C5)")
    print("\nAvailable commands:")
    print("  press <key>  - Press a note key (e.g., 'press a')")
    print("  release <key> - Release a note key (e.g., 'release a')")
    print("  sine    - Switch to sine wave")
    print("  square  - Switch to square wave")
    print("  saw     - Switch to saw wave")
    print("  quit    - Exit the program")

    try:
        with MIDISynth() as synth:
            print("\nSynthesizer is running! Enter commands to play notes or change settings.")

            while synth.is_running:
                cmd = input().strip().lower()
                parts = cmd.split()

                if cmd in ['sine', 'square', 'saw']:
                    synth.set_waveform(cmd)
                    print(f"Switched to {cmd} waveform")
                elif len(parts) == 2 and parts[0] == 'press':
                    key = parts[1]
                    if synth.handle_key_press(key):
                        print(f"Note {key} pressed")
                    else:
                        print(f"Invalid key: {key}")
                elif len(parts) == 2 and parts[0] == 'release':
                    key = parts[1]
                    if synth.handle_key_release(key):
                        print(f"Note {key} released")
                    else:
                        print(f"Invalid key or key not pressed: {key}")
                elif cmd == 'quit':
                    break
                else:
                    print("Unknown command")

    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
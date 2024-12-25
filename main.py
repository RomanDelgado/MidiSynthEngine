import sys
import time
from event_system import EventDispatcher
from midi_handler import MidiHandler
from synthesizer import Synthesizer
from audio_output import AudioOutput

def main():
    # Initialize components
    SAMPLE_RATE = 44100
    BLOCK_SIZE = 256
    
    dispatcher = EventDispatcher()
    synth = Synthesizer(SAMPLE_RATE)
    audio = AudioOutput(SAMPLE_RATE, BLOCK_SIZE)
    midi = MidiHandler(dispatcher)
    
    # Set up event handlers
    dispatcher.subscribe('note_on', lambda event: synth.note_on(event.note, event.velocity))
    dispatcher.subscribe('note_off', lambda event: synth.note_off(event.note))
    
    try:
        # Start MIDI input
        midi.init_midi()
        
        # Start audio output
        audio.start(lambda frames: synth.generate_samples(frames))
        
        print("Synth is running! Press Ctrl+C to exit.")
        print("Available commands:")
        print("  sine    - Switch to sine wave")
        print("  square  - Switch to square wave")
        print("  saw     - Switch to saw wave")
        print("  quit    - Exit the program")
        
        # Main loop for command processing
        while True:
            cmd = input().strip().lower()
            if cmd == 'quit':
                break
            elif cmd in ['sine', 'square', 'saw']:
                synth.set_waveform(cmd)
                print(f"Switched to {cmd} waveform")
            else:
                print("Unknown command")
                
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        audio.stop()
        midi.cleanup()

if __name__ == "__main__":
    main()

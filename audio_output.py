import sounddevice as sd
import numpy as np
import time
import threading

class AudioOutput:
    def __init__(self, sample_rate: int, block_size: int):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.stream = None
        self._dummy_mode = False
        self._is_running = False
        self._dummy_thread = None

    def start(self, callback):
        try:
            # First try to initialize real audio output
            devices = sd.query_devices()
            default_device = sd.default.device[1] if hasattr(sd.default, 'device') else -1

            # If no default device, try to find any output device
            if default_device < 0:
                for i, device in enumerate(devices):
                    if device['max_output_channels'] > 0:
                        default_device = i
                        break

            if default_device >= 0:
                print(f"Using audio device: {devices[default_device]['name']}")
                self.stream = sd.OutputStream(
                    samplerate=self.sample_rate,
                    device=default_device,
                    channels=1,
                    callback=lambda outdata, frames, time, status: self._callback(outdata, frames, time, status, callback),
                    blocksize=self.block_size,
                    dtype=np.float32
                )
                self.stream.start()
                print("Audio output started successfully")
            else:
                print("No audio output devices found, falling back to dummy output mode")
                self._start_dummy_mode(callback)

        except Exception as e:
            print(f"Error starting audio output: {str(e)}")
            print("Available audio devices:")
            try:
                print(sd.query_devices())
            except:
                print("Could not query audio devices")
            print("\nFalling back to dummy output mode")
            self._start_dummy_mode(callback)

    def _start_dummy_mode(self, callback):
        """Start a dummy output mode that simulates audio output"""
        self._dummy_mode = True
        self._is_running = True

        def dummy_audio_loop():
            while self._is_running:
                # Generate samples but don't output them
                _ = callback(self.block_size)
                time.sleep(self.block_size / self.sample_rate)  # Simulate real-time audio

        self._dummy_thread = threading.Thread(target=dummy_audio_loop)
        self._dummy_thread.daemon = True
        self._dummy_thread.start()
        print("Dummy audio output mode active (no sound will be produced)")

    def _callback(self, outdata, frames, time, status, user_callback):
        if status:
            print(f"Audio callback status: {status}")

        try:
            # Get samples from the synthesizer
            samples = user_callback(frames)

            # Ensure samples are float32 and properly shaped
            samples = np.asarray(samples, dtype=np.float32)

            # Clip to prevent distortion
            samples = np.clip(samples, -1.0, 1.0)

            # Reshape to match required output format
            outdata[:] = samples.reshape(-1, 1)

        except Exception as e:
            print(f"Error in audio callback: {str(e)}")
            outdata[:] = np.zeros((frames, 1), dtype=np.float32)

    def stop(self):
        self._is_running = False

        if self._dummy_thread:
            self._dummy_thread.join(timeout=1.0)
            print("Dummy audio output stopped")

        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
                print("Audio output stopped")
            except Exception as e:
                print(f"Error stopping audio output: {str(e)}")
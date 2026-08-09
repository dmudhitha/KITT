"""
Voice Module for VANGUARD Assistant.
Implements Speech-to-Text (STT) speech recognition, wake word detection, and mute states.
"""
import logging
import threading
import time
from typing import Callable, Optional
import speech_recognition as sr
import pyttsx3

logger = logging.getLogger("vanguard.voice")


class SpeechRecognizer:
    """Manages microphone input capture, background listening, wake word validation, and transcription."""

    def __init__(
        self,
        config_manager,
        on_transcription: Callable[[str], None],
        on_status_change: Callable[[str, bool], None]
    ):
        self.config = config_manager
        self.on_transcription = on_transcription
        self.on_status_change = on_status_change

        # Load configs
        self.wake_word = self.config.get("voice", "wake_word", "hey kitt").lower()
        self.wake_word_enabled = self.config.get("voice", "wake_word_enabled", True)
        self.mic_timeout = self.config.get("voice", "mic_timeout", 5)
        self.mute_mode = self.config.get("voice", "mute_mode", False)

        # Recognizer setup
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = self.config.get("voice", "mic_energy_threshold", 300)
        self.recognizer.dynamic_energy_threshold = True

        self.microphone: Optional[sr.Microphone] = None
        self.stop_listening_fn: Optional[Callable] = None
        self.is_listening = False
        self.is_calibrating = False

        # Run microphone discovery in a thread to prevent blocking main UI initialization
        threading.Thread(target=self._init_microphone, daemon=True).start()

    def _init_microphone(self) -> None:
        """Discovers audio hardware and performs ambient noise calibration."""
        self.is_calibrating = True
        logger.info("Initializing audio input device...")
        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                logger.info("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
            logger.info("Microphone calibration complete.")
            self.is_calibrating = False
            
            # Start continuous background listening if wake word is enabled
            if self.wake_word_enabled and not self.mute_mode:
                self.start_background_listening()
        except OSError as e:
            logger.error(f"Microphone hardware discovery failed: {e}")
            self.on_status_change("MIC HARDWARE NOT FOUND", False)
            self.is_calibrating = False

    def _wait_for_mic_release(self) -> None:
        """Blocks for a short duration until the microphone device stream is released by background threads."""
        if self.microphone:
            for _ in range(40):  # Wait up to 2.0 seconds
                if self.microphone.stream is None:
                    break
                time.sleep(0.05)

    def start_background_listening(self) -> None:
        """Starts background thread listener waiting for the wake word."""
        if self.mute_mode or not self.microphone:
            return

        if self.stop_listening_fn:
            self.stop_listening_fn(wait_for_stop=True)
            self.stop_listening_fn = None

        # Spin up a worker thread to wait for mic release and launch listeners safely
        def start_listening_worker():
            self._wait_for_mic_release()
            try:
                # Double check we haven't mutated states in the meantime
                if self.stop_listening_fn is None and not self.mute_mode and not self.is_listening:
                    logger.info("VANGUARD wake word monitoring activated...")
                    self.stop_listening_fn = self.recognizer.listen_in_background(
                        self.microphone,
                        self._background_callback,
                        phrase_time_limit=self.mic_timeout
                    )
            except Exception as e:
                logger.error(f"Failed to start background listener: {e}")

        threading.Thread(target=start_listening_worker, daemon=True).start()

    def stop_background_listening(self) -> None:
        """Stops background thread listener."""
        if self.stop_listening_fn:
            logger.info("VANGUARD wake word monitoring deactivated.")
            self.stop_listening_fn(wait_for_stop=True)
            self.stop_listening_fn = None

    def _background_callback(self, recognizer: sr.Recognizer, audio: sr.AudioData) -> None:
        """Triggered automatically by listen_in_background thread when speech ends."""
        if self.mute_mode or self.is_listening:
            return
            
        # Launch transcription in a thread to keep background callback responsive
        threading.Thread(target=self._transcribe_background_audio, args=(audio,), daemon=True).start()

    def _transcribe_background_audio(self, audio: sr.AudioData) -> None:
        """Transcribes background audio, looking for the wake word."""
        try:
            logger.debug("Transcribing background capture...")
            stt_lang = self.config.get("voice", "stt_language", "en-US")
            text = self.recognizer.recognize_google(audio, language=stt_lang).lower().strip()
            logger.debug(f"Background capture: '{text}'")
            
            # Match common phonetical variations of "hey kitt" including Sinhala scripts
            wake_options = [
                "hey kitt", "hey kit", "hai kitt", "hai kit", "hi kitt", "hi kit", "hey kid", "hey cat",
                "හේ කිට්", "හේ කිට්ටෝ", "කිට්", "කිට්ටෝ"
            ]
            matched_wake = None
            for wake in wake_options:
                if wake in text:
                    matched_wake = wake
                    break
            
            if matched_wake:
                logger.info(f"Wake word '{matched_wake}' detected!")
                # Remove the wake word from transcription and process subsequent command if present
                command = text.split(matched_wake, 1)[1].strip()
                
                # Notify UI of wake-up
                self.on_status_change("WAKE WORD DETECTED", True)
                
                if command:
                    logger.info(f"Processing follow-up command: {command}")
                    self.on_transcription(command)
                else:
                    # Single short wake-up beep or alert
                    logger.info("Wake word matched with no command. Activating single listener...")
                    time.sleep(0.2)
                    self.trigger_single_listen()
        except sr.UnknownValueError:
            pass  # Ignore unrecognizable noise
        except sr.RequestError as e:
            logger.warning(f"Google speech service API unavailable: {e}")
        except Exception as e:
            logger.error(f"Error in background transcription: {e}")

    def trigger_single_listen(self) -> None:
        """Actively starts listening for a single query (push-to-talk behavior)."""
        if not self.microphone:
            self.on_status_change("MIC NOT INITIALIZED", False)
            return

        if self.is_listening:
            return

        self.is_listening = True
        self.stop_background_listening()
        self.on_status_change("LISTENING...", True)

        # Run listening capture on background thread
        threading.Thread(target=self._single_listen_worker, daemon=True).start()

    def _single_listen_worker(self) -> None:
        """Microphone capture thread worker for single-shot command."""
        self._wait_for_mic_release()
        try:
            with self.microphone as source:
                logger.info("Awaiting audio capture...")
                audio = self.recognizer.listen(source, timeout=self.mic_timeout, phrase_time_limit=self.mic_timeout)
            
            self.on_status_change("TRANSCRIBING...", True)
            stt_lang = self.config.get("voice", "stt_language", "en-US")
            text = self.recognizer.recognize_google(audio, language=stt_lang).strip()
            logger.info(f"Transcribed speech command: '{text}'")
            
            # Post command back to UI thread
            self.on_transcription(text)
            
        except sr.WaitTimeoutError:
            logger.info("Audio capture timed out. No speech detected.")
            self.on_status_change("TIMEOUT: NO SPEECH DETECTED", False)
        except sr.UnknownValueError:
            logger.warning("Google Speech Recognition was unable to clarify audio.")
            self.on_status_change("ERROR: UNABLE TO CLARIFY AUDIO", False)
        except sr.RequestError as e:
            logger.error(f"Speech recognition service request failure: {e}")
            self.on_status_change("API SERVICE REFUSED LINK", False)
        except Exception as e:
            logger.error(f"Unhandled error in voice recognizer capture: {e}")
            self.on_status_change("INPUT DEVICE ERROR", False)
        finally:
            self.is_listening = False
            # Resume background wake word listener
            if self.wake_word_enabled and not self.mute_mode:
                self.start_background_listening()

    def set_mute(self, is_muted: bool) -> None:
        """Toggles mute mode on or off."""
        self.mute_mode = is_muted
        self.config.set("voice", "mute_mode", is_muted)
        logger.info(f"Voice mute state changed to: {is_muted}")
        
        if is_muted:
            self.stop_background_listening()
        else:
            if self.wake_word_enabled:
                self.start_background_listening()


class SpeechSynthesizer:
    """Manages Text-to-Speech (TTS) speech synthesis engines on background threads."""

    def __init__(self, config_manager):
        self.config = config_manager
        self.speaking_lock = threading.Lock()
        self.engine = None
        
        try:
            # Initialize pyttsx3 once to avoid weak-reference collection errors on Linux
            self.engine = pyttsx3.init()
            logger.info("pyttsx3 Speech Synthesizer engine initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3 TTS engine: {e}")

    def speak(
        self,
        text: str,
        on_start_callback: Optional[Callable[[], None]] = None,
        on_end_callback: Optional[Callable[[], None]] = None
    ) -> None:
        """
        Synthesizes text to speech in a background thread.
        Aborts early if voice output is disabled or muted.
        """
        tts_enabled = self.config.get("voice", "tts_enabled", True)
        mute_mode = self.config.get("voice", "mute_mode", False)

        if not tts_enabled or mute_mode or not self.engine:
            logger.info("Voice synthesis bypassed (TTS disabled, muted, or uninitialized).")
            if on_end_callback:
                on_end_callback()
            return

        # Spawn background speaking thread to prevent blocking CustomTkinter loop
        threading.Thread(
            target=self._speak_worker,
            args=(text, on_start_callback, on_end_callback),
            daemon=True
        )        .start()

    def _speak_worker(
        self,
        text: str,
        on_start: Optional[Callable[[], None]],
        on_end: Optional[Callable[[], None]]
    ) -> None:
        """Speaking execution thread worker."""
        if not self.engine:
            if on_end:
                on_end()
            return

        # Ensure only one thread calls pyttsx3 speaker at a time
        with self.speaking_lock:
            if on_start:
                on_start()

            try:
                # Configure Voice properties on each play call
                rate = self.config.get("voice", "tts_rate", 160)
                volume = self.config.get("voice", "tts_volume", 1.0)
                pitch = self.config.get("voice", "tts_pitch", 50)
                variant = self.config.get("voice", "tts_variant", "+m3")
                voice_index = self.config.get("voice", "tts_voice_index", 0)

                self.engine.setProperty("rate", rate)
                self.engine.setProperty("volume", volume)
                self.engine.setProperty("pitch", pitch)

                # Check if text contains Sinhala characters (Unicode range \u0d80 - \u0dff)
                is_sinhala = any('\u0d80' <= char <= '\u0dff' for char in text)

                voices = self.engine.getProperty("voices")
                if voices:
                    if voice_index >= len(voices):
                        voice_index = 0
                    
                    selected_voice_id = voices[voice_index].id
                    
                    if is_sinhala:
                        # Find the Sinhala voice (e.g. ID inc/si or name containing 'sinhala')
                        for v in voices:
                            v_id_lower = v.id.lower()
                            v_name_lower = v.name.lower()
                            if "sinhala" in v_name_lower or "inc/si" == v_id_lower or v_id_lower.endswith("/si") or v_id_lower == "si":
                                selected_voice_id = v.id
                                logger.info(f"Selected Sinhala TTS voice: {v.name}")
                                break
                    else:
                        # 1. Look for English (US)
                        for v in voices:
                            v_id_lower = v.id.lower()
                            v_name_lower = v.name.lower()
                            if "en-us" in v_id_lower or "english-us" in v_id_lower or "america" in v_name_lower:
                                selected_voice_id = v.id
                                # Append variant for cleaner/more natural tone on Linux (e.g. 'en-us+m3')
                                if variant and ("en" in selected_voice_id or "gmw" in selected_voice_id):
                                    selected_voice_id = "en-us" + variant
                                logger.info(f"Selected clearer US English voice with variant: {selected_voice_id}")
                                break
                        else:
                            # 2. Fallback to generic English
                            for v in voices:
                                v_id_lower = v.id.lower()
                                if "en" in v_id_lower or "english" in v_id_lower:
                                    selected_voice_id = v.id
                                    if variant and ("en" in selected_voice_id or "gmw" in selected_voice_id):
                                        selected_voice_id = "en" + variant
                                    logger.info(f"Fallback to English voice with variant: {selected_voice_id}")
                                    break
                            else:
                                # 3. Fallback to male search
                                for v in voices:
                                    name_lower = v.name.lower()
                                    if "david" in name_lower or ("male" in name_lower and "female" not in name_lower):
                                        selected_voice_id = v.id
                                        logger.info(f"Fallback male voice matched: {v.name}")
                                        break
                    
                    self.engine.setProperty("voice", selected_voice_id)

                # Synthesize
                self.engine.say(text)
                self.engine.runAndWait()
                
            except Exception as e:
                logger.error(f"Error executing speech synthesis: {e}")
            finally:
                if on_end:
                    # Let espeak handles settle before releasing state
                    time.sleep(0.1)
                    on_end()

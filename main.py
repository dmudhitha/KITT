"""
VANGUARD AI Assistant - Main Entry Point.
Autonomous Electronic General Intelligence System (A.E.G.I.S. / VANGUARD)
"""
import os
import sys
import argparse
import logging
import time
import threading
from typing import Optional
from config import ConfigManager
from database import DatabaseManager
from utils import setup_logging
from ui import VanguardUI
from ai import AIEngine
from voice import SpeechRecognizer, SpeechSynthesizer
from commands import PluginManager

# Subsystem variables
config: Optional[ConfigManager] = None
db: Optional[DatabaseManager] = None
logger: Optional[logging.Logger] = None
ai_engine: Optional[AIEngine] = None
voice_recognizer: Optional[SpeechRecognizer] = None
voice_synthesizer: Optional[SpeechSynthesizer] = None
plugin_manager: Optional[PluginManager] = None


def init_subsystems(config_dir: str = "config", database_dir: str = "database", log_dir: str = "logs") -> bool:
    """Initializes config, logging, database, AI, and Voice subsystems."""
    global config, db, logger, ai_engine, voice_recognizer
    
    # 1. Load configuration (fallback to defaults if config file doesn't exist)
    config = ConfigManager(config_dir=config_dir)
    
    # 2. Setup Logging using configuration preferences
    log_level = config.get("logging", "log_level", "INFO")
    log_to_file = config.get("logging", "log_to_file", True)
    logger = setup_logging(log_dir=log_dir, log_level_str=log_level, log_to_file=log_to_file)
    
    logger.info("Initializing VANGUARD sub-systems...")
    
    # 3. Create required directories
    for directory in ["assets/sounds", "assets/icons", "assets/fonts", "assets/images", "plugins"]:
        os.makedirs(directory, exist_ok=True)
        logger.debug(f"Ensured directory exists: {directory}")
        
    # Generate Synthesized Audio Notification Files
    from utils import generate_sine_wav
    generate_sine_wav("assets/sounds/boot.wav", [220.0, 440.0, 880.0], duration=0.2)
    generate_sine_wav("assets/sounds/shutdown.wav", [880.0, 440.0, 220.0], duration=0.3)
    generate_sine_wav("assets/sounds/wake.wav", [659.25, 783.99, 987.77], duration=0.12)
        
    # 4. Initialize Database
    try:
        db = DatabaseManager(db_dir=database_dir)
    except Exception as e:
        logger.critical(f"Critical error initializing database: {e}")
        return False
        
    # 5. Initialize AI Engine
    try:
        ai_engine = AIEngine(config_manager=config, db_manager=db)
    except Exception as e:
        logger.critical(f"Critical error initializing AI Engine: {e}")
        return False
        
    logger.info("All base sub-systems initialized successfully.")
    return True


def run_dry_run_test() -> int:
    """Executes a diagnostic system self-test to verify Phase 1 architecture."""
    print("=" * 60)
    print("VANGUARD SYSTEM DIAGNOSTICS: PHASE 1 DRY RUN")
    print("=" * 60)
    
    # Initializing subsystems
    success = init_subsystems()
    if not success or not logger or not config or not db:
        print("[-] FAILED: Subsystem initialization error.")
        return 1
        
    print("[+] Subsystem Initialization: SUCCESS")
    
    # Test Configuration Manager
    api_provider = config.get("api", "provider")
    print(f"[+] Config Check (API Provider): {api_provider}")
    
    # Test Logging
    logger.info("Test log entry: System check in progress...")
    print(f"[+] Logging Check: Logs generated in logs/system.log")
    
    # Test Database Manager
    print("[+] Database Check: Testing write/read operations...")
    db_success = db.add_message("system", "Self-test sequence initiated.")
    if db_success:
        history = db.get_recent_history(limit=1)
        if history and history[0]["message"] == "Self-test sequence initiated.":
            print(f"[+] Database Check: Write/Read SUCCESS (Retrieved: '{history[0]['message']}')")
            db.clear_history()  # clean up self-test message
        else:
            print("[-] Database Check: Read mismatch or failed.")
            return 1
    else:
        print("[-] Database Check: Write failed.")
        return 1
        
    print("=" * 60)
    print("PHASE 1 DRY RUN COMPLETED SUCCESSFULLY: ALL SUB-SYSTEMS GO!")
    print("=" * 60)
    return 0


def main() -> None:
    """Main execution path."""
    parser = argparse.ArgumentParser(description="VANGUARD AI Desktop Assistant")
    parser.add_argument("--dry-run", action="store_true", help="Run subsystem diagnostics and exit")
    args = parser.parse_args()
    
    if args.dry_run:
        sys.exit(run_dry_run_test())
    
    success = init_subsystems()
    if not success or not logger or not config or not db:
        print("Critical systems failed to start. Check logs/system.log.")
        sys.exit(1)
        
    logger.info("Starting dashboard GUI...")
    
    # Callback Handlers for UI Events
    def handle_send(message: str) -> None:
        """Sends the message to the AI Engine and handles streaming response back to the UI."""
        logger.info(f"Command received: {message}")
        
        # 1. Check if user input matches a local command or plugin
        context = {
            "ui": ui_app,
            "voice_rec": voice_recognizer,
            "diagnostics": ui_app.diagnostics,
            "manager": plugin_manager
        }
        plugin_response = plugin_manager.parse_and_execute(message, context)
        
        if plugin_response is not None:
            logger.info("Executing local command handler.")
            
            # Print response directly to the console text box
            ui_app.after(0, lambda: ui_app.console_print(plugin_response, prefix="[VANGUARD] >> "))
            
            # Save assistant response to DB
            db.add_message("assistant", plugin_response)
            
            speaking_active_local = [False]
            
            def speak_start() -> None:
                # Pause background voice listening to prevent loop triggers
                if voice_recognizer:
                    voice_recognizer.stop_background_listening()
                
                ui_app.after(0, lambda: ui_app.set_thinking_state(False))
                ui_app.after(0, lambda: ui_app.draw_voice_indicator("green"))
                ui_app.after(0, lambda: ui_app.status_label.configure(
                    text="VANGUARD CORE: SPEAKING...", text_color="#33FF33"
                ))
                ui_app.after(0, lambda: ui_app.scanner.set_mode("talk"))
                
                # Start scanner amplitude modulation thread
                speaking_active_local[0] = True
                def modulate_amplitude():
                    import random
                    while speaking_active_local[0]:
                        amplitude = random.uniform(0.35, 0.95)
                        ui_app.after(0, lambda a=amplitude: ui_app.scanner.set_talk_amplitude(a))
                        time.sleep(0.08)
                threading.Thread(target=modulate_amplitude, daemon=True).start()

            def speak_end() -> None:
                speaking_active_local[0] = False
                ui_app.after(0, lambda: ui_app.draw_voice_indicator("gray"))
                ui_app.after(0, lambda: ui_app.status_label.configure(
                    text="VANGUARD CORE: ACTIVE", text_color="#33FF33"
                ))
                ui_app.after(0, lambda: ui_app.scanner.set_mode("scan"))
                
                # Resume speech recognition
                if voice_recognizer and voice_recognizer.wake_word_enabled and not voice_recognizer.mute_mode:
                    voice_recognizer.start_background_listening()
                    
            # Clean text for speech synthesis
            import re
            clean_text = re.sub(r'[\*\#`_\-]', ' ', plugin_response)
            
            if voice_synthesizer:
                voice_synthesizer.speak(clean_text, on_start_callback=speak_start, on_end_callback=speak_end)
            else:
                speak_end()
            return

        # 2. Bypassed local commands: Route to AI Engine
        ui_app.set_thinking_state(True)
        first_chunk = [True]  # Use a mutable list container to track state across thread calls
        
        def on_chunk(token: str) -> None:
            # Shift scanner to talk mode on first chunk and set randomized/simulated amplitude
            if first_chunk[0]:
                first_chunk[0] = False
                ui_app.after(0, lambda: ui_app.console_stream_start(prefix="[VANGUARD] >> "))
                ui_app.after(0, lambda: ui_app.scanner.set_mode("talk"))
            
            # Update stream text and flash scanner amplitude
            ui_app.after(0, lambda: ui_app.console_stream_chunk(token))
            import random
            amplitude = random.uniform(0.4, 0.95)
            ui_app.after(0, lambda: ui_app.scanner.set_talk_amplitude(amplitude))

        speaking_active = [False]  # Mutable cell to track speaking thread state

        def on_complete(full_text: str) -> None:
            # Save assistant response to DB
            db.add_message("assistant", full_text)
            
            # Log to specific conversation log
            convo_logger = logging.getLogger("vanguard.conversations")
            convo_logger.info(f"User: {message} | Assistant: {full_text}")
            
            # Finalize streaming text display in UI
            ui_app.after(0, lambda: ui_app.console_stream_end())
            
            # Clean markdown formatting out of text for natural speech synthesis
            import re
            clean_text = re.sub(r'```.*?```', '[Code Block omitted]', full_text, flags=re.DOTALL)
            clean_text = re.sub(r'[\*\#`_\-]', ' ', clean_text)
            
            # Sub-callbacks for Text-to-Speech playback
            def speak_start() -> None:
                # Pause background STT listener to prevent VANGUARD hearing its own output
                if voice_recognizer:
                    voice_recognizer.stop_background_listening()
                
                ui_app.after(0, lambda: ui_app.set_thinking_state(False))
                ui_app.after(0, lambda: ui_app.draw_voice_indicator("green"))
                ui_app.after(0, lambda: ui_app.status_label.configure(
                    text="VANGUARD CORE: SPEAKING...", text_color="#33FF33"
                ))
                ui_app.after(0, lambda: ui_app.scanner.set_mode("talk"))
                
                # Start scanner segment height/amplitude modulation thread
                speaking_active[0] = True
                def modulate_amplitude():
                    import random
                    while speaking_active[0]:
                        amplitude = random.uniform(0.35, 0.95)
                        ui_app.after(0, lambda a=amplitude: ui_app.scanner.set_talk_amplitude(a))
                        time.sleep(0.08)
                threading.Thread(target=modulate_amplitude, daemon=True).start()

            def speak_end() -> None:
                speaking_active[0] = False
                ui_app.after(0, lambda: ui_app.draw_voice_indicator("gray"))
                ui_app.after(0, lambda: ui_app.status_label.configure(
                    text="VANGUARD CORE: ACTIVE", text_color="#33FF33"
                ))
                ui_app.after(0, lambda: ui_app.scanner.set_mode("scan"))
                
                # Resume background speech recognition
                if voice_recognizer and voice_recognizer.wake_word_enabled and not voice_recognizer.mute_mode:
                    voice_recognizer.start_background_listening()

            # Execute speech in background thread
            if voice_synthesizer:
                voice_synthesizer.speak(clean_text, on_start_callback=speak_start, on_end_callback=speak_end)
            else:
                speak_end()

        def on_error(error_msg: str) -> None:
            # Log error
            logger.error(error_msg)
            
            # Print error to screen and reset UI states
            ui_app.after(0, lambda: ui_app.console_print(error_msg, prefix="[SYSTEM] >> "))
            ui_app.after(0, lambda: ui_app.set_thinking_state(False))
            ui_app.after(0, lambda: ui_app.scanner.set_mode("scan"))

        # Trigger AI Stream worker in background thread
        ai_engine.send_message_stream(
            user_message=message,
            chunk_callback=on_chunk,
            complete_callback=on_complete,
            error_callback=on_error
        )

    def handle_transcription(text: str) -> None:
        """Callback triggered when SpeechRecognizer delivers a transcribed query."""
        ui_app.after(0, lambda: ui_app.input_entry.delete(0, 'end'))
        ui_app.after(0, lambda: ui_app.input_entry.insert(0, text))
        ui_app.after(0, lambda: ui_app.send_message())

    def handle_voice_status(status_msg: str, is_active: bool) -> None:
        """Updates UI indicator and status bar based on voice engine transitions."""
        ui_app.after(0, lambda: ui_app.set_listening_state(is_active))
        ui_app.after(0, lambda: ui_app.status_label.configure(
            text=f"VANGUARD CORE: {status_msg}",
            text_color="#FF3333" if is_active else "#33FF33"
        ))

    def handle_mic() -> None:
        """Triggers the active single listener microphone capture."""
        if voice_recognizer:
            voice_recognizer.trigger_single_listen()

    def handle_shutdown() -> None:
        """Callback to release locks and save files before UI shuts down."""
        logger.info("Performing subsystem shutdown procedures...")
        if voice_recognizer:
            voice_recognizer.stop_background_listening()
        # Explicitly delete the pyttsx3 engine proxy during active namespaces to prevent GC warnings on exit
        if voice_synthesizer and voice_synthesizer.engine:
            try:
                del voice_synthesizer.engine
            except:
                pass
        db.close()
        logger.info("VANGUARD System Shutdown complete.")

    # Create and run CustomTkinter Application
    ui_app = VanguardUI(
        config_manager=config,
        db_manager=db,
        on_send_callback=handle_send,
        on_mic_callback=handle_mic,
        on_shutdown_callback=handle_shutdown
    )
    
    # Initialize Voice and Plugin subsystems with active UI context callbacks
    global voice_recognizer, voice_synthesizer, plugin_manager
    voice_synthesizer = SpeechSynthesizer(config_manager=config)
    plugin_manager = PluginManager(config_manager=config, db_manager=db)
    voice_recognizer = SpeechRecognizer(
        config_manager=config,
        on_transcription=handle_transcription,
        on_status_change=handle_voice_status
    )
    
    ui_app.mainloop()

if __name__ == "__main__":
    main()

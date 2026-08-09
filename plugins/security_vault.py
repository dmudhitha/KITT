"""
Security Vault and Text Encryption Plugin for VANGUARD AI Assistant.
Encodes and decodes target text strings using base64 cipher algorithms.
"""
import base64
import logging
from typing import List, Dict, Any
from commands import BasePlugin
from utils import play_sound_async

logger = logging.getLogger("vanguard.commands.security_vault")


class SecurityVaultPlugin(BasePlugin):
    """Executes text string encryption and decryption operations."""

    @property
    def name(self) -> str:
        return "SecurityVault"

    @property
    def description(self) -> str:
        return "Encodes and decodes target text strings using security ciphers."

    @property
    def commands(self) -> List[str]:
        return ["encrypt text", "decrypt text", "security vault", "vault"]

    def execute(self, trigger: str, args: str, context: Dict[str, Any]) -> str:
        text = args.strip()
        if not text:
            play_sound_async("assets/sounds/error.wav")
            return "SECURITY VAULT NOTICE: Provide text to encrypt/decrypt (e.g., 'encrypt text my secret code')."

        if "decrypt" in trigger.lower() or "decrypt" in text.lower():
            try:
                # Decrypt
                cipher_str = text.replace("decrypt", "").strip()
                decoded_bytes = base64.b64decode(cipher_str.encode("utf-8"))
                original_text = decoded_bytes.decode("utf-8")
                play_sound_async("assets/sounds/plugin.wav")
                return f"SECURITY VAULT DECRYPTION SUCCESSFUL: Decoded Text = '{original_text}'"
            except Exception as e:
                play_sound_async("assets/sounds/error.wav")
                return f"SECURITY VAULT DECRYPTION ERROR: Invalid ciphertext ({e})."
        else:
            try:
                # Encrypt
                cipher_bytes = base64.b64encode(text.encode("utf-8"))
                encoded_str = cipher_bytes.decode("utf-8")
                play_sound_async("assets/sounds/plugin.wav")
                logger.info("Encrypted text string in security vault.")
                return f"SECURITY VAULT ENCRYPTION SUCCESSFUL: Ciphertext = '{encoded_str}'"
            except Exception as e:
                play_sound_async("assets/sounds/error.wav")
                return f"SECURITY VAULT ERROR: Encryption failed ({e})."

import os
import subprocess
import tempfile
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class AudioConverter:
    """Utility class for converting audio formats to WAV"""
    
    @staticmethod
    def convert_to_wav(audio_data: bytes, input_format: str = None) -> Optional[bytes]:
        """
        Convert audio data to WAV format using ffmpeg
        
        Args:
            audio_data: Raw audio data
            input_format: Format hint (e.g., 'webm', 'mp3', 'opus')
            
        Returns:
            WAV audio data as bytes, or None if conversion fails
        """
        try:
            # Create temporary input file
            with tempfile.NamedTemporaryFile(suffix=f'.{input_format or "audio"}', delete=False) as temp_input:
                temp_input.write(audio_data)
                temp_input_path = temp_input.name
            
            # Create temporary output file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_output:
                temp_output_path = temp_output.name
            
            try:
                # Build ffmpeg command
                cmd = [
                    'ffmpeg',
                    '-i', temp_input_path,
                    '-acodec', 'pcm_s16le',  # 16-bit PCM
                    '-ar', '16000',           # 16kHz sample rate
                    '-ac', '1',               # Mono channel
                    '-y',                     # Overwrite output file
                    temp_output_path
                ]
                
                logger.info(f"Running ffmpeg command: {' '.join(cmd)}")
                
                # Run ffmpeg conversion
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30  # 30 second timeout
                )
                
                if result.returncode == 0:
                    # Read the converted WAV file
                    with open(temp_output_path, 'rb') as wav_file:
                        wav_data = wav_file.read()
                    
                    logger.info(f"Successfully converted audio to WAV: {len(wav_data)} bytes")
                    return wav_data
                else:
                    logger.error(f"FFmpeg conversion failed: {result.stderr}")
                    return None
                    
            finally:
                # Clean up temporary files
                try:
                    os.unlink(temp_input_path)
                    os.unlink(temp_output_path)
                except Exception as e:
                    logger.warning(f"Error cleaning up temp files: {e}")
                    
        except Exception as e:
            logger.error(f"Error in audio conversion: {e}")
            return None
    
    @staticmethod
    def detect_audio_format(audio_data: bytes) -> Optional[str]:
        """
        Detect audio format from file headers
        
        Args:
            audio_data: Raw audio data
            
        Returns:
            Detected format string or None
        """
        if len(audio_data) < 12:
            return None
            
        # Check for WAV format
        if audio_data.startswith(b'RIFF') and b'WAVE' in audio_data[:12]:
            return 'wav'
        
        # Check for WebM format
        if audio_data.startswith(b'\x1a\x45\xdf\xa3'):
            return 'webm'
        
        # Check for MP3 format
        if audio_data.startswith(b'\xff\xfb') or audio_data.startswith(b'ID3'):
            return 'mp3'
        
        # Check for OGG format
        if audio_data.startswith(b'OggS'):
            return 'ogg'
        
        # Check for FLAC format
        if audio_data.startswith(b'fLaC'):
            return 'flac'
        
        # Check for M4A/AAC format
        if audio_data.startswith(b'\x00\x00\x00') and b'ftyp' in audio_data[:16]:
            return 'm4a'
        
        return None
    
    @staticmethod
    def is_wav_format(audio_data: bytes) -> bool:
        """Check if audio data is already in WAV format"""
        return AudioConverter.detect_audio_format(audio_data) == 'wav'
    
    @staticmethod
    def convert_audio_to_wav(audio_data: bytes) -> Optional[bytes]:
        """
        Convert any audio format to WAV
        
        Args:
            audio_data: Raw audio data in any format
            
        Returns:
            WAV audio data as bytes, or None if conversion fails
        """
        # Check if already WAV format
        if AudioConverter.is_wav_format(audio_data):
            logger.info("Audio data is already in WAV format")
            return audio_data
        
        # Detect format
        detected_format = AudioConverter.detect_audio_format(audio_data)
        if detected_format:
            logger.info(f"Detected audio format: {detected_format}")
        else:
            logger.warning("Could not detect audio format, attempting conversion anyway")
            detected_format = None
        
        # Convert to WAV
        return AudioConverter.convert_to_wav(audio_data, detected_format) 
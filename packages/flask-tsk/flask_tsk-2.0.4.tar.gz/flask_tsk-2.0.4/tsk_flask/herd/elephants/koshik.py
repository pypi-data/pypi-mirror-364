"""
TuskPHP Koshik - The Speaking Notification System (Python Edition)
================================================================

🐘 BACKSTORY: Koshik - The Elephant Who Learned to Speak
--------------------------------------------------------
Koshik, an Asian elephant at the Everland Zoo in South Korea, amazed the
world by learning to "speak" Korean words. By placing his trunk in his mouth
and modulating his vocal tract, Koshik could mimic human speech, saying
words like "annyong" (hello), "anja" (sit down), "aniya" (no), "nuo" (lie
down), and "choah" (good). Scientists believe he learned to vocalize to bond
with his human keepers, as he was the only elephant at the zoo for years.

WHY THIS NAME: Like Koshik who bridged the communication gap between elephants
and humans, this notification system creates audio alerts and spoken messages
for your users. Whether it's a simple "ding" or complex voice notifications,
Koshik helps your application speak to users in ways they'll understand and
remember.

"Annyong!" - Koshik's greeting to the world

FEATURES:
- Client-side audio generation
- Text-to-speech capabilities
- Custom notification sounds
- Multi-language support
- Audio sprite management
- Volume control and muting
- Notification queuing

@package TuskPHP\Elephants
@author  TuskPHP Team
@since   2.0.0
"""

import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue

# Flask-TSK imports
try:
    from tsk_flask.database import TuskDb
    from tsk_flask.memory import Memory
    from tsk_flask.utils import PermissionHelper
except ImportError:
    # Fallback for standalone usage
    TuskDb = None
    Memory = None
    PermissionHelper = None


class SoundType(Enum):
    """Sound type enumeration"""
    DEFAULT = "default"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    MESSAGE = "message"
    ANNYONG = "annyong"


class Language(Enum):
    """Language enumeration"""
    KOREAN = "ko"
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    JAPANESE = "ja"
    CHINESE = "zh"


@dataclass
class AudioConfig:
    """Audio configuration data structure"""
    volume: float = 0.7
    language: str = "en"
    rate: float = 1.0
    pitch: float = 1.0
    voice: str = "koshik"


@dataclass
class Notification:
    """Notification data structure"""
    id: str
    user_id: int
    action: str
    sound_type: str
    message: str
    created_at: int
    played: bool = False
    options: Dict = None

    def __post_init__(self):
        if self.options is None:
            self.options = {}


class Koshik:
    """The Speaking Notification System"""
    
    def __init__(self, config: Dict = None):
        """
        Initialize Koshik - The elephant prepares to speak
        
        Args:
            config: Configuration dictionary
        """
        self.vocabulary = {}
        self.volume = 0.7
        self.language = "en"
        self.voice_profiles = {}
        self.audio_queue = queue.Queue()
        self.sound_bank = {}
        
        # Load configuration
        self._load_config(config)
        
        # Learn vocabulary
        self._learn_basic_vocabulary()
        
        # Prepare audio system
        self._prepare_audio_system()
        
        # Start audio processing thread
        self._start_audio_processing()
    
    def speak(self, message: str, options: Dict = None) -> Dict:
        """
        Speak a message - Koshik vocalizes
        
        Args:
            message: Message to speak
            options: Speech options
            
        Returns:
            Dict with speech configuration
        """
        options = options or {}
        voice = options.get('voice', 'koshik')
        language = options.get('language', self.language)
        emotion = options.get('emotion', 'friendly')
        
        # Generate speech configuration
        speech_config = {
            'text': message,
            'voice': self._select_voice(voice, language),
            'rate': options.get('rate', 1.0),
            'pitch': options.get('pitch', 1.0),
            'volume': options.get('volume', self.volume)
        }
        
        # Create the vocalization
        audio = self._generate_speech(speech_config)
        
        # Remember what Koshik said
        self._remember_utterance(message, language)
        
        return audio
    
    def notify(self, sound_type: str = 'default', options: Dict = None) -> str:
        """
        Create notification sound - Koshik's alert trumpet
        
        Args:
            sound_type: Type of notification sound
            options: Sound options
            
        Returns:
            JavaScript code for audio playback
        """
        options = options or {}
        
        # Koshik's different notification sounds
        sounds = {
            'default': self._create_trumpet(440, 0.2),     # A4 note
            'success': self._create_happy_sound(),          # Rising tone
            'warning': self._create_warning_sound(),        # Two quick notes
            'error': self._create_error_sound(),            # Descending tone
            'message': self._create_message_sound(),        # Gentle chime
            'annyong': self._create_annyong_sound()        # Koshik's hello!
        }
        
        sound_data = sounds.get(sound_type, sounds['default'])
        
        # Apply options
        if 'volume' in options:
            sound_data['volume'] = options['volume']
        
        return self._generate_audio_script(sound_data)
    
    def say(self, word: str, language: str = 'en') -> str:
        """
        Text to speech - Koshik attempts human language
        
        Args:
            word: Word to say
            language: Language code
            
        Returns:
            JavaScript code for TTS
        """
        # Check if Koshik knows this word
        if language in self.vocabulary and word in self.vocabulary[language]:
            pronunciation = self.vocabulary[language][word]
            
            # Generate speech synthesis script
            return self._generate_tts_script(pronunciation, language)
        
        # Koshik doesn't know this word yet
        return self.notify('default', {'message': 'Koshik is still learning!'})
    
    def play_melody(self, melody: List, options: Dict = None) -> str:
        """
        Generate musical sequence - Koshik plays a melody
        
        Args:
            melody: List of musical notes
            options: Melody options
            
        Returns:
            JavaScript code for melody playback
        """
        options = options or {}
        tempo = options.get('tempo', 120)  # BPM
        key = options.get('key', 'C')  # Musical key
        scale = options.get('scale', 'major')  # major/minor/pentatonic
        
        # Convert note names to frequencies
        notes = self._convert_melody_to_frequencies(melody, key, scale)
        
        # Create sequence configuration
        sequence = {
            'type': 'melody',
            'notes': notes,
            'tempo': tempo,
            'instrument': options.get('instrument', 'sine'),
            'effects': options.get('effects', {'reverb': {'roomSize': 0.6}})
        }
        
        return self._generate_melody_script(sequence)
    
    def get_vocabulary_stats(self) -> Dict:
        """
        Get Koshik's stats - What has he learned?
        
        Returns:
            Dict with vocabulary statistics
        """
        return {
            'languages_known': list(self.vocabulary.keys()),
            'total_words': sum(len(words) for words in self.vocabulary.values()),
            'korean_words': len(self.vocabulary.get('ko', [])),
            'most_said': Memory.recall('koshik_most_said') if Memory else 'annyong',
            'utterance_count': Memory.recall('koshik_utterance_count') if Memory else 0
        }
    
    def learn_new_word(self, word: str, pronunciation: str, language: str = 'ko', context: Dict = None) -> Dict:
        """
        Language learning mode - Teach Koshik new words
        
        Args:
            word: Word to learn
            pronunciation: How to pronounce it
            language: Language code
            context: Learning context
            
        Returns:
            Dict with learning results
        """
        context = context or {}
        
        # Add to vocabulary
        if language not in self.vocabulary:
            self.vocabulary[language] = {}
        
        self.vocabulary[language][word] = pronunciation
        
        # Create learning record
        learning = {
            'word': word,
            'pronunciation': pronunciation,
            'language': language,
            'learned_at': int(time.time()),
            'context': context,
            'practice_count': 0
        }
        
        # Store in memory
        if Memory:
            learning_key = f"koshik_learning_{language}_{word}"
            Memory.remember(learning_key, learning, 86400 * 365)  # Remember for a year
            
            # Update vocabulary cache
            Memory.remember('koshik_vocabulary', self.vocabulary, 86400)
        
        return {
            'success': True,
            'message': f"Koshik learned: {word} = {pronunciation}",
            'total_words': len(self.vocabulary[language])
        }
    
    def practice_pronunciation(self, word: str, language: str = 'ko') -> Dict:
        """
        Practice pronunciation - Koshik practices speaking
        
        Args:
            word: Word to practice
            language: Language code
            
        Returns:
            Dict with practice session
        """
        if language not in self.vocabulary or word not in self.vocabulary[language]:
            return {
                'success': False,
                'message': 'Koshik doesn\'t know this word yet'
            }
        
        pronunciation = self.vocabulary[language][word]
        
        # Generate practice session
        practice = {
            'word': word,
            'pronunciation': pronunciation,
            'slow_speed': self._generate_tts_script(pronunciation, language, {'rate': 0.6}),
            'normal_speed': self._generate_tts_script(pronunciation, language, {'rate': 0.9}),
            'with_emphasis': self._generate_tts_script(pronunciation, language, {'pitch': 1.2, 'rate': 0.8})
        }
        
        # Update practice count
        if Memory:
            learning_key = f"koshik_learning_{language}_{word}"
            learning = Memory.recall(learning_key)
            if learning:
                learning['practice_count'] += 1
                Memory.remember(learning_key, learning, 86400 * 365)
        
        return practice
    
    def queue_notification(self, user_id: int, action: str, options: Dict = None) -> str:
        """
        Queue a notification for the user
        
        Args:
            user_id: User ID
            action: Action type
            options: Notification options
            
        Returns:
            Notification ID
        """
        options = options or {}
        
        # Create notification data
        notification = Notification(
            id=f"koshik_{int(time.time())}_{user_id}",
            user_id=user_id,
            action=action,
            sound_type=self._determine_sound_type(action),
            message=self._generate_message(action),
            created_at=int(time.time()),
            options=options
        )
        
        # Get current user's notification queue
        if Memory:
            queue_key = f"koshik_queue_{user_id}"
            queue_data = Memory.recall(queue_key) or []
            
            # Add new notification
            queue_data.append(asdict(notification))
            
            # Keep only last 5 notifications
            queue_data = queue_data[-5:]
            
            # Store updated queue (expire in 1 hour)
            Memory.remember(queue_key, queue_data, 3600)
        
        return notification.id
    
    def get_pending_notifications(self, user_id: int) -> List[Dict]:
        """
        Get pending notifications for user
        
        Args:
            user_id: User ID
            
        Returns:
            List of pending notifications
        """
        if not Memory:
            return []
        
        queue_key = f"koshik_queue_{user_id}"
        queue_data = Memory.recall(queue_key) or []
        
        # Return only unplayed notifications
        return [n for n in queue_data if not n.get('played', False)]
    
    def mark_as_played(self, user_id: int, notification_id: str) -> bool:
        """
        Mark notification as played
        
        Args:
            user_id: User ID
            notification_id: Notification ID
            
        Returns:
            True if marked successfully
        """
        if not Memory:
            return False
        
        queue_key = f"koshik_queue_{user_id}"
        queue_data = Memory.recall(queue_key) or []
        
        # Find and mark as played
        for notification in queue_data:
            if notification['id'] == notification_id:
                notification['played'] = True
                break
        
        # Update queue
        Memory.remember(queue_key, queue_data, 3600)
        return True
    
    def clear_notifications(self, user_id: int) -> bool:
        """
        Clear all notifications for user
        
        Args:
            user_id: User ID
            
        Returns:
            True if cleared successfully
        """
        if Memory:
            queue_key = f"koshik_queue_{user_id}"
            Memory.forget(queue_key)
        return True
    
    def get_user_preferences(self, user_id: int) -> Dict:
        """
        Get user's audio preferences
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with user preferences
        """
        if not Memory:
            return self._get_default_preferences()
        
        prefs_key = f"koshik_prefs_{user_id}"
        return Memory.recall(prefs_key) or self._get_default_preferences()
    
    def update_user_preferences(self, user_id: int, preferences: Dict) -> Dict:
        """
        Update user's audio preferences
        
        Args:
            user_id: User ID
            preferences: New preferences
            
        Returns:
            Updated preferences
        """
        if not Memory:
            return preferences
        
        prefs_key = f"koshik_prefs_{user_id}"
        current = self.get_user_preferences(user_id)
        updated = {**current, **preferences}
        
        Memory.remember(prefs_key, updated, 86400 * 30)  # 30 days
        return updated
    
    def export_configuration(self) -> Dict:
        """
        Export audio configuration for client
        
        Returns:
            Dict with configuration
        """
        return {
            'version': '2.0',
            'capabilities': {
                'tts': True,
                'synthesis': True,
                'effects': ['reverb', 'delay', 'distortion'],
                'languages': list(self.vocabulary.keys()),
                'melodies': True,
                'nature_sounds': True,
                'binaural': True,
                'games': True
            },
            'settings': {
                'volume': self.volume,
                'language': self.language,
                'voice_profiles': self.voice_profiles
            },
            'vocabulary_stats': self.get_vocabulary_stats(),
            'api_endpoint': '/api/koshik'
        }
    
    def _load_config(self, config: Dict = None):
        """Load configuration"""
        config = config or {}
        self.volume = config.get('volume', 0.7)
        self.language = config.get('language', 'en')
    
    def _learn_basic_vocabulary(self):
        """Learn basic vocabulary - Koshik's Korean lessons"""
        self.vocabulary = {
            'ko': {
                # Original Koshik words
                'hello': 'annyong',
                'sit': 'anja',
                'no': 'aniya',
                'lie_down': 'nuo',
                'good': 'choah',
                'goodbye': 'annyeonghi gaseyo',
                'thank_you': 'gamsahamnida',
                'yes': 'ne',
                'please': 'jebal',
                'sorry': 'mianhae',
                'love': 'saranghae',
                'friend': 'chingu',
                'elephant': 'kokkiri',
                'water': 'mul',
                'food': 'eumsik',
                'play': 'nolda',
                'sleep': 'jada',
                'happy': 'haengbokhae',
                'beautiful': 'areumdawo',
                'strong': 'himdeulda',
                'smart': 'ttokttokhada'
            },
            'en': {
                'hello': 'hello',
                'goodbye': 'goodbye',
                'yes': 'yes',
                'no': 'no',
                'good': 'good',
                'thank_you': 'thank you',
                'please': 'please',
                'sorry': 'sorry',
                'love': 'love',
                'friend': 'friend',
                'elephant': 'elephant',
                'happy': 'happy',
                'play': 'play',
                'help': 'help',
                'welcome': 'welcome',
                'amazing': 'amazing',
                'wonderful': 'wonderful',
                'excellent': 'excellent',
                'perfect': 'perfect',
                'beautiful': 'beautiful'
            }
        }
        
        # Cache the vocabulary
        if Memory:
            Memory.remember('koshik_vocabulary', self.vocabulary, 86400)
    
    def _prepare_audio_system(self):
        """Prepare audio system - Initialize Koshik's voice capabilities"""
        # Initialize audio configuration
        self.audio_context = {
            'sampleRate': 44100,
            'channels': 2,
            'bitDepth': 16,
            'format': 'webm',
            'codec': 'opus'
        }
        
        # Load voice profiles for different languages
        self._load_voice_profiles()
        
        # Cache audio system state
        if Memory:
            Memory.remember('koshik_audio_system', self.audio_context, 3600)
    
    def _load_voice_profiles(self):
        """Load voice profiles for multiple languages"""
        self.voice_profiles = {
            'en': {
                'male': {'pitch': 1.0, 'rate': 1.0, 'voice': 'en-US-Standard-B'},
                'female': {'pitch': 1.2, 'rate': 1.0, 'voice': 'en-US-Standard-C'},
                'koshik': {'pitch': 0.9, 'rate': 0.85, 'voice': 'en-US-Wavenet-D'}
            },
            'ko': {
                'male': {'pitch': 1.0, 'rate': 0.9, 'voice': 'ko-KR-Standard-A'},
                'female': {'pitch': 1.15, 'rate': 0.95, 'voice': 'ko-KR-Standard-B'},
                'koshik': {'pitch': 0.85, 'rate': 0.8, 'voice': 'ko-KR-Wavenet-A'}
            }
        }
    
    def _select_voice(self, voice: str, language: str) -> Dict:
        """Select appropriate voice for the message"""
        # Default to English if language not supported
        if language not in self.voice_profiles:
            language = 'en'
        
        # Get voice profile
        if voice in self.voice_profiles[language]:
            return self.voice_profiles[language][voice]
        
        # Default to Koshik's special voice
        return self.voice_profiles[language]['koshik']
    
    def _generate_speech(self, config: Dict) -> Dict:
        """Generate speech configuration for TTS"""
        speech_data = {
            'id': f"koshik_speech_{int(time.time())}",
            'text': config['text'],
            'voice': config['voice'],
            'audioConfig': {
                'audioEncoding': self.audio_context['codec'],
                'speakingRate': config['rate'],
                'pitch': config['pitch'],
                'volumeGainDb': self._convert_volume_to_db(config['volume']),
                'sampleRateHertz': self.audio_context['sampleRate']
            },
            'timestamp': int(time.time())
        }
        
        # Cache the speech configuration
        if Memory:
            Memory.remember(f"koshik_speech_{speech_data['id']}", speech_data, 300)
        
        return speech_data
    
    def _generate_audio_script(self, config: Dict) -> str:
        """Generate client-side audio - Koshik's voice box"""
        return f"""
<script>
(function() {{
    // Koshik's Audio Generator
    const KoshikSpeak = {{
        context: null,
        
        init: function() {{
            if (!this.context) {{
                this.context = new (window.AudioContext || window.webkitAudioContext)();
            }}
        }},
        
        playSound: function(frequency, duration, type = 'sine') {{
            this.init();
            
            const oscillator = this.context.createOscillator();
            const gainNode = this.context.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(this.context.destination);
            
            oscillator.frequency.value = frequency;
            oscillator.type = type;
            
            gainNode.gain.setValueAtTime({config.get('volume', 0.7)}, this.context.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, this.context.currentTime + duration);
            
            oscillator.start(this.context.currentTime);
            oscillator.stop(this.context.currentTime + duration);
        }},
        
        trumpet: function() {{
            // Koshik's signature elephant trumpet
            this.playSound({config.get('frequency', 440)}, {config.get('duration', 0.2)});
        }}
    }};
    
    // Play the sound
    KoshikSpeak.trumpet();
    
    // Koshik says: "{config.get('message', 'annyong!')}"
}})();
</script>
"""
    
    def _generate_tts_script(self, text: str, language: str, options: Dict = None) -> str:
        """Generate TTS script - Modern speech synthesis"""
        options = options or {}
        rate = options.get('rate', 0.9)
        pitch = options.get('pitch', 1.1)
        volume = options.get('volume', self.volume)
        
        return f"""
<script>
(function() {{
    // Koshik's Text-to-Speech
    const utterance = new SpeechSynthesisUtterance('{text}');
    utterance.lang = '{language}';
    utterance.rate = {rate};
    utterance.pitch = {pitch};
    utterance.volume = {volume};
    
    // Koshik speaks!
    window.speechSynthesis.speak(utterance);
    
    console.log('🐘 Koshik says: "{text}"');
}})();
</script>
"""
    
    def _generate_melody_script(self, sequence: Dict) -> str:
        """Generate melody script for browser playback"""
        notes_json = json.dumps(sequence['notes'])
        tempo = sequence['tempo']
        effects = json.dumps(sequence.get('effects', {}))
        
        return f"""
<script>
(function() {{
    // Koshik's Melody Player
    const KoshikMelody = {{
        context: new (window.AudioContext || window.webkitAudioContext)(),
        tempo: {tempo},
        notes: {notes_json},
        effects: {effects},
        
        playMelody: function() {{
            let time = this.context.currentTime;
            const beatDuration = 60 / this.tempo;
            
            this.notes.forEach((note, index) => {{
                const oscillator = this.context.createOscillator();
                const gainNode = this.context.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(this.context.destination);
                
                oscillator.frequency.value = note.frequency;
                oscillator.type = '{sequence.get("instrument", "sine")}';
                
                // Set envelope
                gainNode.gain.setValueAtTime(0, time);
                gainNode.gain.linearRampToValueAtTime(note.velocity * {self.volume}, time + 0.01);
                gainNode.gain.exponentialRampToValueAtTime(0.01, time + note.duration * beatDuration);
                
                oscillator.start(time);
                oscillator.stop(time + note.duration * beatDuration);
                
                time += note.duration * beatDuration;
            }});
            
            console.log('🐘 Koshik plays a melody!');
        }}
    }};
    
    // Play the melody
    KoshikMelody.playMelody();
}})();
</script>
"""
    
    def _create_trumpet(self, frequency: float, duration: float) -> Dict:
        """Create trumpet sound - Koshik's signature"""
        return {
            'type': 'complex',
            'frequency': frequency,
            'duration': duration,
            'harmonics': [1.0, 0.8, 0.6, 0.4, 0.2],
            'volume': self.volume,
            'message': 'Koshik trumpets!'
        }
    
    def _create_happy_sound(self) -> Dict:
        """Create happy sound - When Koshik says 'choah' (good)"""
        return {
            'type': 'sequence',
            'notes': [
                {'frequency': 523.25, 'duration': 0.1},  # C5
                {'frequency': 659.25, 'duration': 0.1},  # E5
                {'frequency': 783.99, 'duration': 0.2},  # G5
            ],
            'volume': self.volume,
            'message': 'choah!'
        }
    
    def _create_warning_sound(self) -> Dict:
        """Create warning sound - When Koshik says 'aniya' (no)"""
        return {
            'type': 'sequence',
            'notes': [
                {'frequency': 440, 'duration': 0.15},  # A4
                {'frequency': 440, 'duration': 0.15},  # A4
            ],
            'volume': self.volume,
            'message': 'aniya!'
        }
    
    def _create_error_sound(self) -> Dict:
        """Create error sound - Descending tone"""
        return {
            'type': 'sequence',
            'notes': [
                {'frequency': 587.33, 'duration': 0.2},  # D5
                {'frequency': 493.88, 'duration': 0.2},  # B4
                {'frequency': 392.00, 'duration': 0.3},  # G4
            ],
            'volume': self.volume * 0.8,
            'message': 'aniya!'  # No!
        }
    
    def _create_message_sound(self) -> Dict:
        """Create message sound - Gentle chime"""
        return {
            'type': 'chord',
            'frequencies': [523.25, 659.25, 783.99, 1046.50],  # C5 E5 G5 C6
            'duration': 0.6,
            'volume': self.volume * 0.6,
            'message': 'saranghae'  # Love (in Korean)
        }
    
    def _create_annyong_sound(self) -> Dict:
        """Create Annyong sound - Koshik's greeting"""
        return {
            'type': 'modulated',
            'baseFrequency': 440,
            'modulation': {
                'type': 'frequency',
                'depth': 50,
                'rate': 8,
                'shape': 'sine'
            },
            'duration': 0.5,
            'harmonics': [1.0, 0.5, 0.3],
            'volume': self.volume,
            'message': 'annyong!'  # Hello!
        }
    
    def _convert_melody_to_frequencies(self, melody: List, key: str, scale: str) -> List[Dict]:
        """Convert melody notation to frequencies"""
        # Musical note frequencies (A4 = 440Hz)
        note_frequencies = {
            'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13,
            'E': 329.63, 'F': 349.23, 'F#': 369.99, 'G': 392.00,
            'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88
        }
        
        frequencies = []
        
        for note in melody:
            if isinstance(note, dict):
                # Note with duration and octave
                pitch = note.get('pitch', 'C4')
                duration = note.get('duration', 0.25)
                octave = int(pitch[-1]) if pitch[-1].isdigit() else 4
                note_name = pitch[:-1]
                
                base_freq = note_frequencies.get(note_name, 440)
                frequency = base_freq * (2 ** (octave - 4))
                
                frequencies.append({
                    'frequency': frequency,
                    'duration': duration,
                    'velocity': note.get('velocity', 0.8)
                })
            else:
                # Simple note name
                frequencies.append({
                    'frequency': note_frequencies.get(note, 440),
                    'duration': 0.25,
                    'velocity': 0.8
                })
        
        return frequencies
    
    def _convert_volume_to_db(self, volume: float) -> float:
        """Convert volume (0-1) to decibels"""
        if volume <= 0:
            return -96
        return 20 * (volume ** 0.5)  # Simplified conversion
    
    def _remember_utterance(self, message: str, language: str):
        """Remember what was said - Koshik never forgets"""
        if not Memory:
            return
        
        count = Memory.recall('koshik_utterance_count') or 0
        Memory.remember('koshik_utterance_count', count + 1, 86400)
        
        Memory.remember("koshik_last_said", {
            'message': message,
            'language': language,
            'time': int(time.time())
        }, 3600)
    
    def _determine_sound_type(self, action: str) -> str:
        """Determine sound type based on action"""
        sound_map = {
            'login': 'welcome',
            'dashboard': 'soft_chime',
            'admin': 'authority',
            'manager': 'success',
            'editor': 'creative',
            'users': 'notification',
            'system': 'alert',
            'reports': 'completion',
            'team': 'group',
            'content': 'writing',
            'profile': 'personal',
            'settings': 'config',
            'error': 'warning',
            'success': 'celebration'
        }
        
        return sound_map.get(action, 'default')
    
    def _generate_message(self, action: str) -> str:
        """Generate Koshik's message for the action"""
        messages = {
            'login': 'annyong!',  # Koshik's hello
            'dashboard': 'choah!',  # Good!
            'admin': 'anja!',  # Attention!
            'manager': 'nuo',  # Ready
            'editor': 'choah',  # Good for writing
            'error': 'aniya!',  # No! (something wrong)
            'success': 'choah!',  # Good!
        }
        
        return messages.get(action, 'annyong')
    
    def _get_default_preferences(self) -> Dict:
        """Get default user preferences"""
        return {
            'enabled': True,
            'volume': 0.7,
            'sounds': {
                'login': True,
                'navigation': True,
                'notifications': True,
                'errors': True,
                'success': True
            },
            'language': 'en'
        }
    
    def _start_audio_processing(self):
        """Start background audio processing"""
        self.audio_thread = threading.Thread(target=self._audio_worker, daemon=True)
        self.audio_thread.start()
    
    def _audio_worker(self):
        """Background audio processing worker"""
        while True:
            try:
                # Process audio queue
                while not self.audio_queue.empty():
                    audio_task = self.audio_queue.get_nowait()
                    self._process_audio_task(audio_task)
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                print(f"Koshik audio worker error: {e}")
                time.sleep(5)
    
    def _process_audio_task(self, task: Dict):
        """Process a background audio task"""
        # Implementation for background audio processing
        pass


# Flask-TSK Integration Functions
def init_koshik(app):
    """Initialize Koshik with Flask app"""
    app.koshik = Koshik()
    return app.koshik


def get_koshik() -> Koshik:
    """Get Koshik instance from Flask app context"""
    from flask import current_app
    return current_app.koshik 
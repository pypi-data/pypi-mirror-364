"""
VoxTerm Menu System - Handle menu flow and navigation
Simplified to work with SessionManager
"""

import asyncio
from typing import Optional, Dict, Callable, Any
from dataclasses import dataclass
from enum import Enum

from .settings import TerminalSettings
from .session_manager import create_session
from .logger import logger, setup_logging, patch_print, restore_print


class MenuState(Enum):
    """Menu states"""
    MAIN = "main"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    SETTINGS = "settings"
    MODE_SELECT = "mode_select"
    VOICE_SELECT = "voice_select"
    IDENTITY_SELECT = "identity_select"
    EXITING = "exiting"


@dataclass
class MenuItem:
    """A menu item"""
    key: str
    label: str
    action: Optional[Callable] = None
    next_state: Optional[MenuState] = None


class VoxTermMenu:
    """Simplified menu system that uses SessionManager"""
    
    def __init__(self, engine: Any, settings: Optional[TerminalSettings] = None):
        self.engine = engine
        self.settings = settings or TerminalSettings()
        self.current_state = MenuState.MAIN
        self.running = True
        self.connected = False
        
        # Current selections
        self.current_mode = self.settings.default_mode
        self.current_voice = self.settings.voice.current_voice
        self.current_identity = self.settings.identity.current_identity
        
        # Menu definitions
        self.menus = self._create_menus()
        
    def _create_menus(self) -> Dict[MenuState, Dict[str, MenuItem]]:
        """Create all menu definitions"""
        return {
            MenuState.MAIN: {
                'a': MenuItem('a', 'Connect & Start', action=self._connect_and_start),
                'm': MenuItem('m', 'Mode', next_state=MenuState.MODE_SELECT),
                's': MenuItem('s', 'Settings', next_state=MenuState.SETTINGS),
                'q': MenuItem('q', 'Quit', action=self._quit),
            },
            
            MenuState.CONNECTED: {
                'd': MenuItem('d', self._get_start_label(), action=self._start_session),
                'm': MenuItem('m', 'Change Mode', next_state=MenuState.MODE_SELECT),
                'v': MenuItem('v', 'Change Voice', next_state=MenuState.VOICE_SELECT),
                'r': MenuItem('r', 'Restart Session', action=self._start_session),
                'q': MenuItem('q', 'Disconnect & Quit', action=self._quit),
            },
            
            MenuState.SETTINGS: {
                'v': MenuItem('v', 'Change Voice', next_state=MenuState.VOICE_SELECT),
                'p': MenuItem('p', 'Change Identity/Prompt', next_state=MenuState.IDENTITY_SELECT),
                'l': MenuItem('l', f'Logging to File: {"ON" if self.settings.log_to_file else "OFF"}', action=self._toggle_logging),
                'i': MenuItem('i', 'Info', action=self._show_info),
                'b': MenuItem('b', 'Back', action=self._go_back),
            },
            
            MenuState.MODE_SELECT: {
                '1': MenuItem('1', 'Push to Talk', action=lambda: self._set_mode('push_to_talk')),
                '2': MenuItem('2', 'Always On', action=lambda: self._set_mode('always_on')),
                '3': MenuItem('3', 'Text', action=lambda: self._set_mode('text')),
                '4': MenuItem('4', 'Turn Based', action=lambda: self._set_mode('turn_based')),
                'b': MenuItem('b', 'Back', action=self._go_back),
            },
            
            MenuState.VOICE_SELECT: {
                '1': MenuItem('1', 'Alloy', action=lambda: self._set_voice('alloy')),
                '2': MenuItem('2', 'Echo', action=lambda: self._set_voice('echo')),
                '3': MenuItem('3', 'Fable', action=lambda: self._set_voice('fable')),
                '4': MenuItem('4', 'Onyx', action=lambda: self._set_voice('onyx')),
                '5': MenuItem('5', 'Nova', action=lambda: self._set_voice('nova')),
                '6': MenuItem('6', 'Shimmer', action=lambda: self._set_voice('shimmer')),
                'b': MenuItem('b', 'Back', action=self._go_back),
            },
            
            MenuState.IDENTITY_SELECT: {
                '1': MenuItem('1', 'Default Assistant', action=lambda: self._set_identity('default')),
                '2': MenuItem('2', 'Voice Assistant', action=lambda: self._set_identity('voice_assistant')),
                '3': MenuItem('3', 'Conversational AI', action=lambda: self._set_identity('conversational')),
                '4': MenuItem('4', 'Customer Service', action=lambda: self._set_identity('customer_service')),
                '5': MenuItem('5', 'Transcription Service', action=lambda: self._set_identity('transcription')),
                '6': MenuItem('6', 'Audio Only', action=lambda: self._set_identity('audio_only')),
                'b': MenuItem('b', 'Back', action=self._go_back),
            },
        }
    
    def _get_start_label(self) -> str:
        """Get appropriate label for start button"""
        labels = {
            'text': 'Start Typing',
            'push_to_talk': 'Start Talking (Push-to-Talk)',
            'always_on': 'Start Listening',
            'turn_based': 'Start Turn-Based Chat'
        }
        return labels.get(self.current_mode, 'Start Session')
    
    def _clear_screen(self):
        """Clear the terminal screen"""
        print("\033[2J\033[H", end="")
    
    def _show_header(self):
        """Show VoxTerm header"""
        print("╔═══════════════════════════════════════╗")
        print("║          🎙️  VoxTerm v1.0            ║")
        print("╚═══════════════════════════════════════╝")
        print()
    
    def _show_current_state(self):
        """Show current state/settings"""
        if self.current_state == MenuState.MAIN:
            print(f"OpenAI, mode: {self.current_mode}, voice: {self.current_voice}")
            print(f"Identity: {self.current_identity}")
            if not self.connected:
                print("📡 Status: Not connected")
            print()
            
        elif self.current_state == MenuState.CONNECTED:
            print(f"✅ Connected | Mode: {self.current_mode} | Voice: {self.current_voice}")
            print(f"Identity: {self.current_identity}")
            print()
            
        elif self.current_state in [MenuState.SETTINGS, MenuState.MODE_SELECT, MenuState.VOICE_SELECT, MenuState.IDENTITY_SELECT]:
            print(f"Current: {self.current_mode} mode, {self.current_voice} voice")
            print(f"Identity: {self.current_identity}")
            print()
    
    def _show_menu(self):
        """Show current menu"""
        menu = self.menus.get(self.current_state, {})
        
        # Menu titles
        titles = {
            MenuState.MAIN: "🏠 Main Menu",
            MenuState.CONNECTED: "🎯 Ready to Chat",
            MenuState.SETTINGS: "⚙️  Settings",
            MenuState.MODE_SELECT: "🎮 Select Mode",
            MenuState.VOICE_SELECT: "🗣️  Select Voice",
            MenuState.IDENTITY_SELECT: "🤖 Select Identity"
        }
        
        if self.current_state in titles:
            print(f"{titles[self.current_state]}:")
            print()
        
        # Show menu items
        for key, item in menu.items():
            # Update dynamic labels
            if self.current_state == MenuState.CONNECTED and key == 'd':
                item.label = self._get_start_label()
            print(f"  [{key}] {item.label}")
        
        print()
        print("💡 Ctrl+C to force quit anytime")
    
    async def run(self):
        """Run the menu system"""
        self._clear_screen()
        
        # Setup logging based on current settings
        if self.settings.log_to_file:
            setup_logging(self.settings)
            patch_print()
            logger.log_event("SESSION", "VoxTerm menu started")
        
        while self.running:
            try:
                # Show interface
                self._show_header()
                self._show_current_state()
                self._show_menu()
                
                # Get input
                choice = await self._get_input()
                
                # Process choice
                await self._process_choice(choice)
                
                # Clear for next iteration
                if self.running:
                    self._clear_screen()
                    
            except KeyboardInterrupt:
                print("\n\n⚡ Force quit")
                self.running = False
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                await asyncio.sleep(2)
    
    async def _get_input(self) -> str:
        """Get user input"""
        loop = asyncio.get_event_loop()
        choice = await loop.run_in_executor(None, input, "> ")
        return choice.lower().strip()
    
    async def _process_choice(self, choice: str):
        """Process menu choice"""
        menu = self.menus.get(self.current_state, {})
        
        if choice not in menu:
            print("❌ Invalid choice")
            await asyncio.sleep(1)
            return
        
        item = menu[choice]
        
        # Execute action if any
        if item.action:
            result = await self._execute_action(item.action)
            if result is False:  # Action failed
                return
        
        # Change state if specified
        if item.next_state:
            self.current_state = item.next_state
    
    async def _execute_action(self, action: Callable) -> Any:
        """Execute an action"""
        if asyncio.iscoroutinefunction(action):
            return await action()
        else:
            return action()
    
    # Actions
    async def _connect_and_start(self):
        """Connect and immediately start a session"""
        if not self.connected:
            print("\n📡 Connecting...")
            if self.settings.log_to_file:
                logger.log_api_event("Attempting connection")
            try:
                await self.engine.connect()
                self.connected = True
                print("✅ Connected!")
                
                # Apply current identity settings after connection
                identity = self.settings.identity.get_current_identity()
                if identity and hasattr(self.engine, 'configure_session'):
                    from voicechatengine import SessionConfig
                    identity_config = SessionConfig.from_identity(identity)
                    await self.engine.configure_session(identity_config)
                    print(f"✅ Applied identity: {self.current_identity}")
                
                if self.settings.log_to_file:
                    logger.log_api_event("Connected successfully")
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"❌ Connection failed: {e}")
                if self.settings.log_to_file:
                    logger.log_event("ERROR", f"Connection failed: {e}")
                await asyncio.sleep(2)
                return False
        
        # Go directly to session
        await self._start_session()
        
        # After session ends, go to connected menu
        self.current_state = MenuState.CONNECTED
    
    async def _start_session(self):
        """Start a voice/text session using SessionManager"""
        self._clear_screen()
        self._show_header()
        
        print(f"🚀 Starting {self.current_mode} session...\n")
        
        if self.settings.log_to_file:
            logger.log_event("SESSION", f"Starting {self.current_mode} session")
        
        # Create session manager
        session = create_session(self.engine, self.current_mode, self.settings)
        
        try:
            # Start the session
            await session.start()
            
            # Run interactive loop
            await session.run_interactive()
            
            # Show session stats
            print(f"\n📊 Session Summary:")
            print(f"   Messages sent: {session.metrics.messages_sent}")
            print(f"   Messages received: {session.metrics.messages_received}")
            if session.metrics.errors > 0:
                print(f"   Errors: {session.metrics.errors}")
            print(f"   Duration: {session.metrics.duration:.1f}s")
            
            if self.settings.log_to_file:
                logger.log_event("SESSION", f"Session ended - Messages: {session.metrics.messages_sent}/{session.metrics.messages_received}, Duration: {session.metrics.duration:.1f}s")
            
        except Exception as e:
            print(f"\n❌ Session error: {e}")
            if self.settings.log_to_file:
                logger.log_event("ERROR", f"Session error: {e}")
        finally:
            # Always cleanup
            await session.stop()
            
        print("\n[Press ENTER to continue]")
        await asyncio.get_event_loop().run_in_executor(None, input, "")
        
        # Clear any buffered input
        await asyncio.sleep(0.1)
    
    def _set_mode(self, mode: str):
        """Set the interaction mode"""
        self.current_mode = mode
        print(f"✅ Mode changed to: {mode}")
        # Don't auto-go back, wait for user to press 'b'
    
    def _set_voice(self, voice: str):
        """Set the voice"""
        self.current_voice = voice
        if hasattr(self.engine, 'config'):
            self.engine.config.voice = voice
        print(f"✅ Voice changed to: {voice}")
        # Don't auto-go back, wait for user to press 'b'
    
    async def _set_identity(self, identity_name: str):
        """Set the identity (system prompt and behavior)"""
        self.current_identity = identity_name
        self.settings.identity.current_identity = identity_name
        
        # Get the identity object
        identity = self.settings.identity.get_current_identity()
        if identity:
            # Apply identity settings to engine config
            if hasattr(self.engine, 'config'):
                # Update the engine's session config with the identity
                from voicechatengine import SessionConfig
                new_config = SessionConfig.from_identity(identity)
                
                # Apply the key settings from identity
                self.engine.config.instructions = identity.prompt
                self.engine.config.temperature = identity.temperature
                self.engine.config.voice = identity.voice
                
                # Update our tracked voice to match identity
                self.current_voice = identity.voice
                
            # If connected, update the session configuration
            if self.connected and hasattr(self.engine, 'configure_session'):
                try:
                    from voicechatengine import SessionConfig
                    identity_config = SessionConfig.from_identity(identity)
                    await self.engine.configure_session(identity_config)
                    print(f"✅ Identity changed to: {identity_name}")
                    print(f"   Prompt: {identity.prompt[:50]}...")
                    print(f"   Voice: {identity.voice}, Temperature: {identity.temperature}")
                    print("   (Session updated)")
                except Exception as e:
                    print(f"⚠️  Failed to update session: {e}")
            else:
                print(f"✅ Identity changed to: {identity_name}")
                print(f"   Prompt: {identity.prompt[:50]}...")
                print(f"   Voice: {identity.voice}, Temperature: {identity.temperature}")
                if not self.connected:
                    print("   (Will apply on next connection)")
        else:
            print(f"⚠️  Identity '{identity_name}' not found")
        # Don't auto-go back, wait for user to press 'b'
    
    def _toggle_logging(self):
        """Toggle file logging on/off"""
        self.settings.log_to_file = not self.settings.log_to_file
        
        if self.settings.log_to_file:
            # Create log filename with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.settings.log_file_path = f"voxterm_log_{timestamp}.txt"
            print(f"✅ Logging enabled: {self.settings.log_file_path}")
            
            # Start logging immediately
            setup_logging(self.settings)
            patch_print()
            logger.log_event("SESSION", "Logging enabled from settings menu")
        else:
            print("✅ Logging disabled")
            if logger.enabled:
                logger.log_event("SESSION", "Logging disabled from settings menu")
                restore_print()
                logger.disable()
            self.settings.log_file_path = None
            
        # Update menu label
        self.menus[MenuState.SETTINGS]['l'].label = f'Logging to File: {"ON" if self.settings.log_to_file else "OFF"}'
    
    def _show_info(self):
        """Show info about VoxTerm"""
        print("\n" + "─" * 50)
        print("📖 About VoxTerm")
        print("─" * 50)
        print("\nVoxTerm is made so we can test voice API features")
        print("in better isolation, away from UI complexity.")
        print("\n" + "─" * 50)
        print("\nPress ENTER to continue...")
        asyncio.get_event_loop().run_in_executor(None, input, "")
    
    def _go_back(self):
        """Go back to previous menu"""
        if self.connected:
            self.current_state = MenuState.CONNECTED
        else:
            self.current_state = MenuState.MAIN
    
    def _quit(self):
        """Quit the application"""
        print("\n👋 Goodbye!")
        if self.settings.log_to_file:
            logger.log_event("SESSION", "User quit from menu")
        self.running = False
        if self.connected:
            asyncio.create_task(self._disconnect())
        
        # Clean up logging if enabled
        if logger.enabled:
            restore_print()
            logger.disable()
    
    async def _disconnect(self):
        """Disconnect from voice API"""
        try:
            await self.engine.disconnect()
        except:
            pass
# Source Generated with Decompyle++
# File: consts.pyc (Python 3.10)

from dataclasses import dataclass
from enum import Enum
MRPATCHER_TIMEOUT_S = 30
BANK_SIZE = 16384
BITMAP_REFRESH_INTERVAL_S = 1
NUM_WRITE_RETRIES = 3
LOADING_TEXT_INTERVAL_S = 4
LOADING_TEXT_DEFAULT = 'CHECKING YOUR GAME...'
LOADING_TEXT_SNIPPETS = [
    'LOADING NOSTALGIA...',
    'BLOWING INTO CARTRIDGE...',
    'GETTING TO A SAVE SPOT...',
    'SPAWNING MOBS...',
    'GENERATING SECRET LEVELS...',
    'LOOKING UP CHEAT CODES...',
    'ENTERING KONAMI CODE...',
    'ARGUING WITH THE SERVER...',
    'PRACTICING BOSS FIGHTS...',
    'BUFFERING IMAGINATION...',
    'POLISHING PIXELS...',
    'DOWNLOADING GOOD VIBES...',
    'COMPOSING CHIPTUNES...',
    'LOSING THE GAME...',
    'READING CARTRIDGE...',
    'MASHING BUTTONS...',
    'LEVELLING UP...',
    'SQUASHING BUGS...',
    'RESTORING HEALTH...',
    'POWERING UP...',
    'EQUIPPING GEAR...',
    'UNLOCKING ACHIEVEMENTS...',
    'BEATING HIGH SCORE...',
    'CHOOSING STARTER...',
    'FIGHTING GARY...',
    'EATING RARE CANDIES...',
    'CALLING MOM...',
    'HUNTING FOR SHINIES...',
    'LOOKING FOR WARP ZONES...',
    'STOMPING GOOMBAS...',
    'RESCUING THE PRINCESS...',
    'HURLING BLUE SHELLS...',
    'ROTATING BLOCKS...',
    'WAITING FOR AN I-PIECE...',
    'SMASHING POTS...',
    'WAKING THE WIND FISH...',
    'INHALING ENEMIES...',
    'WHIPPING HAIR...',
    'PRACTICING DK RAP...',
    'PEELING BANANAS...',
    'PETTING THE QUAKZALS...',
    'USHERING IN TRUE ZAHNBALA...',
    'SAILING THE SEVEN SEAS...',
    'ROCKING TO PIRATE METAL...',
    'EYEING A SUSPICIOUS BOX...',
    'STUDYING SPELLS...',
    'MIXING POTIONS...',
    'PLOTTING WORLD DOMINATION...',
    'LOOKING FOR WALDO...']

class CartClinicConfigItem(Enum, str):
    PREVIOUS_HOMEBREW_DIR = 'previous_homebrew_dir'
    PREVIOUS_SAVE_DIR = 'previous_save_dir'


class CartClinicFeature(Enum, str):
    DEVELOPER_MODE = 'mrupdater.cart-clinic:developer-mode'

CartClinicSaveOperationValue = dataclass(<NODE:12>)

class CartClinicSaveOperation(Enum):
    BACKUP = CartClinicSaveOperationValue(1, 'BACKING UP SAVE...', 'Your save will be backed up to the file specified. The save file may not work if you restore it after updating a game using Cart Clinic.\nYour Chromatic display will turn off and reset.\nDo you want to continue?', 'Your game save was successfully backed up!', **('value', 'status_message', 'warning_message', 'success_message'))
    RESTORE = CartClinicSaveOperationValue(2, 'RESTORING SAVE...', 'You are about to overwrite the save file stored on your cartridge. The save file may not work if it came from an older version of the game.\nYour Chromatic display will turn off and reset.\nDo you want to continue?', 'Your game save was successfully restored!', **('value', 'status_message', 'warning_message', 'success_message'))
    ERASE = CartClinicSaveOperationValue(3, 'ERASING SAVE...', 'You are about to erase the save file stored on your cartridge.\nYour Chromatic display will turn off and reset.\nDo you want to continue?', 'Your game save has been erased!', **('value', 'status_message', 'warning_message', 'success_message'))


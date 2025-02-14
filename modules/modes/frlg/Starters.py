import random
import struct
from typing import NoReturn

from modules.Config import config
from modules.Console import console
from modules.Gui import GetEmulator
from modules.Inputs import PressButton, WaitFrames
from modules.Memory import ReadSymbol, GameState, GetGameState, GetTask, WriteSymbol
from modules.Navigation import FollowPath
from modules.Pokemon import GetParty
from modules.Stats import GetRNGStateHistory, SaveRNGStateHistory, EncounterPokemon
from modules.Trainer import GetTrainer

session_pids = []
seen = 0
dupes = 0

if not config['cheats']['starters_rng']:
    rng_history = GetRNGStateHistory(config['general']['starter'])


def Starters() -> NoReturn:  # TODO `and config['general']['bot_mode'] != 'manual'` temporary until mode step refactor
    try:
        global dupes
        global seen

        while GetGameState() != GameState.OVERWORLD and config['general']['bot_mode'] != 'manual':
            PressButton(['A'])

        if config['cheats']['starters_rng']:
            WriteSymbol('gRngValue', struct.pack('<I', random.randint(0, 2 ** 32 - 1)))
            WaitFrames(1)
        else:
            rng = int(struct.unpack('<I', ReadSymbol('gRngValue', size=4))[0])
            while rng in rng_history['rng'] and config['general']['bot_mode'] != 'manual':
                WaitFrames(1)
                rng = int(struct.unpack('<I', ReadSymbol('gRngValue', size=4))[0])

        while GetTask('TASK_SCRIPTSHOWMONPIC') == {} and config['general']['bot_mode'] != 'manual':
            PressButton(['A'])

        while GetTask('TASK_SCRIPTSHOWMONPIC') != {} and config['general']['bot_mode'] != 'manual':
            PressButton(['A'])

        while GetTask('TASK_FANFARE') == {} and config['general']['bot_mode'] != 'manual':
            PressButton(['B'])

        if config['cheats']['starters']:
            while not GetParty() and config['general']['bot_mode'] != 'manual':
                PressButton(['B'])
        else:
            while GetTrainer()['facing'] != 'Down' and config['general']['bot_mode'] != 'manual':
                PressButton(['B', 'Down'])

            FollowPath([
                (GetTrainer()['coords'][0], 7),
                (7, 7),
                (7, 8)
            ])

            while GetTask('TASK_PLAYERCONTROLLER_RESTOREBGMAFTERCRY') == {} and config['general']['bot_mode'] != 'manual':
                PressButton(['B'])

        pokemon = GetParty()[0]
        seen += 1
        if pokemon['pid'] in session_pids:
            dupes += 1
            console.print('[red]Duplicate detected! {} [{}] has already been seen during this bot session, and will not be logged ({:.2f}% dupes this session).'.format(
                pokemon['name'],
                hex(pokemon['pid'])[2:],
                (dupes/seen)*100))
            console.print('[red]If you notice too many dupes or resets taking too long, consider enabling `starters_rng` in `config/cheats.yml`. Ctrl + click [link=https://github.com/40Cakes/pokebot-gen3#cheatsyml---cheats-config]here[/link] for more information on this cheat.\n')
        else:
            EncounterPokemon(pokemon)
            session_pids.append(pokemon['pid'])

        if not config['cheats']['starters_rng']:
            rng_history['rng'].append(rng)
            SaveRNGStateHistory(config['general']['starter'], rng_history)

        if config['general']['bot_mode'] != 'manual':
            GetEmulator().Reset()
    except SystemExit:
        raise
    except:
        console.print_exception(show_locals=True)

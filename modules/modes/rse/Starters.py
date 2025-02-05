import random
import struct
from typing import NoReturn

from modules.Config import config
from modules.Console import console
from modules.Gui import GetROM, GetEmulator
from modules.Inputs import PressButton, WaitFrames
from modules.Memory import ReadSymbol, GetGameState, GameState, GetTask, WriteSymbol
from modules.Pokemon import GetParty
from modules.Stats import GetRNGStateHistory, SaveRNGStateHistory, EncounterPokemon

if GetROM().game_title == 'POKEMON EMER':
    t_bag_cursor = 'TASK_HANDLESTARTERCHOOSEINPUT'
    t_confirm = 'TASK_HANDLECONFIRMSTARTERINPUT'
    t_ball_throw = 'TASK_PLAYCRYWHENRELEASEDFROMBALL'
else:
    t_bag_cursor = 'TASK_STARTERCHOOSE2'
    t_confirm = 'TASK_STARTERCHOOSE5'
    t_ball_throw = 'SUB_81414BC'

session_pids = []
seen = 0
dupes = 0

if not config['cheats']['starters_rng']:
    rng_history = GetRNGStateHistory(config['general']['starter'])


def Starters() -> NoReturn:  # TODO `and config['general']['bot_mode'] != 'manual'` temporary until mode step refactor
    try:
        global dupes
        global seen

        # Bag starters
        if config['general']['starter'] in ['treecko', 'torchic', 'mudkip']:
            while GetGameState() != GameState.CHOOSE_STARTER and config['general']['bot_mode'] != 'manual':
                PressButton(['A'])

            if config['cheats']['starters_rng']:
                WriteSymbol('gRngValue', struct.pack('<I', random.randint(0, 2**32 - 1)))
                WaitFrames(1)

            match config['general']['starter']:
                case 'treecko':
                    while GetTask(t_bag_cursor).get('data', ' ')[0] != 0 and config['general']['bot_mode'] != 'manual':
                        PressButton(['Left'])
                case 'mudkip':
                    while GetTask(t_bag_cursor).get('data', ' ')[0] != 2 and config['general']['bot_mode'] != 'manual':
                        PressButton(['Right'])

            while not GetTask(t_confirm).get('isActive', False) and config['general']['bot_mode'] != 'manual':
                PressButton(['A'], 1)

            if not config['cheats']['starters_rng']:
                rng = int(struct.unpack('<I', ReadSymbol('gRngValue', size=4))[0])
                while rng in rng_history['rng'] and config['general']['bot_mode'] != 'manual':
                    WaitFrames(1)
                    rng = int(struct.unpack('<I', ReadSymbol('gRngValue', size=4))[0])

            if config['cheats']['starters']:
                while not GetParty() and config['general']['bot_mode'] != 'manual':
                    PressButton(['A'])
            else:
                while GetGameState() != GameState.BATTLE and config['general']['bot_mode'] != 'manual':
                    PressButton(['A'])

                while GetTask(t_ball_throw) == {} and config['general']['bot_mode'] != 'manual':
                    PressButton(['B'])

                WaitFrames(60)

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

        # Johto starters (Emerald only)
        elif GetROM().game_title == 'POKEMON EMER' and config['general']['starter'] in ['chikorita', 'totodile', 'cyndaquil']:
            config['cheats']['starters'] = True  # TODO temporary until menu navigation is ready
            console.print('[red]Note: Johto starters enables the fast `starters` check option in `config/cheats.yml`, the shininess of the starter is checked via memhacks while start menu navigation is WIP (in future, shininess will be checked via the party summary menu).')

            if len(GetParty()) > 1:
                console.print('[red]Pokémon detected in party slot 2, deposit all party members (except lead) before using this bot mode!')
                exit(1)
            else:
                while GetGameState() != GameState.OVERWORLD and config['general']['bot_mode'] != 'manual':
                    PressButton(['A'])

                if config['cheats']['starters_rng']:
                    WriteSymbol('gRngValue', struct.pack('<I', random.randint(0, 2 ** 32 - 1)))
                    WaitFrames(1)
                else:
                    while GetTask('TASK_DRAWFIELDMESSAGE') == {} and config['general']['bot_mode'] != 'manual':
                        PressButton(['A'])
                    while GetTask('TASK_HANDLEYESNOINPUT') == {} and config['general']['bot_mode'] != 'manual':
                        PressButton(['B'])

                    rng = int(struct.unpack('<I', ReadSymbol('gRngValue', size=4))[0])
                    while rng in rng_history['rng'] and config['general']['bot_mode'] != 'manual':
                        WaitFrames(1)
                        rng = int(struct.unpack('<I', ReadSymbol('gRngValue', size=4))[0])

                while GetTask('TASK_FANFARE') == {} and config['general']['bot_mode'] != 'manual':
                    PressButton(['A'])

                if config['cheats']['starters']:
                    while len(GetParty()) == 1 and config['general']['bot_mode'] != 'manual':
                        PressButton(['B'])
                #else:
                    # TODO check Pokémon summary screen once menu navigation merged
                    # while GetTask('TASK_HANDLEYESNOINPUT') != {} or GetTask('TASK_DRAWFIELDMESSAGE') != {}:
                    #    PressButton(['B'])

                pokemon = GetParty()[1]
                seen += 1
                if pokemon['pid'] in session_pids:
                    dupes += 1
                    console.print(
                        '[red]Duplicate detected! {} [{}] has already been seen during this bot session, and will not be logged ({:.2f}% dupes this session).'.format(
                            pokemon['name'],
                            hex(pokemon['pid'])[2:],
                            (dupes / seen) * 100))
                    console.print(
                        '[red]If you notice too many dupes or resets taking too long, consider enabling `starters_rng` in `config/cheats.yml`. Ctrl + click [link=https://github.com/40Cakes/pokebot-gen3#cheatsyml---cheats-config]here[/link] for more information on this cheat.\n')
                else:
                    EncounterPokemon(pokemon)
                    session_pids.append(pokemon['pid'])

        else:
            console.print('[red]Invalid `starter` config for {} ({})!'.format(
                GetROM().game_name,
                config['general']['starter']))
            exit(1)

        if not config['cheats']['starters_rng']:
            rng_history['rng'].append(rng)
            SaveRNGStateHistory(config['general']['starter'], rng_history)

        if config['general']['bot_mode'] != 'manual':
            GetEmulator().Reset()
    except SystemExit:
        raise
    except:
        console.print_exception(show_locals=True)

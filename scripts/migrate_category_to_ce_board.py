import asyncio
import os
from dotenv import load_dotenv
import speedruncompy
from speedruncompy import (
    Player,
    RunSettings,
    RuntimeTuple,
    GetSession,
    GetGameLeaderboard2,
    PutRunSettings,
    VarValue,
)
from speedruncompy.datatypes.defs import Run

load_dotenv()
speedruncompy.api._default.PHPSESSID = os.environ["SRC_PHPSESSID"]

# Category names
defeat_ganon_ram_prep = 'defeat_ganon_ram_prep'
hundo_item_completion = 'hundo_item_completion'
any_percent_no_oob = 'any_percent_no_oob'
cane_of_byrna = 'cane_of_byrna'

# Source category ids
alttp_main_board_id = '9d3rr0dl'
mb_misc_category_id = 'jdz8nmvd'
mb_misc_sub_categories_variable_id = 'rn11g4pn'
mb_misc_sub_categories = {
    defeat_ganon_ram_prep: 'mlnvgk61',
    hundo_item_completion: 'rqvd68wq',
    any_percent_no_oob: 'z1958jyq',
    cane_of_byrna: '81we5vm1',
}

# Main board Blue ball variables
mb_bb_variable_id = 'rn1wzdlj',
mb_bb_id_to_count_mapping = {
    # 'gq7298p1': '-',
    '810604o1': '0',
    '9qj2w371': '1',
    'jq6vydv1': '2',
    '5lm2858q': '3',
    '81w7eymq': '4',
    'zqojm451': '5',
    '013xwgr1': '6',
    'rqvx68rl': '7',
    '5len3jml': '8',
    '0q54xr7l': '9',
    '4lxg0n3q': '10',
    '8149kzeq': '11',
    'z19x5ny1': '12',
    'p129o7dl': '13',
    '81pe49vl': '14',
    'xqko9vd1': '15',
}

# Target category ids
alttp_ce_board_id = 'm1zjyk06'

# TODO: Fill this:
# - Create new category and fill id in here
# - Create BB variable for category if applicable. Find new variable ID from variables.json.
# - Add values. Filter GetGameData on variableId to get ids for all added values.
new_ce_categories = {
    defeat_ganon_ram_prep: {
        'id': '',
        'bb_variable_id': None,
    },
    hundo_item_completion: {
        'id': '',
        'bb_variable_id': '',
        'bb_count_to_id_mapping': {
            '0': '',
            '1': '',
            '2': '',
            '3': '',
            '4': '',
            '5': '',
            '6': '',
            '7': '',
            '8': '',
            '9': '',
            '10': '',
            '11': '',
            '12': '',
            '13': '',
            '14': '',
            '15': '',
        },
    },
    any_percent_no_oob: {
        'id': '',
        'bb_variable_id': None,
    },
    cane_of_byrna: {
        'id': '',
        'bb_variable_id': '',
        'bb_count_to_id_mapping': {
            '0': '',
            '1': '',
            '2': '',
            '3': '',
            '4': '',
            '5': '',
            '6': '',
            '7': '',
            '8': '',
            '9': '',
            '10': '',
            '11': '',
            '12': '',
            '13': '',
            '14': '',
            '15': '',
        },
    },
}

async def fetch_runs_for_misc_subcategory(subcategory_name: str) -> tuple[list[Run], dict[str, Player]]:
    """Fetch all submissions (including obsolete ones) for a given Misc subcategory."""
    lb = await GetGameLeaderboard2(
        gameId=alttp_main_board_id,
        categoryId=mb_misc_category_id,
        obsolete=1,
        values=[{
            'variableId': mb_misc_sub_categories_variable_id,
            'valueIds': [mb_misc_sub_categories[subcategory_name]],
        }]
    ).perform_all()
    return lb.runList, lb._playerDict

# New run settings generation helpers
def convert_run_duration_to_runtime_tuple(seconds: float) -> RuntimeTuple:
    total_secs = int(seconds)
    hours, remainder = divmod(total_secs, 3600)
    minutes, seconds = divmod(remainder, 60)
    return RuntimeTuple(hour=hours, minute=minutes, second=seconds, millisecond=0)

def generate_run_values(ce_category: dict, run_id: str, run_value_ids: list[str]) -> list[VarValue]:
    bb_variable_id = ce_category['bb_variable_id']

    # Fill in BB count variableId and value if applicable
    values = []
    if bb_variable_id is not None:
        try:
            bb_count = next(mb_bb_id_to_count_mapping[id] for id in run_value_ids if id in mb_bb_id_to_count_mapping)
        except StopIteration:
            raise ValueError(f"No valid bb count variable found in valueIds for run '{run_id}'")
        values = [VarValue(variableId=bb_variable_id, valueId=ce_category['bb_count_to_id_mapping'][bb_count])]

    return values

def build_run_settings(run: Run, player_names_for_run: list[str], ce_category: dict) -> RunSettings:
    """
    Map a Run from GetGameLeaderboard2 onto RunSettings object.

    Data preserved:
    - playerNames -> runner
    - time -> RTA time
    - platformId -> platform
    - emulator -> emulator flag
    - video -> video url
    - comment -> existing run comment
    - date -> original submission date
    - values -> BB count (if present)
    - regionId -> region -- Extra param not present in RunSettings, but will be passed on during serialization anyway
    Data lost:
    - Original verification date
    - Original verifier
    """
    # Make sure required fields are present
    if run.time is None:
        raise ValueError(f"`time` field missing in run '{run.id}'")
    if run.platformId is None:
        raise ValueError(f"`platformId` field missing in run '{run.id}'")
    if run.regionId is None:
        raise ValueError(f"`regionId` field missing in run '{run.id}'")
    if run.video is None:
        raise ValueError(f"`video` field missing in run '{run.id}'")

    return RunSettings(
        gameId=alttp_ce_board_id,
        categoryId=ce_category['id'],
        playerNames=player_names_for_run,
        time=convert_run_duration_to_runtime_tuple(run.time),
        platformId=run.platformId,
        emulator=run.emulator,
        regionId=run.regionId,
        video=run.video,
        comment=run.comment,
        date=run.date,
        values=generate_run_values(ce_category, run.id, run.valueIds),
        videoState=run.videoState,
    )

async def copy_category_to_ce_board(category_name: str, session_token: str, dry_run: bool = True):
    """Fetch all runs for the given category and copy them to a new category on the CE board."""
    new_ce_category = new_ce_categories[category_name]
    if new_ce_category['id'] == '':
        print(f"[Error] Details for provided category '{category_name}' are incomplete")
        return

    print(f"Fetching existing submissions for category '{category_name}'")
    runs, players = await fetch_runs_for_misc_subcategory(category_name)
    print(f"Found {len(runs)} submissions (including obsolete).")
    print()

    for run in runs:
        player_names_for_run = [players[id].name for id in run.playerIds]

        try:
            settings = build_run_settings(run, player_names_for_run, new_ce_category)
        except (ValueError) as e:
            print(f"[Error] Error generating settings for run '{run.id}': {e}")
            continue

        run_duration = convert_run_duration_to_runtime_tuple(run.time)
        print(f"Processing run with duration {run_duration} by runner '{player_names_for_run[0]}'")

        if not dry_run:
            try:
                result = await PutRunSettings(
                    csrfToken=session_token,
                    settings=settings,
                    autoverify=True,
                ).perform()
                print(f"- Successfully created new run: {result}")
            except Exception as exception:
                print(f"- [Error] Run creation failed: {exception}")
        else:
            print(f"- Dry run success. Would call PutRunSettings with: {settings}")

async def main():
    session = (await GetSession().perform()).session
    if not session.signedIn:
        raise RuntimeError("[Error] Not signed in. Set SRC_PHPSESSID in '.env'. See '.env.sample' for instructions.")
    print(f"Signed in as: {session.user.name}")

    await copy_category_to_ce_board(defeat_ganon_ram_prep, session.csrfToken, dry_run=True)

if __name__ == "__main__":
    asyncio.run(main())

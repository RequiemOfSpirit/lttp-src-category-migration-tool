import asyncio
import os
from dotenv import load_dotenv
import speedruncompy
from speedruncompy import GetSession

from config import (
    DEFEAT_GANON_RAM_PREP,
    ALTTP_MAIN_BOARD_ID,
    MB_MISC_CATEGORY_ID,
    MB_MISC_SUB_CATEGORIES_VARIABLE_ID,
    MB_MISC_SUB_CATEGORIES,
    ALTTP_CE_BOARD_ID,
    MB_BB_ID_TO_COUNT_MAPPING,
    NEW_CE_CATEGORIES,
)
from lttp_category_migration_tool import (
    fetch_submissions_for_category,
    generate_lttp_run_values,
    submit_run_to_board,
)

load_dotenv()
speedruncompy.api._default.PHPSESSID = os.environ["SRC_PHPSESSID"]

async def main():
    """Fetch all runs for the given category and copy them to a new category on the CE board."""
    session = (await GetSession().perform()).session
    if not session.signedIn:
        raise RuntimeError("[Error] Not signed in. Set SRC_PHPSESSID in '.env'. See '.env.sample' for instructions.")
    print(f"Signed in as: {session.user.name}\n")

    # MODIFY THESE WHEN RUNNING SCRIPT / TODO: Accept input from user
    category_name = DEFEAT_GANON_RAM_PREP
    dry_run = True

    new_ce_category = NEW_CE_CATEGORIES[category_name]
    if new_ce_category['id'] == '':
        print(f"[Error] Details for provided category '{category_name}' are incomplete")
        return

    print(f"Fetching existing submissions for category '{category_name}'")
    runs, players = await fetch_submissions_for_category(
        game_id=ALTTP_MAIN_BOARD_ID,
        category_id=MB_MISC_CATEGORY_ID,
        value_filters=[{
            'variableId': MB_MISC_SUB_CATEGORIES_VARIABLE_ID,
            'valueIds': [MB_MISC_SUB_CATEGORIES[category_name]],
        }],
    )
    print(f"Found {len(runs)} submissions (including obsolete).\n")

    for run in runs:
        player_names_for_run = [players[id].name for id in run.playerIds]

        run_values = []
        bb_variable_id = new_ce_category['bb_variable_id']
        if bb_variable_id is not None:
            try:
                bb_count = next(MB_BB_ID_TO_COUNT_MAPPING[id] for id in run.valueIds if id in MB_BB_ID_TO_COUNT_MAPPING)
            except StopIteration:
                raise ValueError(f"No valid bb count variable found in valueIds for run '{run.id}'")

            run_values = generate_lttp_run_values(
                bb_variable_id=bb_variable_id,
                bb_count=bb_count,
                bb_count_to_id_mapping=new_ce_category.get('bb_count_to_id_mapping', {}),
            )

        await submit_run_to_board(
            board_id=ALTTP_CE_BOARD_ID,
            category_id=new_ce_category['id'],
            runner_names=player_names_for_run,
            run=run,
            run_values=run_values,
            session_token=session.csrfToken,
            dry_run=dry_run,
        )

if __name__ == "__main__":
    asyncio.run(main())

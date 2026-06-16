import asyncio
import os
from dotenv import load_dotenv
import speedruncompy
from speedruncompy import GetSession, VarValue

from config import (
    ALTTP_MAIN_BOARD_ID,
    MB_MISC_CATEGORY_ID,
    MB_BB_VARIABLE_ID,
    MB_MISC_SUB_CATEGORIES,
    MB_MISC_SUB_CATEGORIES_VARIABLE_ID,
    MB_NMG_CATEGORY_ID,
    MB_NMG_SUB_CATEGORIES_VARIABLE_ID,
    MIRROR_SHIELD,
    NEW_MB_MIRROR_SHIELD_SUB_CATEGORY_ID,
)
from lttp_category_migration_tool import (build_run_settings, fetch_submissions_for_category, submit_run_to_board)

load_dotenv()
speedruncompy.api._default.PHPSESSID = os.environ["SRC_PHPSESSID"]

# Script config
DRY_RUN = True

async def main():
    """Fetch all runs for Mirror Shield in Misc and move them under the NMG tab."""
    session = (await GetSession().perform()).session
    if not session.signedIn:
        raise RuntimeError("[Error] Not signed in. Set SRC_PHPSESSID in '.env'. See '.env.sample' for instructions.")
    print(f"Signed in as: {session.user.name}\n")

    print(f"Fetching existing submissions for category '{MIRROR_SHIELD} (Misc)'")
    runs, players = await fetch_submissions_for_category(
        game_id=ALTTP_MAIN_BOARD_ID,
        category_id=MB_MISC_CATEGORY_ID,
        value_filters=[{
            'variableId': MB_MISC_SUB_CATEGORIES_VARIABLE_ID,
            'valueIds': [MB_MISC_SUB_CATEGORIES[MIRROR_SHIELD]],
        }],
    )
    print(f"Found {len(runs)} submissions (including obsolete).\n")

    for run in runs:
        # Get runner name
        runner_names = [players[id].name for id in run.playerIds]

        # Generate VarValue list for run
        bb_count_id_singleton_list = [
            value_id for value_id in run.valueIds if value_id != MB_MISC_SUB_CATEGORIES[MIRROR_SHIELD]
        ]
        if (len(bb_count_id_singleton_list) != 1):
            raise ValueError(f"Expected 1 value but found {len(bb_count_id_singleton_list)} values for run '{run.id}'")

        bb_count_id = bb_count_id_singleton_list[0]
        run_values = [
            VarValue(variableId=MB_BB_VARIABLE_ID, valueId=bb_count_id),
            VarValue(variableId=MB_NMG_SUB_CATEGORIES_VARIABLE_ID, valueId=NEW_MB_MIRROR_SHIELD_SUB_CATEGORY_ID),
        ]

        # Submit run
        run_settings = build_run_settings(
            board_id=ALTTP_MAIN_BOARD_ID,
            category_id=MB_NMG_CATEGORY_ID,
            runner_names=runner_names,
            run=run,
            run_values=run_values,
            is_edit=True,
        )
        await submit_run_to_board(
            session_token=session.csrfToken,
            run_settings=run_settings,
            should_auto_verify=True,
            dry_run=DRY_RUN,
        )

if __name__ == "__main__":
    asyncio.run(main())

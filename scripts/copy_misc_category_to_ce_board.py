import asyncio
import os
from dotenv import load_dotenv
import speedruncompy
from speedruncompy import GetSession

from config import (
    ALTTP_CE_BOARD_ID,
    ALTTP_MAIN_BOARD_ID,
    MB_BB_ID_TO_COUNT_MAPPING,
    MB_NMG_CATEGORY_ID,
    MB_NMG_SUB_CATEGORIES_VARIABLE_ID,
    MIRROR_SHIELD,
    NEW_CE_CATEGORIES,
    NEW_MB_MIRROR_SHIELD_SUB_CATEGORY_ID,
)
from lttp_category_migration_tool import (
    build_run_settings,
    fetch_submissions_for_category,
    fetch_username,
    format_run_verification_date,
    generate_lttp_run_values,
    submit_run_to_board,
)

load_dotenv()
speedruncompy.api._default.PHPSESSID = os.environ["SRC_PHPSESSID"]

# Script config: EDIT BEFORE RUNNING SCRIPT
SOURCE_CATEGORY_ID = MB_NMG_CATEGORY_ID
SOURCE_SUB_CATEGORY_VARIABLE_ID = MB_NMG_SUB_CATEGORIES_VARIABLE_ID
SOURCE_SUB_CATEGORY_ID = NEW_MB_MIRROR_SHIELD_SUB_CATEGORY_ID
TARGET_CATEGORY_NAME = MIRROR_SHIELD
DRY_RUN = True

async def main():
    """Fetch all runs for the given Misc category and copy them to a new category on the CE board."""
    session = (await GetSession().perform()).session
    if not session.signedIn:
        raise RuntimeError("[Error] Not signed in. Set SRC_PHPSESSID in '.env'. See '.env.sample' for instructions.")
    print(f"Signed in as: {session.user.name}\n")

    new_ce_category = NEW_CE_CATEGORIES[TARGET_CATEGORY_NAME]
    if new_ce_category['id'] == '':
        print(f"[Error] Details for provided category '{TARGET_CATEGORY_NAME}' are incomplete")
        return

    print(f"Fetching existing submissions for category '{TARGET_CATEGORY_NAME}'")
    runs, players = await fetch_submissions_for_category(
        game_id=ALTTP_MAIN_BOARD_ID,
        category_id=SOURCE_CATEGORY_ID,
        value_filters=[{
            'variableId': SOURCE_SUB_CATEGORY_VARIABLE_ID,
            'valueIds': [SOURCE_SUB_CATEGORY_ID],
        }],
    )
    print(f"Found {len(runs)} submissions (including obsolete).\n")

    verifiers = {}
    for run in runs:
        # Get runner name
        runner_names = [players[id].name for id in run.playerIds]

        # Get verification details to add to mod note
        mod_note_parts = ["Mod note: Run moved over from main board."]
        if run.dateVerified is None or run.verifiedById is None:
            print(f"[Warning] Run '{run.id}' by runner '{runner_names[0]}' missing verification details")

        if run.verifiedById is not None:
            if run.verifiedById in verifiers:
                verifier_name = verifiers[run.verifiedById]
            elif run.verifiedById in players:
                verifier_name = players[run.verifiedById].name
                verifiers[run.verifiedById] = verifier_name
            else:
                verifier_name = await fetch_username(run.verifiedById)
                verifiers[run.verifiedById] = verifier_name
            mod_note_parts.append(f"Originally verified by {verifier_name}.")

        if run.dateVerified is not None:
            mod_note_parts.append(f"Original verification date: {format_run_verification_date(run.dateVerified)}.")

        mod_note = ' '.join(mod_note_parts)

        # Generate VarValue list for run
        run_values = []
        bb_variable_id = new_ce_category['bb_variable_id']
        if bb_variable_id is not None:
            try:
                bb_count = next(MB_BB_ID_TO_COUNT_MAPPING[id] for id in run.valueIds if id in MB_BB_ID_TO_COUNT_MAPPING)
            except StopIteration:
                raise ValueError(f"No valid bb count variable found in valueIds for run '{run.id}'")

            if bb_count == '-':
                print(f"[Warning] BB count unknown for run '{run.id}' by runner '{runner_names[0]}'")
            else:
                run_values = generate_lttp_run_values(
                    bb_variable_id=bb_variable_id,
                    bb_count=bb_count,
                    bb_count_to_id_mapping=new_ce_category.get('bb_count_to_id_mapping', {}),
                )

        # Submit run
        run_settings = build_run_settings(
            board_id=ALTTP_CE_BOARD_ID,
            category_id=new_ce_category['id'],
            runner_names=runner_names,
            run=run,
            run_values=run_values,
            mod_note=mod_note,
        )
        await submit_run_to_board(
            session_token=session.csrfToken,
            run_settings=run_settings,
            should_auto_verify=True,
            dry_run=DRY_RUN,
        )

if __name__ == "__main__":
    asyncio.run(main())

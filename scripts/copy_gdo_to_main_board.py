import asyncio
import os
from dotenv import load_dotenv
import speedruncompy
from speedruncompy import GetSession, VarValue

from config import (
    ALTTP_CE_BOARD_ID,
    ALTTP_MAIN_BOARD_ID,
    CE_GDO_CATEGORY_DETAILS,
    MB_BB_COUNT_TO_ID_MAPPING,
    MB_BB_VARIABLE_ID,
    MB_NMG_CATEGORY_ID,
    MB_NMG_SUB_CATEGORIES_VARIABLE_ID,
    NEW_MB_GDO_SUB_CATEGORY_ID,
)
from lttp_category_migration_tool import (
    build_run_settings,
    fetch_submissions_for_category,
    fetch_username,
    format_run_verification_date,
    submit_run_to_board,
)

load_dotenv()
speedruncompy.api._default.PHPSESSID = os.environ["SRC_PHPSESSID"]

# Script config
DRY_RUN = True

async def main():
    """Fetch all runs for GDO on the CE board and copy them to a new sub-category under the NMG tab on the main board"""
    session = (await GetSession().perform()).session
    if not session.signedIn:
        raise RuntimeError("[Error] Not signed in. Set SRC_PHPSESSID in '.env'. See '.env.sample' for instructions.")
    print(f"Signed in as: {session.user.name}\n")

    if CE_GDO_CATEGORY_DETAILS['id'] == '' or CE_GDO_CATEGORY_DETAILS['bb_variable_id'] == '':
        print("[Error] CE GDO details in config are incomplete")
        return
    if NEW_MB_GDO_SUB_CATEGORY_ID == '':
        print("[Error] Target main board subcategory ID is empty")
        return

    print("Fetching existing submissions for category 'Glitchless Dungeon Order' on the CE board")
    runs, players = await fetch_submissions_for_category(
        game_id=ALTTP_CE_BOARD_ID,
        category_id=CE_GDO_CATEGORY_DETAILS['id'],
        value_filters=[],
    )
    print(f"Found {len(runs)} submissions (including obsolete).\n")

    verifiers: dict[str, str] = {}
    for run in runs:
        # Get runner name
        runner_names = [players[id].name for id in run.playerIds]

        # Get verification details to add to mod note
        mod_note_parts = ["Mod note: Run moved over from CE board."]
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
        run_values = [VarValue(variableId=MB_NMG_SUB_CATEGORIES_VARIABLE_ID, valueId=NEW_MB_GDO_SUB_CATEGORY_ID)]
        try:
            bb_count = next(
                CE_GDO_CATEGORY_DETAILS['bb_id_to_count_mapping'][id]
                for id in run.valueIds
                if id in CE_GDO_CATEGORY_DETAILS['bb_id_to_count_mapping']
            )
        except StopIteration:
            raise ValueError(f"No valid BB count variable found in valueIds for run '{run.id}'")

        run_values.append(VarValue(variableId=MB_BB_VARIABLE_ID, valueId=MB_BB_COUNT_TO_ID_MAPPING[bb_count]))

        # Submit run
        run_settings = build_run_settings(
            board_id=ALTTP_MAIN_BOARD_ID,
            category_id=MB_NMG_CATEGORY_ID,
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

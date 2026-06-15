import asyncio
import os
from dotenv import load_dotenv
import speedruncompy
from speedruncompy import GetSession, GetRun, Player, Run

from config import (ALTTP_CE_BOARD_ID, HUNDO_ITEM_COMPLETION, MB_BB_ID_TO_COUNT_MAPPING, NEW_CE_CATEGORIES)
from lttp_category_migration_tool import (
    build_run_settings,
    fetch_username,
    format_run_verification_date,
    submit_run_to_board,
)
from lttp_category_migration_tool.core import generate_lttp_run_values

load_dotenv()
speedruncompy.api._default.PHPSESSID = os.environ["SRC_PHPSESSID"]

# Script config
TEST_RUN_ID = 'ydegd1vm' # Use one of your own existing lttp runs here. Delete submission after manual verification.
TARGET_CATEGORY_NAME = HUNDO_ITEM_COMPLETION
DRY_RUN = True

async def get_run(run_id: str) -> tuple[Run, dict[str, Player]]:
    """Fetch a single run by id."""
    response = await GetRun(runId=run_id).perform()
    return response.run, {p.id: p for p in response.players}

async def main():
    session = (await GetSession().perform()).session
    if not session.signedIn:
        raise RuntimeError("[Error] Not signed in. Set SRC_PHPSESSID in '.env'. See '.env.sample' for instructions.")
    print(f"Signed in as: {session.user.name}\n")

    new_ce_category = NEW_CE_CATEGORIES[TARGET_CATEGORY_NAME]
    if new_ce_category['id'] == '':
        print(f"[Error] Details for provided category '{TARGET_CATEGORY_NAME}' are incomplete")
        return

    # Get test run details
    print(f"Fetching test run '{TEST_RUN_ID}'")
    run, players = await get_run(TEST_RUN_ID)
    runner_names = [players[id].name for id in run.playerIds]

    # Build mod note
    mod_note_parts = ["Mod note: Run moved over from main board."]
    if run.dateVerified is None or run.verifiedById is None:
        print(f"[Warning] Run '{run.id}' by runner '{runner_names[0]}' missing verification details")

    if run.verifiedById is not None:
        verifier_name = await fetch_username(run.verifiedById)
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
        should_auto_verify=False,
        dry_run=DRY_RUN,
    )

if __name__ == "__main__":
    asyncio.run(main())

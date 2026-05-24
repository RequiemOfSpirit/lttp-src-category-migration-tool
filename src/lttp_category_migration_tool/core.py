"""Helper functions for ALTTP category migrations"""

from speedruncompy import (
    Player,
    RunSettings,
    RuntimeTuple,
    GetGameLeaderboard2,
    PutRunSettings,
    VarValue,
)
from speedruncompy.datatypes.defs import Run, VarValues

async def fetch_submissions_for_category(
    game_id: str,
    category_id: str,
    value_filters: list[VarValues],
) -> tuple[list[Run], dict[str, Player]]:
    """Fetch all submissions (including obsolete ones) for a given category."""
    lb = await GetGameLeaderboard2(
        gameId=game_id,
        categoryId=category_id,
        obsolete=1,
        values=value_filters,
    ).perform_all()
    return lb.runList, lb._playerDict

# Run settings generation helpers
def generate_lttp_run_values(
    bb_variable_id: str,
    bb_count: str,
    bb_count_to_id_mapping: dict,
) -> list[VarValue]:
    """Generate BB count variable value for a run."""
    return [VarValue(variableId=bb_variable_id, valueId=bb_count_to_id_mapping[bb_count])]

def convert_run_duration_to_runtime_tuple(seconds: float) -> RuntimeTuple:
    """Convert a duration in seconds to a RuntimeTuple."""
    total_secs = int(seconds)
    hours, remainder = divmod(total_secs, 3600)
    minutes, seconds = divmod(remainder, 60)
    return RuntimeTuple(hour=hours, minute=minutes, second=seconds, millisecond=0)

def build_run_settings(
    board_id: str,
    category_id: str,
    runner_names: list[str],
    run: Run,
    run_values: list[VarValue],
) -> RunSettings:
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
    - regionId -> region (extra param not present in RunSettings, but will be passed on during serialization anyway)
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
        gameId=board_id,
        categoryId=category_id,
        playerNames=runner_names,
        time=convert_run_duration_to_runtime_tuple(run.time),
        platformId=run.platformId,
        emulator=run.emulator,
        regionId=run.regionId,
        video=run.video,
        comment=run.comment,
        date=run.date,
        values=run_values,
        videoState=run.videoState,
    )

async def submit_run_to_board(
    board_id: str,
    category_id: str,
    runner_names: list[str],
    run: Run,
    run_values: list[VarValue],
    session_token: str,
    dry_run: bool = True,
) -> bool:
    """Submit a single run to the board."""
    settings = build_run_settings(
        board_id=board_id,
        category_id=category_id,
        runner_names=runner_names,
        run=run,
        run_values=run_values,
    )
    print(f"Processing run with duration {settings.time} by runner '{runner_names[0]}'")

    if not dry_run:
        try:
            result = await PutRunSettings(
                csrfToken=session_token,
                settings=settings,
                autoverify=True,
            ).perform()
            print(f"- Successfully created new run: {result}")
            return True
        except Exception as exception:
            print(f"- [Error] Run creation failed: {exception}")
            return False
    else:
        print(f"- Dry run success. Would call PutRunSettings with: {settings}")
        return True

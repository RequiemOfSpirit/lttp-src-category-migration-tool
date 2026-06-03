# Category names
DEFEAT_GANON_RAM_PREP = 'defeat_ganon_ram_prep'
HUNDO_ITEM_COMPLETION = 'hundo_item_completion'
ANY_PERCENT_NO_OOB = 'any_percent_no_oob'
CANE_OF_BYRNA = 'cane_of_byrna'

# Source category ids
ALTTP_MAIN_BOARD_ID = '9d3rr0dl'
MB_MISC_CATEGORY_ID = 'jdz8nmvd'
MB_MISC_SUB_CATEGORIES_VARIABLE_ID = 'rn11g4pn'
MB_MISC_SUB_CATEGORIES = {
    DEFEAT_GANON_RAM_PREP: 'mlnvgk61',
    HUNDO_ITEM_COMPLETION: 'rqvd68wq',
    ANY_PERCENT_NO_OOB: 'z1958jyq',
    CANE_OF_BYRNA: '81we5vm1',
}

# Main board Blue ball variables
MB_BB_VARIABLE_ID = 'rn1wzdlj'
MB_BB_ID_TO_COUNT_MAPPING = {
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
ALTTP_CE_BOARD_ID = 'm1zjyk06'

# TODO: Fill this:
# - Create new category and fill id in here
# - Create BB variable for category if applicable. Find new variable ID from variables.json.
# - Add values. Filter GetGameData on variableId to get ids for all added values.
NEW_CE_CATEGORIES = {
    DEFEAT_GANON_RAM_PREP: {
        'id': 'n2ypzpe2',
        'bb_variable_id': None,
    },
    HUNDO_ITEM_COMPLETION: {
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
    ANY_PERCENT_NO_OOB: {
        'id': '9kv4ez0k',
        'bb_variable_id': None,
    },
    CANE_OF_BYRNA: {
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

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
# - Create new category and fill category id in here (id can be found in the URL on the category page)
# - Create BB variable for category if applicable. Open the new variable and hit save without making any changes.
#   Read the resulting PutVariableUpdate payload in the network tab to get the variable id and value ids.
NEW_CE_CATEGORIES = {
    DEFEAT_GANON_RAM_PREP: {
        'id': 'n2ypzpe2',
        'bb_variable_id': None,
    },
    HUNDO_ITEM_COMPLETION: {
        'id': 'wk6x59ek',
        'bb_variable_id': '0nwd90k8',
        'bb_count_to_id_mapping': {
            '0': 'ln896jdl',
            '1': 'lmopj041',
            '2': '1w49wx5q',
            '3': 'qox9w62q',
            '4': '139pen31',
            '5': 'qvv9w5wq',
            '6': 'le25g7zl',
            '7': 'q5vpejnl',
            '8': 'lx59w7r1',
            '9': '14ope0jq',
            '10': '192kgokq',
            '11': '12vpeykq',
            '12': '1py2wmk1',
            '13': 'qke5kyyq',
            '14': 'q75pemy1',
            '15': '1gn5rzml',
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

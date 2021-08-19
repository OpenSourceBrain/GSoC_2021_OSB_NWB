import roman

from datetime import datetime


def get_base_filename(experiment_info):
    """
    get_dat_filename: converts string in dd-mm-yy format with the month stored
    as roman numerals into yy_mm_dd format with all integer values
    """
    date_raw = experiment_info['Recording Date'].values[0]

    # convert roman numerals to string
    date_split = date_raw.split('-')
    date_split[1] = str(roman.fromRoman(date_split[1]))

    # convert to be yy-mm-dd format for .dat files
    date = datetime.strptime(' '.join(date_split), "%d %m %y").strftime("%y-%m-%d")

    return date

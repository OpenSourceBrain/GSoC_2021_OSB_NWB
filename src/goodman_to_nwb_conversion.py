import os
import pandas as pd
import roman
import x_to_nwb

from datetime import datetime


def convert_goodman_to_nwb(metadata_filename, cell_ids):
    '''
        convert_worm_data: converts metadata from spreadsheet and patchmaster data from .dat files to nwb format
    '''
    for cell in cell_ids:
        # import experiment info and get metadata
        metadata = Metadata(metadata_filename, cell)
        experiment_info = metadata.import_metadata(start_row=13)
        all_metadata = metadata.compile_metadata()

        # convert data to nwb file
        base_filename = get_base_filename(experiment_info)
        patchmaster_data = PatchmasterData(all_metadata, base_filename)
        patchmaster_data.convert_dat_to_nwb()

class PatchmasterData:
    def __init__(self, metadata, base_filename):
        self.metadata = metadata
        self.base_filename = base_filename

    def get_file_path(self):
        # check that file exists
        dat_filename = f"..//test_data//{self.base_filename}.dat"
        if not os.path.isfile(dat_filename):
            self.base_filename = self.base_filename.replace('-','_')
            dat_filename = f"..//test_data//{self.base_filename}.dat"

        if not os.path.isfile(dat_filename):
            raise ValueError(f"The file {dat_filename} does not exist")

        return dat_filename

    def convert_dat_to_nwb(self):
        # convert the dataset
        dat_filename = self.get_file_path()
        x_to_nwb.convert(dat_filename, overwrite=True, metadata=self.metadata)

class Metadata:
    def __init__(self, filename, cell_id):
        self.metadata_filename = filename
        self.subject_id = cell_id
        self.experiment_info = None

    def import_metadata(self, start_row):
        '''
        import_metadata: gets all the metadata from a specific recording with the input cell id
        '''
        #import excel file
        df = pd.read_excel(self.metadata_filename, skiprows = range(start_row), header=[0,1], sheet_name='Recordings-MetaData')

        #clean up the column names
        colname_top = df.columns.get_level_values(level=0).str.replace('Unnamed.*','',regex=True)
        colname_bottom = df.columns.get_level_values(level=1).str.replace('Unnamed.*','',regex=True)
        df.columns = [colname_top, colname_bottom]
        df.columns = df.columns.map(''.join)

        #select the row containing the relevant experiment info
        self.experiment_info = df.loc[df['Cell ID'] == self.subject_id]
        if self.experiment_info.empty:
            raise ValueError(f"The Cell ID {self.subject_id} is not in the metadata spreadsheet")

        return self.experiment_info

    def select_subject_data(self):
        '''
        import_subject_metadata: gets subject info like genotype, worm dimensions, id
        and exports as dict for input into the nwb file
        '''
        if self.experiment_info is None:
            return ValueError('Must import metadata first to select subject data')

        #get cell id
        cell_id = self.experiment_info['Cell'].values[0]

        #get genotype using strain ID
        strain = self.experiment_info['Strain'].values[0]
        df = pd.read_excel(self.metadata_filename, sheet_name='StrainsdB')
        genotype = df['Genotype'][df['Strain'] == strain].values[0]

        #get worm description
        vals = self.experiment_info.filter(like='µm').values[0]
        keys = ['length (µm)','width (µm)','area (µm)']
        dims = dict(zip(keys,vals))
        descript = {**{'cell type': cell_id}, **dims}
        nan_vals = ['no data','nd']
        for k in descript:
            if descript[k] in nan_vals:
                descript[k] = 'nan'

        subject_data = {'subject_id': cell_id,
                        'subject_species':'C. elegans',
                        'subject_description': str(descript),
                        'subject_genotype': genotype}

        return subject_data

    def select_preparation_data(self):
        if self.experiment_info is None:
            return ValueError('Must import metadata first to select preparation data')

        # get solution data
        sol_int = get_ingredients(self.metadata_filename, self.experiment_info, 'I-SolutionsdB', 'I-soln')
        sol_ext_ctl = get_ingredients(self.metadata_filename, self.experiment_info, 'E-SolutionsdB', 'E-soln-ctl')
        sol_ext_exp = get_ingredients(self.metadata_filename, self.experiment_info, 'E-SolutionsdB', 'E-soln-exp')

        # select environment data # TODO - check if these are the right definitions?
        temp_cell = self.experiment_info['Tc°C'].values[0]
        temp_environment = self.experiment_info['Te°C'].values[0]

        #compile preparation metadata
        preparation_metadata = {'Internal solution': sol_int,
                                'External solution - control': sol_ext_ctl,
                                'External solution - experimental': sol_ext_exp,
                                'Temperature - cell': temp_cell,
                                'Temperature - environment': temp_environment,
                                }

        return {'notes': str(preparation_metadata)}

    def select_electrode_data(self):
        # electrode info # TODO - check if these are the right definitions?
        pipette_resistance = str(self.experiment_info['RpMΩ'].values[0]) #resistance pipette?
        input_capacitance = str(self.experiment_info['CinpF'].values[0]) #whole_cell_capacitance_comp?? capacitance_compensation?
        seal_resistance = str(self.experiment_info['RsMΩ'].values[0])  # series resistance?
        filtering_cutoff = str(self.experiment_info['Fc*(kHz)'].values[0]) #filtering low pass cutoff? high pass?

        electrode_metadata = {'electrode_resistance': pipette_resistance,
                              'electrode_capacitance': input_capacitance,
                              'electrode_seal': seal_resistance,
                              'electrode_filtering': filtering_cutoff,
                              'electrode_description': 'recording pipette'
                              }

        return electrode_metadata

    def select_mechanical_data(self):
        mechanical_stim = str(self.experiment_info['Probe'].values[0])
        if mechanical_stim == 'nw':
            stim_description = 'No mechanical stimulation given this session.'
        else:
            stim_description = f"Mechanical stimulus ({mechanical_stim}) given this session."

        return stim_description

    def compile_metadata(self):
        subject_data = self.select_subject_data()
        preparation_data = self.select_preparation_data()
        electrode_data = self.select_electrode_data()
        mechanical_data = self.select_mechanical_data()
        # TODO - add more details to stimulus traces?

        # save all metadata fields
        misc_metadata = {'experiment_description': 'This dataset uses in vivo whole-cell patch-clamp recording to '
                                                   'deconstruct mechanoreceptor currents in ASH neurons of C. elegans',
                        'session_description': f'Intracellular whole-cell patch clamp recordings in ASH neurons of C.'
                                               f' elegans. {mechanical_data}',
                        'lab': 'Goodman Lab',
                        'institution': 'Stanford University',
                        'protocol': 'Recording starts with ct-ivq ‘on cell’, followed by ct-ivq ‘whole cell’.' \
                                    'The average traces from first IVq (Current-Voltage curve, Quick) are subtracted ' \
                                    'from averaged traces of the second IVq to remove capacitance artifacts.' \
                                    'The ct protocol (capacity transient) is a series of +10 mV and -10 mV voltage ' \
                                    'pulses that we use to measure capacitance and series resistance of each recording.',
                        'related_publications': ('Geffeney et al, Neuron 2011, doi: 10.1016/j.neuron.2011.06.038',
                                                 'Goodman et al, 1998 Neuron, doi: 10.1016/s0896-6273(00)81014-4')
                        }

        all_metadata = {**misc_metadata, **subject_data, **preparation_data, **electrode_data}

        return all_metadata

def get_ingredients(fname, rec_data, sheet_name, col_name):
    #import values for experiment
    df = pd.read_excel(fname, header=[0,1], sheet_name=sheet_name)
    solution = rec_data[col_name].values[0]

    #get ingredients list for each solution
    if solution == 'np':
        ingredients = 'no fast perfusion, gravity fed'
    elif solution not in df:
        ingredients = solution
    else:
        ingredients = dict(zip(df[solution]['Ingredients'], df[solution]['Molarity']))

    return ingredients

def get_base_filename(experiment_info):
    '''
    get_dat_filename: converts string in dd-mm-yy format with the month stored
    as roman numerals into yy_mm_dd format with all integer values
    '''
    date_raw = experiment_info['Recording Date'].values[0]

    # convert roman numerals to string
    date_split = date_raw.split('-')
    date_split[1] = str(roman.fromRoman(date_split[1]))

    #convert to be yy-mm-dd format for .dat files
    date = datetime.strptime(' '.join(date_split), "%d %m %y").strftime("%y-%m-%d")

    return date


if __name__ == "__main__":
    metadata_filename = '..//test_data//ASH-metadata_12_III_29.xls'
    #cell_list = ['ASH116', 'ASH213','ASH214', 'ASH215', 'ASH230', 'ASH231']
    cell_list = ['ASH116']

    convert_goodman_to_nwb(metadata_filename, cell_list)
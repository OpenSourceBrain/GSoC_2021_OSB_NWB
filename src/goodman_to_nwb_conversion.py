import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
import roman
import x_to_nwb

from datetime import datetime
from pynwb import NWBHDF5IO

def convert_goodman_to_nwb(metadata_filename, cell_ids, overwrite=False):
    """
        convert_worm_data: converts metadata from spreadsheet and patchmaster data from .dat files to nwb format
    """
    for cell in cell_ids:
        # import experiment info and get metadata
        print(f'Generating metadata for cell {cell}...')
        metadata = Metadata(metadata_filename, cell)
        experiment_info = metadata.import_metadata(start_row=13)
        all_metadata = metadata.compile_metadata()

        # convert data to nwb file
        print(f'Generating NWB file for cell {cell}...')
        base_filename = get_base_filename(experiment_info)
        patchmaster_data = PatchmasterData(all_metadata, base_filename)
        nwb_filenames = patchmaster_data.convert_dat_to_nwb(overwrite=overwrite)

        # create an image for each cell summary the data output
        print(f'Generating summary image for cell {cell}...')
        for file in nwb_filenames:
            summary_image_data = NWBFileSummaryImage(file)  # just use the first file to summarize data
            summary_image_data.create_summary_image()

        print(f'Finished converting all data for cell {cell}')

    print('Finished converting all data for all cells')

class PatchmasterData:
    def __init__(self, metadata, base_filename):
        self.metadata = metadata
        self.base_filename = base_filename

    def get_file_path(self):
        # check that file exists
        dat_filename = f"..//test_data//{self.base_filename}.dat"
        if not os.path.isfile(dat_filename):
            self.base_filename = self.base_filename.replace('-', '_')
            dat_filename = f"..//test_data//{self.base_filename}.dat"

        if not os.path.isfile(dat_filename):
            raise ValueError(f"The file {dat_filename} does not exist")

        return dat_filename

    def convert_dat_to_nwb(self, overwrite=False):
        # convert the dataset
        dat_filename = self.get_file_path()
        nwb_filename = x_to_nwb.convert(dat_filename, overwrite=overwrite, metadata=self.metadata)

        return nwb_filename

class NWBFileSummaryImage:
    def __init__(self, nwb_filename):
        self.nwb_filename = nwb_filename
        self.image_filename = nwb_filename.replace('.nwb','.png')

    def create_summary_image(self):
        # load nwbfile
        io = NWBHDF5IO(self.nwb_filename, 'r')
        nwbfile = io.read()

        # get mechanical stimulation information from metadata
        mech_stim_info = self.get_mechanical_stim_info(nwbfile)

        # plot and save summary image
        self.plot_summary_image(nwbfile, mech_stim_info)

    def plot_summary_image(self, nwbfile, mech_stim_info):
        """
        This function plots selected traces from an nwbfile in order to give a brief summary of the file contents.
        These plots are created by finding ANY series that match the key words. Multiple types of stimuli may be
        visualized in the same plot

        Mechanoreceptor currents: (acq 1 MEC-VC) + force (acq 2 MEC-VC)
        Mechanoreceptor potentials: (acq 1 MEC-CC) + force (acq 2 MEC-CC)
        Membrane currents: (acq 1 ct-ivq) + stim (stim 1 ct-ivq) ??
        Other plots that would be helpful? (Miv_VC, 'OnCellTemplate', 'WholeCell', 'OnCell', 'iv_VC')
        """

        sweep_table = nwbfile.sweep_table.to_dataframe()
        sweep_numbers = np.unique(sweep_table.sweep_number)
        sweep_table['label'] = sweep_table.apply(lambda row: eval(row.series[0].description)['series_label'], axis=1)

        plot_labels = self.get_plot_labels(nwbfile)

        plt.figure(figsize=(15, 8))

        # plot data for each series type
        for i, label in enumerate(plot_labels):
            ax_acq = plt.subplot(2, len(plot_labels), i+len(plot_labels)+1)
            ax_stim = plt.subplot(2, len(plot_labels), i+1)
            ax_stim.set_title(label, size='x-large')

            if mech_stim_info is not None and self.is_mech_stim(label):
                mech_stim_amp = mech_stim_info[label]
                ax_stim.text(0.55, 0.75, f"Mechanical stim:\n {mech_stim_amp} (µN)", transform=ax_stim.transAxes)

            for sweep in sweep_numbers:
                sweep_label = sweep_table.label[sweep_table.sweep_number == sweep].values[0]
                if label == sweep_label:
                    series = nwbfile.sweep_table.get_series(sweep)
                    acq, stim = self.get_data_channels(series, label)

                    ax_stim.plot(range(len(stim.data))/stim.rate, stim.data, "black", lw=.75, alpha=0.3)
                    ax_stim.set_ylabel(stim.unit, size='large')

                    ax_acq.plot(range(len(acq.data))/acq.rate, acq.data, "black", lw=.75, alpha=0.3)
                    ax_acq.set_ylabel(acq.unit, size='large')
                    ax_acq.set_xlabel(f'Time ({acq.starting_time_unit})', size='large')

        plt.suptitle(f"NWB data for {nwbfile.subject.subject_id} - "
                     f"{eval(nwbfile.subject.description)['cell type']} - "
                     f"{nwbfile.subject.genotype}")
        plt.tight_layout()
        plt.savefig(self.image_filename)
        plt.show()

    def get_plot_labels(self, nwbfile):
        # get series labels from each sweep
        labels = [eval(s.description)['series_label'] for s in nwbfile.sweep_table.series[:]]
        unique_labels = [x for x in np.unique(labels)]

        # check if recording contained mechanical stimulation sweeps and plot accordingly
        contains_mech_stim = any(self.is_mech_stim(item) for item in unique_labels)
        if contains_mech_stim:
            plot_labels = ('IVq', 'IVq-2s', 'MEC_VC', 'MEC_CC')
        else:
            plot_labels = ('IVq', 'IVq-2s', 'ct_pos', 'ct_neg')

        return plot_labels

    def is_mech_stim(self, label):
        return label in ('Mec-VC', 'Mec-CC', 'MEC_VC', 'MEC_CC', 'M-VC', 'M-CC', 'dMEC_VC')

    def get_data_channels(self, series, label):
        data_types = [s.neurodata_type for s in series]
        stim_channels = [i for i, type in enumerate(data_types) if 'Stimulus' in type]
        acq_channels = [i for i, type in enumerate(data_types) if 'Stimulus' not in type]

        if self.is_mech_stim(label):
            acq = series[acq_channels[0]]
            stim = series[acq_channels[1]]
        else:
            acq = series[acq_channels[0]]
            stim = series[stim_channels[0]]

        return (acq, stim)

    def get_mechanical_stim_info(self, nwbfile):
        if 'M-VC' in nwbfile.session_description:
            mech_stim_metadata = nwbfile.session_description.split('{')[1]
            mech_stim_info = eval('{' + mech_stim_metadata) # TODO - better way to get mechanical stim data

            # rename to match series labels
            mech_stim_info['MEC_VC'] = mech_stim_info.pop('M-VC')
            mech_stim_info['MEC_CC'] = mech_stim_info.pop('M-CC')
        else:
            mech_stim_info = None

        return mech_stim_info

class Metadata:
    def __init__(self, filename, cell_id):
        self.metadata_filename = filename
        self.subject_id = cell_id
        self.experiment_info = None

    def import_metadata(self, start_row):
        """
        import_metadata: gets all the metadata from a specific recording with the input cell id
        """
        # import excel file
        df = pd.read_excel(self.metadata_filename, skiprows=range(start_row), header=[0, 1],
                           sheet_name='Recordings-MetaData')

        # clean up the column names
        colname_top = df.columns.get_level_values(level=0).str.replace('Unnamed.*', '', regex=True)
        colname_bottom = df.columns.get_level_values(level=1).str.replace('Unnamed.*', '', regex=True)
        df.columns = [colname_top, colname_bottom]
        df.columns = df.columns.map(''.join)

        # select the row containing the relevant experiment info
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

        # get cell id
        cell_id = self.experiment_info['Cell'].values[0]

        # get genotype using strain ID
        strain = self.experiment_info['Strain'].values[0]
        df = pd.read_excel(self.metadata_filename, sheet_name='StrainsdB')
        genotype = df['Genotype'][df['Strain'] == strain].values[0]

        # get worm description
        vals = self.experiment_info.filter(like='µm').values[0]
        keys = ['length (µm)', 'width (µm)', 'area (µm)']
        dims = dict(zip(keys, vals))
        descript = {**{'cell type': cell_id}, **dims}
        nan_vals = ['no data', 'nd']
        for k in descript:
            if descript[k] in nan_vals:
                descript[k] = 'nan'

        subject_data = {'subject_id': self.subject_id,
                        'subject_species': 'C. elegans',
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

        # compile preparation metadata
        preparation_metadata = {'Internal solution': sol_int,
                                'External solution - control': sol_ext_ctl,
                                'External solution - experimental': sol_ext_exp,
                                'Temperature - cell': temp_cell,
                                'Temperature - environment': temp_environment,
                                }

        return {'notes': str(preparation_metadata)}

    def select_electrode_data(self):
        # electrode info # TODO - check if these are the right definitions?
        pipette_resistance = str(self.experiment_info['RpMΩ'].values[0])  # resistance pipette?
        input_capacitance = str(
            self.experiment_info['CinpF'].values[0])  # whole_cell_capacitance_comp?? capacitance_compensation?
        seal_resistance = str(self.experiment_info['RsMΩ'].values[0])  # series resistance?
        filtering_cutoff = str(self.experiment_info['Fc*(kHz)'].values[0])  # filtering low pass cutoff? high pass?

        electrode_metadata = {'electrode_resistance': pipette_resistance,
                              'electrode_capacitance': input_capacitance,
                              'electrode_seal': seal_resistance,
                              'electrode_filtering': filtering_cutoff,
                              'electrode_description': 'recording pipette'
                              }

        return electrode_metadata

    def select_mechanical_data(self):
        # get amplitude(?) values of the stimulation across the different stages
        stim_values = {}
        mechanical_stim_names = ('M-VC', 'M-CC', 'Miv')
        for key in mechanical_stim_names:
            value = str(self.experiment_info[key].values[0]).replace('mov', '').replace(' ', '')
            stim_values[key] = value

        # get probe information and whether stimulation was given
        probe_id = str(self.experiment_info['Probe'].values[0])
        if probe_id == 'nw':
            mechanical_stim_metadata = 'No mechanical stimulation delivered'
        else:
            mechanical_stim_metadata = f"Mechanical stimulation delivered with probe {probe_id}. " \
                                       f"Force amplitudes (µN) for each of the patch clamp series: {stim_values}"

        return mechanical_stim_metadata

    def compile_metadata(self):
        subject_data = self.select_subject_data()
        preparation_data = self.select_preparation_data()
        electrode_data = self.select_electrode_data()
        mechanical_data = self.select_mechanical_data()
        # TODO - add more details to stimulus traces?

        # save all metadata fields
        misc_metadata = {'experiment_description': 'This dataset uses in vivo whole-cell patch-clamp recording to '
                                                   'deconstruct mechanoreceptor currents in ASH neurons of C. elegans',
                         'session_description': f"Intracellular whole-cell patch clamp recordings in ASH neurons of C."
                                                f" elegans. {mechanical_data}",
                         'lab': 'Goodman Lab',
                         'institution': 'Stanford University',
                         'protocol': 'Recording starts with ct-ivq ‘on cell’, followed by ct-ivq ‘whole cell’.'
                                     'The average traces from first IVq (Current-Voltage curve, Quick) are subtracted '
                                     'from averaged traces of the second IVq to remove capacitance artifacts.'
                                     'The ct protocol (capacity transient) is a series of +10 mV and -10 mV voltage '
                                     'pulses that we use to measure capacitance and series resistance of each '
                                     'recording.',
                         'related_publications': ('Geffeney et al, Neuron 2011, doi: 10.1016/j.neuron.2011.06.038',
                                                  'Goodman et al, 1998 Neuron, doi: 10.1016/s0896-6273(00)81014-4')
                         }

        all_metadata = {**misc_metadata, **subject_data, **preparation_data, **electrode_data}

        return all_metadata


def get_ingredients(fname, rec_data, sheet_name, col_name):
    # import values for experiment
    df = pd.read_excel(fname, header=[0, 1], sheet_name=sheet_name)
    solution = rec_data[col_name].values[0]

    # get ingredients list for each solution
    if solution == 'np':
        ingredients = 'no fast perfusion, gravity fed'
    elif solution not in df:
        ingredients = solution
    else:
        ingredients = dict(zip(df[solution]['Ingredients'], df[solution]['Molarity']))

    return ingredients


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


if __name__ == "__main__":
    metadata_filename = '..//test_data//ASH-metadata_12_III_29.xls'
    cell_list = ['ASH097', 'ASH116', 'ASH230', 'ASH287']
    overwrite = False

    convert_goodman_to_nwb(metadata_filename, cell_list, overwrite)
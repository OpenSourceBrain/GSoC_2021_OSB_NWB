import matplotlib.pyplot as plt
import numpy as np
from pynwb import NWBHDF5IO


class NWBSummaryImagePlotter:
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

    def is_mech_stim(self, label):
        return label in ('Mec-VC', 'Mec-CC', 'MEC_VC', 'MEC_CC', 'M-VC', 'M-CC', 'dMEC_VC')

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

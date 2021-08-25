import utils

from metadata_mapper import MetadataMapper
from nwb_summary_image_plotter import NWBSummaryImagePlotter
from patchmaster_converter import PatchmasterConverter


def convert_goodman_to_nwb(metadata_filename, cell_ids, overwrite=False):
    """
        convert_goodman_to_nwb: converts metadata from spreadsheet and patchmaster data from .dat files to nwb format
    """
    for cell in cell_ids:
        # import experiment info and get metadata
        print(f'Generating metadata for cell {cell}...')
        metadata = MetadataMapper(metadata_filename, cell)
        experiment_info = metadata.import_metadata(start_row=13)
        all_metadata = metadata.compile_metadata()

        # convert data to nwb file
        print(f'Generating NWB file for cell {cell}...')
        base_filename = utils.get_base_filename(experiment_info)
        patchmaster_data = PatchmasterConverter(all_metadata, base_filename)
        nwb_filenames = patchmaster_data.convert_dat_to_nwb(overwrite=overwrite)

        # create an image for each cell summary the data output
        print(f'Generating summary image for cell {cell}...')
        for file in nwb_filenames:
            summary_image_data = NWBSummaryImagePlotter(file)  # just use the first file to summarize data
            summary_image_data.create_summary_image()

        print(f'Finished converting all data for cell {cell}')

    print('Finished converting all data for all cells')


if __name__ == "__main__":
    metadata_filename = '..//test_data//ASH-metadata_12_III_29.xls'
    cell_list = ['ASH097', 'ASH116', 'ASH230', 'ASH287']
    overwrite = True

    convert_goodman_to_nwb(metadata_filename, cell_list, overwrite)

import os
import x_to_nwb


class PatchmasterConverter:
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

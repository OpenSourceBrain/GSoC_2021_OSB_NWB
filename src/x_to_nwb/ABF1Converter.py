import pyabf
import numpy as np
import os
import glob
import json
from datetime import datetime
from dateutil.tz import tzlocal
from pynwb import NWBHDF5IO, NWBFile

from .conversion_utils import convertDataset, V_CLAMP_MODE, I_CLAMP_MODE, getStimulusSeriesClass, getAcquiredSeriesClass


class ABF1Converter:

    """
    Converts Neuron2BrainLab's ABF1 files from a single cell (collected without amplifier settings from the
    multi-clamp commander) to a collective NeurodataWithoutBorders v2 file.

    Modeled after ABFConverter created by the Allen Institute.

    Parameters
    ----------
    inputPath: path to ABF file or a folder of ABF files to be converted
    outputFilePath: path to the output NWB file
    acquisitionChannelName: Allows to output only a specific acquisition channel, defaults to all
    stimulusChannelName: Allows to output only a specific stimulus channel,
                         defaults to all. The name can also be an AD channel name for cases where
                         the stimulus is recorded as well.
    responseGain: user-input float indicating scalar gain for response channel
    stimulusGain: user-input float indicating scalar gain for stimulus channel
    compression:  Toggle compression for HDF5 datasets
    clampMode: 0 or 1 integer indicating clamp mode (0 is VC, 1 is CC). If not None, overwrites clamp mode provided in ABF file
    """

    def __init__(
        self,
        inputPath,
        outputFilePath,
        acquisitionChannelName=None,
        stimulusChannelName=None,
        responseGain=1,
        stimulusGain=1,
        responseOffset=0,
        clampMode=None,
        compression=True,
    ):

        self.inputPath = inputPath
        self.debug = False

        if os.path.isfile(self.inputPath):
            print(inputPath)

            abf = pyabf.ABF(self.inputPath)
            if abf.abfVersion["major"] != 1:
                raise ValueError(f"The ABF version for the file {abf} is not supported.")

            self.fileNames = [os.path.basename(self.inputPath)]
            self.abfFiles = [abf]

        elif os.path.isdir(self.inputPath):
            abfFiles = []
            for dirpath, dirnames, filenames in os.walk(self.inputPath):

                # Find all .abf files in the directory
                if len(dirnames) == 0 and len(glob.glob(dirpath + "/*.abf")) != 0:
                    abfFiles += glob.glob(dirpath + "/*.abf")

            if len(abfFiles) == 0:
                raise ValueError(f"{inputPath} contains no ABF Files.")

            # Arrange the ABF files in ascending order
            abfFiles.sort(key=lambda x: os.path.basename(x))

            # Collect file names for description
            self.fileNames = []
            for file in abfFiles:
                self.fileNames += [os.path.basename(file)]

            self.abfFiles = []
            for abfFile in abfFiles:
                # Load each ABF file using pyabf
                abf = pyabf.ABF(abfFile)

                # Check for ABF version
                if abf.abfVersion["major"] != 1:
                    raise ValueError(f"The ABF version for the file {abf} is not supported.")

                self.abfFiles += [abf]

        if clampMode:
            self.clampMode = clampMode  # sometimes the abf-based clamp mode is wrong
        else:
            self.clampMode = self.abfFiles[0]._headerV1.nExperimentType

        self.compression = compression
        self.outputPath = outputFilePath

        # Take metadata input, and return hard coded values for None

        self.responseGain = responseGain
        self.stimulusGain = stimulusGain
        self.responseOffset = responseOffset

        self.acquisitionChannelName = acquisitionChannelName
        self.stimulusChannelName = stimulusChannelName

    @staticmethod
    def outputMetadata(inFile):
        if not os.path.isfile(inFile):
            raise ValueError(f"The file {inFile} does not exist.")

        root, ext = os.path.splitext(inFile)

        abf = pyabf.ABF(inFile)
        pyabf.abfHeaderDisplay.abfInfoPage(abf).generateHTML(saveAs=root + ".html")

    def _getComments(self, abf):

        """
        Accesses the tag comments created in Clampfit
        """

        return abf.tagComments

    def _createNWBFile(self):

        """
        Creates the NWB file for the cell, as defined by PyNWB
        """

        self.start_time = datetime.combine(
            self.abfFiles[0].abfDateTime.date(), self.abfFiles[0].abfDateTime.time(), tzinfo=tzlocal()
        )
        self.inputCellName = os.path.basename(self.inputPath)

        creatorInfo = self.abfFiles[0]._headerV1.sCreatorInfo
        creatorVersion = self.abfFiles[0]._headerV1.creatorVersionString
        experiment_description = f"{creatorInfo} v{creatorVersion}"

        self.NWBFile = NWBFile(
            session_description="",
            session_start_time=self.start_time,
            experiment_description=experiment_description,
            identifier=self.inputCellName,
            experimenter=None,
            notes="",
        )
        return self.NWBFile

    def _createDevice(self):

        creatorInfo = self.abfFiles[0]._headerV1.sCreatorInfo
        creatorVersion = self.abfFiles[0]._headerV1.creatorVersionString

        self.device = self.NWBFile.create_device(name=f"{creatorInfo} {creatorVersion}")

    def _createElectrode(self):

        self.electrode = self.NWBFile.create_icephys_electrode(
            name="elec0", device=self.device, description="PLACEHOLDER"
        )

    def _unitConversion(self, unit):

        # Returns a 2-list of base unit and conversion factor

        if unit == "V":
            return 1.0, "V"
        elif unit == "mV":
            return 1e-3, "V"
        elif unit == "A":
            return 1.0, "A"
        elif unit == "pA":
            return 1e-12, "A"
        elif unit == "nA":
            return 1e-9, "A"
        else:
            # raise ValueError(f"{unit} is not a valid unit.")
            return 1.0, "V"  # hard coded for units stored as '?'

    def _addStimulus(self):

        """
        Adds a stimulus class as defined by PyNWB to the NWB File.

        Written for experiments conducted from a single channel.
        For multiple channels, refer to https://github.com/AllenInstitute/ipfx/blob/master/ipfx/x_to_nwb/ABFConverter.py
        """

        for idx, abfFile in enumerate(self.abfFiles):

            isStimulus = True

            if self.stimulusChannelName is None:
                channelList = abfFile.adcNames
                channelIndices = range(len(channelList))
            else:
                if self.stimulusChannelName in abfFile.dacNames:
                    channelList = abfFile.dacNames
                    channelIndices = [channelList.index(self.stimulusChannelName)]
                elif self.stimulusChannelName in abfFile.adcNames:
                    isStimulus = False
                    channelList = abfFile.adcNames
                    channelIndices = [channelList.index(self.stimulusChannelName)]
                else:
                    raise ValueError(f"Channel {self.stimulusChannelName} could not be found.")

            for i in range(abfFile.sweepCount):
                for channelIndex in channelIndices:

                    if self.debug:
                        print(
                            f"stimulus: abfFile={abfFile.abfFilePath}, sweep={i}, channelIndex={channelIndex}, channelName={channelList[channelIndex]}"
                        )

                    # Collect data from pyABF
                    abfFile.setSweep(i, channel=channelIndex)
                    seriesName = f"Index_{idx}_{i}_{channelIndex}"

                    if isStimulus:
                        data = abfFile.sweepC
                        scaledUnit = abfFile.sweepUnitsC
                    else:
                        data = abfFile.sweepY
                        scaledUnit = abfFile.sweepUnitsY

                    stimulusGain = float(self.stimulusGain)
                    data = data * stimulusGain

                    conversion, _ = self._unitConversion(scaledUnit)
                    electrode = self.electrode
                    resolution = np.nan
                    starting_time = 0.0
                    rate = float(abfFile.dataRate)

                    # Create a JSON file for the description field
                    description = json.dumps(
                        {
                            "file_name": os.path.basename(self.fileNames[idx]),
                            "file_version": abfFile.abfVersionString,
                            "sweep_number": i,
                            "protocol": abfFile.protocol,
                            "protocol_path": abfFile.protocolPath,
                            "comments": self._getComments(abfFile),
                        },
                        sort_keys=True,
                        indent=4,
                    )

                    stimulusClass = getStimulusSeriesClass(self.clampMode)

                    data = convertDataset(data, self.compression)

                    # Create a stimulus class
                    stimulus = stimulusClass(
                        name=seriesName,
                        data=data,
                        sweep_number=np.uint32(i),
                        electrode=electrode,
                        gain=stimulusGain,
                        resolution=resolution,
                        conversion=conversion,
                        starting_time=starting_time,
                        rate=rate,
                        description=description,
                    )

                    self.NWBFile.add_stimulus(stimulus)

    def _addAcquisition(self):

        """
        Adds an acquisition class as defined by PyNWB to the NWB File.

        Written for experiments conducted from a single channel.
        For multiple channels, refer to https://github.com/AllenInstitute/ipfx/blob/master/ipfx/x_to_nwb/ABFConverter.py
        """

        for idx, abfFile in enumerate(self.abfFiles):

            if self.acquisitionChannelName is None:
                channelList = abfFile.adcNames
                channelIndices = range(len(channelList))
            else:
                if self.acquisitionChannelName in abfFile.adcNames:
                    channelList = abfFile.adcNames
                    channelIndices = [channelList.index(self.acquisitionChannelName)]
                else:
                    raise ValueError(f"Channel {self.acquisitionChannelName} could not be found.")

            for i in range(abfFile.sweepCount):
                for channelIndex in channelIndices:

                    if self.debug:
                        print(
                            f"acquisition: abfFile={abfFile.abfFilePath}, sweep={i}, channelIndex={channelIndex}, channelName={channelList[channelIndex]}"
                        )

                    # Collect data from pyABF
                    abfFile.setSweep(i, channel=channelIndex)
                    seriesName = f"Index_{idx}_{i}_{channelIndex}"
                    responseGain = float(self.responseGain)
                    responseOffset = self.responseOffset

                    data = abfFile.sweepY * responseGain + responseOffset
                    conversion, _ = self._unitConversion(abfFile.sweepUnitsY)
                    electrode = self.electrode
                    resolution = np.nan
                    starting_time = 0.0
                    rate = float(abfFile.dataRate)

                    # Create a JSON file for the description field
                    description = json.dumps(
                        {
                            "file_name": os.path.basename(self.fileNames[idx]),
                            "file_version": abfFile.abfVersionString,
                            "sweep_number": i,
                            "protocol": abfFile.protocol,
                            "protocol_path": abfFile.protocolPath,
                            "comments": self._getComments(abfFile),
                        },
                        sort_keys=True,
                        indent=4,
                    )

                    # Create an acquisition class
                    # Note: voltage input produces current output; current input produces voltage output

                    data = convertDataset(data, self.compression)

                    series = getAcquiredSeriesClass(self.clampMode)

                    if self.clampMode == I_CLAMP_MODE:
                        acquisition = series(
                            name=seriesName,
                            data=data,
                            sweep_number=np.uint32(i),
                            electrode=electrode,
                            gain=responseGain,
                            resolution=resolution,
                            conversion=conversion,
                            starting_time=starting_time,
                            rate=rate,
                            description=description,
                            bias_current=np.nan,
                            bridge_balance=np.nan,
                            capacitance_compensation=np.nan,
                        )

                    elif self.clampMode == V_CLAMP_MODE:
                        acquisition = series(
                            name=seriesName,
                            data=data,
                            sweep_number=np.uint32(i),
                            electrode=electrode,
                            gain=responseGain,
                            resolution=resolution,
                            conversion=conversion,
                            starting_time=starting_time,
                            rate=rate,
                            description=description,
                            capacitance_fast=np.nan,
                            capacitance_slow=np.nan,
                            resistance_comp_bandwidth=np.nan,
                            resistance_comp_correction=np.nan,
                            resistance_comp_prediction=np.nan,
                            whole_cell_capacitance_comp=np.nan,
                            whole_cell_series_resistance_comp=np.nan,
                        )
                    else:
                        raise ValueError(f"Unsupported clamp mode {self.clampMode}")

                    self.NWBFile.add_acquisition(acquisition)

    def convert(self):

        """
        Iterates through the functions in the specified order.
        :return: True (for success)
        """

        self._createNWBFile()
        self._createDevice()
        self._createElectrode()
        self._addStimulus()
        self._addAcquisition()

        with NWBHDF5IO(self.outputPath, "w") as io:
            io.write(self.NWBFile, cache_spec=True)

        print(f"Successfully converted to {self.outputPath}.")

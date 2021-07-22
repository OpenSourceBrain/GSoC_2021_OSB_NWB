import glob
import os
import sys
import argparse
import logging

import pyabf
from .ABF2Converter import ABF2Converter
from .ABF1Converter import ABF1Converter
from .DatConverter import DatConverter


log = logging.getLogger(__name__)


def convert(
    inFileOrFolder,
    overwrite=False,
    fileType=None,
    outputMetadata=False,
    multipleGroupsPerFile=False,
    compression=True,
    searchSettingsFile=True,
    includeChannelList=list("*"),
    discardChannelList=None,
    acquisitionChannelName=None,
    stimulusChannelName=None,
    existingNWBData=None
):
    """
    Convert the given file to a NeuroDataWithoutBorders file using pynwb

    Supported fileformats:
        - ABF v1/v2 files created by Clampex
        - DAT files created by Patchmaster v2x90

    :param inFileOrFolder: path to a file or folder
    :param overwrite: overwrite output file, defaults to `False`
    :param fileType: file type to be converted, must be passed iff `inFileOrFolder` refers to a folder
    :param outputMetadata: output metadata of the file, helpful for debugging
    :param multipleGroupsPerFile: Write all Groups in the DAT file into one NWB
                                  file. By default we create one NWB per Group (DAT files only).
    :param searchSettingsFile: Search the JSON amplifier settings file and warn if it could not be found (ABFv2 only)
    :param compression: Toggle compression for HDF5 datasets
    :param includeChannelList: ADC channels to write into the NWB file (ABFv2 only)
    :param discardChannelList: ADC channels to not write into the NWB file (ABFv2 only)
    :param acquisitionChannelName: Output only that channel as acquisition channel (ABFv1 only)
    :param stimulusChannelName: Output only that channel as stimulation channel (ABFv1 only)
    :param addExistingNWBData: Add NWB metadata input that will be used in NWB file creation

    :return: path of the created NWB file
    """

    if not os.path.exists(inFileOrFolder):
        raise ValueError(f"The file {inFileOrFolder} does not exist.")

    if os.path.isfile(inFileOrFolder):
        root, ext = os.path.splitext(inFileOrFolder)

        # determine specific ABF major version
        if ext == ".abf":
            abf = pyabf.ABF(inFileOrFolder)
            major_version = abf.abfVersion["major"]
            ext = f".abfv{major_version}"

    if os.path.isdir(inFileOrFolder):
        if not fileType:
            raise ValueError("Missing fileType when passing a folder")

        inFileOrFolder = os.path.normpath(inFileOrFolder)
        inFileOrFolder = os.path.realpath(inFileOrFolder)

        ext = fileType
        root = os.path.join(inFileOrFolder, "..", os.path.basename(inFileOrFolder))

    outFile = root + ".nwb"
    matchingFiles = glob.glob(root + "*.nwb")

    if not outputMetadata and matchingFiles:
        if overwrite:
            for f in matchingFiles:
                os.remove(f)
        else:
            raise ValueError(f"The output file(s) {matchingFiles} already exist.")

    if ext == ".abfv1":
        if outputMetadata:
            ABF1Converter.outputMetadata(inFileOrFolder)
        else:
            conv = ABF1Converter(
                inFileOrFolder,
                outFile,
                compression=compression,
                stimulusChannelName=stimulusChannelName,
                acquisitionChannelName=acquisitionChannelName,
            )
            conv.convert()
    elif ext == ".abfv2":
        if outputMetadata:
            ABF2Converter.outputMetadata(inFileOrFolder)
        else:
            ABF2Converter(
                inFileOrFolder,
                outFile,
                compression=compression,
                searchSettingsFile=searchSettingsFile,
                includeChannelList=includeChannelList,
                discardChannelList=discardChannelList,
            )
    elif ext == ".dat":
        if outputMetadata:
            DatConverter.outputMetadata(inFileOrFolder)
        else:
            DatConverter(inFileOrFolder,
                         outFile,
                         multipleGroupsPerFile=multipleGroupsPerFile,
                         compression=compression,
                         existingNWBData=existingNWBData)

    else:
        raise ValueError(f"The extension {ext} is currently not supported.")

    return outFile


def convert_cli():

    parser = argparse.ArgumentParser()

    common_group = parser.add_argument_group(
        title="Common", description="Options which are applicable to both ABF and DAT files"
    )
    abf_group = parser.add_argument_group(title="ABF", description="Options which are applicable to ABF")
    abfv1_group = parser.add_argument_group(title="ABFv1", description="Options which are applicable to ABFv1")
    abfv2_group = parser.add_argument_group(title="ABFv2", description="Options which are applicable to ABFv2")
    dat_group = parser.add_argument_group(title="DAT", description="Options which are applicable to DAT")

    feature_parser = common_group.add_mutually_exclusive_group(required=False)
    feature_parser.add_argument(
        "--compression", dest="compression", action="store_true", help="Enable compression for HDF5 datasets (default)."
    )
    feature_parser.add_argument(
        "--no-compression", dest="compression", action="store_false", help="Disable compression for HDF5 datasets."
    )
    parser.set_defaults(compression=True)

    common_group.add_argument("--overwrite", action="store_true", default=False, help="Overwrite the output NWB file")
    common_group.add_argument(
        "--outputMetadata",
        action="store_true",
        default=False,
        help="Helper for debugging which outputs HTML/TXT files with the metadata contents of the files.",
    )
    common_group.add_argument("--log", type=str, help="Log level for debugging, defaults to the root logger's value.")
    common_group.add_argument("filesOrFolders", nargs="+", help="List of files/folders to convert.")
    abf_group.add_argument(
        "--fileType",
        type=str,
        default=None,
        choices=[".abfv1", ".abfv2"],
        help=("Type of the files to convert (only required if passing folders)."),
    )

    abfv1_group.add_argument(
        "--acquisitionChannelName", default=None, help="Output only the given channel as acquisition."
    )
    abfv1_group.add_argument("--stimulusChannelName", default=None, help="Output only the given channel as stimulus.")

    abfv2_group.add_argument(
        "--protocolDir", type=str, help=("Disc location where custom waveforms in ATF format are stored.")
    )
    abfv2_group.add_argument(
        "--no-searchSettingsFile",
        action="store_false",
        dest="searchSettingsFile",
        default=True,
        help="Don't search the JSON file for the amplifier settings.",
    )

    abfv2_group_channels = abfv2_group.add_mutually_exclusive_group(required=False)
    abfv2_group_channels.add_argument(
        "--includeChannel",
        type=str,
        dest="includeChannelList",
        action="append",
        help=f"Name of ADC channels to include in the NWB file.",
    )
    abfv2_group_channels.add_argument(
        "--discardChannel",
        type=str,
        dest="discardChannelList",
        action="append",
        help=f"Name of ADC channels to not include in the NWB file.",
    )

    dat_group.add_argument(
        "--multipleGroupsPerFile",
        action="store_true",
        default=False,
        help="Write all Groups from a DAT file into a single NWB file. By default we create one NWB file per Group.",
    )

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    if args.log:
        numeric_level = getattr(logging, args.log.upper(), None)

        if not isinstance(numeric_level, int):
            raise ValueError(f"Invalid log level: {args.log}")

        logger = logging.getLogger()
        logger.setLevel(numeric_level)

    if args.protocolDir:
        if not os.path.exists(args.protocolDir):
            raise ValueError("Protocol directory does not exist")

        ABF2Converter.protocolStorageDir = args.protocolDir

    for fileOrFolder in args.filesOrFolders:
        print(f"Converting {fileOrFolder}")
        convert(
            fileOrFolder,
            overwrite=args.overwrite,
            fileType=args.fileType,
            outputMetadata=args.outputMetadata,
            multipleGroupsPerFile=args.multipleGroupsPerFile,
            compression=args.compression,
            searchSettingsFile=args.searchSettingsFile,
            includeChannelList=args.includeChannelList,
            discardChannelList=args.discardChannelList,
            acquisitionChannelName=args.acquisitionChannelName,
            stimulusChannelName=args.stimulusChannelName,
        )


if __name__ == "__main__":
    convert_cli()

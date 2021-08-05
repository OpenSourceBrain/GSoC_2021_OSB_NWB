# Patchmaster DAT file to NWB testing

### testing conversion with HEKA-Patchmaster-Importer and x-to-nwb
example values given for 'index_000' acquisition/stimulus data field

| Mat file field | Mat file value | NWB file field | NWB file value | Notes |
| ----------- | -----------| ----------- | ----------- | ----------- |
| Experiment name | 'ASH300' | group_label | ASH300 |  |
| Rs | Inf | whole_cell_series_resistance_comp | nan | same value? Rs value also stored in the metadata sheet|
| Rs_fractioncomp | nan | resistance_comp_correction | nan | same value? converted to new name in DatConverter.py| 
| Cm | 0 | Cm_fast | 0 | same value? also have Cm_slow |
| Stimulus | 'ct_neg' | data.series_label | 'ct_neg' | |
| TimeUnit | 's' | data.starting_time_unit | 'seconds' | |
| ChUnit | A | data.unit | 'amperes' | |
| RecMode | 'whole-cell v-clamp' | neurodata_type | VoltageClampSeries | |
| SR | 10000 | rate | 10000| |
| TimeStamp | 19-Mar-2010 14:50:18 | timestamps_reference_time | 2010-03-19T...||
| dataRaw | 200xN traces | data | 200x1||
| RecTable | row for each rec w/multiple sweeps per rec | SweepTable | 1 row per sweep, all unique series id | think sweep table needs to be edited |
| stimUnit | V | stimulus.presentation['index_000'].data.units | 'volts' ||
| stimWave.DA_3 | 200x1 vals of -0.6 | stimulus.presentation['index_000'].data | 200x1 vals of -60.0 ||
| stimWave.DAC_0 | 76x1 vals of 0| | | not sure what this value means?|
| Temp | 20 | | | |
| ChName | 'Imon' | | | |
| Vhold | 0 | | |
| Rs_uncomp | inf | | | |
| | | Cm_slow | nan | |
| | | Cm_slow.unit | farads | |
| | | whole cell_capacitance_comp| nan | |
| | | resistance_comp_bandwith | nan | |
| | | resistance_comp_prediction | nan | |
| | | devices | EPC10-1-0 with LIH1600 | |
| | | description | PatchMaster v2x32, 18-Jan-2008 | |


### Notes/questions
* MEC_VC stimulus type has multiple channels/units saved, not sure yet how to address
  * when plotting, looks like stimulus?
* If E-soln-exp not on solutions list, just list the name? Any other info to add?
* Should the analysis module contain data processed in the way described?

### To do items
* add information from metadata spreadsheet columns from Tc to Cin
* add support for older .dat, .pul, .pgf files that are saved separately and in non DAT2 format
* add support for RampIVq-2s, MEC_VC, Miv_VC stimulus sets
* add support for "Increment mode - Alternate"
    
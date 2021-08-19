# Patchmaster DAT file to NWB testing notes

### Remaining questions
* Is the metadata mapping accurate? Or how should the other values be filled in? (See table below)
* What data is acquired on each of the channels when there are multiple?
  * ex. when acquisition channel 2 and stimulus channel 1 are almost but not quite the same
  * ex. sometimes one stimulus channel covers a very short time period
* Paper describes recording pre/during/post amiloride, are these separated in the experiment file?
* For files with multiple blocks with the same series label, should these be described differently or are they all the same?

### To do items
* compare plotting output with example figures or data to confirm units and stimulus reconstruction are correct
* confirm metadata descriptions are correct and update any other missing information
* add support for "Increment mode - Alternate"
* convert remaining files

### Current metadata mapping
Note: NWB fields with ["value"] indicates that it's a string that's included in the description/notes attribute, not a unique NWB field 

| Metadata field | Metadata unit | NWB file field | NWB file unit | Notes |
| ----------- | -----------| ----------- | ----------- | ----------- |
| Cell ID | --- | subject.subject_id | --- | |
| Cell | --- | subject.description["cell type"] | --- | |
| Strain | --- | subject.genotype | --- | |
| I-soln | --- | notes["Internal solution"] |  --- | I = internal?|
| E-soln-ctl | --- | notes["External solution - control"] |  --- | E = external?|
| E-soln-exp | --- | notes["External solution - experimental"] |  --- | E = external? |
| Tc | °C | notes["Temperature - cell"] | need to add | c = cell? |
| Te | °C | notes["Temperature - enivornment"] |  need to add | e = environment?|
| Fc* | kHz | electrode.filtering | need to add | low pass cutoff? high pass cutoff?|
| Fs | kHz | --- | --- | |
| Probe | --- | session_description - probe id | --- | probe id? |
| M-VC | --- | session_description - force amplitude | µN | force of the probe? M-VC = MEC-VC? |
| M-CC | --- | session_description - force amplitude | µN | force of the probe? M-CC = MEC-CC? |
| SM-VC | --- | --- | --- | |
| Miv | --- | --- |  µN | force of the probe? |
| Vramp | control | --- | --- ||
| Vramp | Gd+ | --- | --- ||
| Rp | MΩ | electrode.resistance | need to convert | Rp = pipette resistance? |
| Rs | MΩ | electrode.seal | need to add | Rs = seal resistance?|
| Cin | pF | --- | --- | whole_cell_capacitance_comp? capacitance compensation?|
| L (Unscaled)| cm | --- |||
| W (Unscaled) | cm | --- |||
| A (Unscaled) | cm | --- |||
| L (Scaled and Corrected) | µm | subject.description["length"] | µm | use scaled vs unscaled?|
| W (Scaled and Corrected) | µm | subject.width["length"] | µm | use scaled vs unscaled?|
| A (Scaled and Corrected) | µm | subject.area["length"]| µm | use scaled vs unscaled? A = area?|
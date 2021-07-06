# NWB Explorer testing with datasets

## test datasets I'm using
| Dataset ID | Example files | Title | Example filename | Notes |
| ----------- | ----------- | ----------- | ----------- | ----------- |
| [000004](https://gui.dandiarchive.org/#/dandiset/000004) | [example file](https://dandiarchive.s3.amazonaws.com/blobs/284/eb3/284eb346-0bc5-42a6-9b33-268e6b0b0bde) | single neurons recorded from the medial temporal lobes of 59 human subjects undergoing intracranial monitoring while they performed a recognition memory task. | sub-P10HMH_ses-20060901_ecephys+image.nwb | see below |
| [000005](https://gui.dandiarchive.org/#/dandiset/000005) | [example file](https://dandiarchive.s3.amazonaws.com/blobs/7ee/415/7ee41580-9b0b-44ca-8675-6959ddd8dc33)  | intracellular and extracellular electrophysiology recordings performed on mouse barrel cortex and ventral posterolateral nucleus (vpm) in whisker-based object locating task | sub-anm184389_ses-20130207_behavior+ecephys.nwb | see below |
| [000006](https://gui.dandiarchive.org/#/dandiset/000006) | [example file](https://dandiarchive.s3.amazonaws.com/blobs/063/b97/063b9771-b0c0-4b84-8b7d-fb52929b3087)| mouse anterior lateral motor cortex (ALM) in delay response task | sub-anm369962_ses-20170309.nwb  | see below |
| [000007](https://gui.dandiarchive.org/#/dandiset/000007) | [example file](https://dandiarchive.s3.amazonaws.com/blobs/d38/726/d38726f8-81ec-4226-afa1-8bf6138efd0a) | A Cortico-cerebellar loop for motor planning | sub-BAYLORCD12_ses-20180125T191601.nwb | see below|
| [000009](https://gui.dandiarchive.org/#/dandiset/000009) | [example file](https://dandiarchive.s3.amazonaws.com/blobs/55b/2aa/55b2aa6b-3bbc-4b29-9637-e899d0ddb4e9) | Maintenance of persistent activity in a frontal thalamocortical loop | sub-anm184389_ses-20130207_behavior+ecephys.nwb| see below |
| [000011](https://gui.dandiarchive.org/#/dandiset/000011) | [example file](https://dandiarchive.s3.amazonaws.com/blobs/a1d/c8d/a1dc8d9a-bbb6-4260-b56e-78844dbd957e) | Robust neuronal dynamics in premotor cortex during motor planning | sub-255200_ses-20140910_behavior+ecephys+ogen.nwb| see below |
| [000016](https://gui.dandiarchive.org/#/dandiset/000016) | [example file](https://dandiarchive.s3.amazonaws.com/blobs/295/a5d/295a5d42-e07f-482e-8022-78e2cc951678) | Excitatory and inhibitory subnetworks are equally selective during decision-making and emerge simultaneously during learning | sub-mouse1-fni16_ses-161220141515.nwb | see below |
| [000039](https://gui.dandiarchive.org/#/dandiset/000039) | [example file](https://dandiarchive.s3.amazonaws.com/blobs/52d/3c6/52d3c6f7-2460-4c03-9bfc-db992ab60365) | Contrast tuning in mouse visual cortex with calcium imaging | sub-661968859_ses-682746585_behavior+ophys.nwb | see below |
| [000048](https://gui.dandiarchive.org/#/dandiset/000048) | [example file](https://dandiarchive.s3.amazonaws.com/blobs/bd8/95b/bd895bc6-7a8f-46c0-8564-d94fd4a0b690) | Electrical and optical physiology in in vivo population scale two photon calcium imaging | sub-222549_ecephys+ophys.nwb | see below |
| [000049](https://gui.dandiarchive.org/#/dandiset/000049) | [example file](https://dandiarchive.s3.amazonaws.com/blobs/2c5/2a3/2c52a341-bb7f-433f-9ade-340f1bb0bf75) | TFxSF tuning in mouse visual cortex with calcium imaging | sub-661968859_ses-681698752_behavior+ophys.nwb | see below |
| [000067](https://gui.dandiarchive.org/#/dandiset/000067)| [example file](https://dandiarchive.s3.amazonaws.com/blobs/3a1/87c/3a187ccc-27a5-4cb1-8fb7-d3ef68edaf96)|Behavior-dependent short-term assembly dynamics in the medial prefrontal cortex | sub-EE_ses-EE-042_ecephys.nwb| see below |
| [NWB Showcase Example](https://github.com/stephprince/NWBShowcase/raw/master/NWB/) | [example file](https://github.com/stephprince/NWBShowcase/raw/master/NWB/datatypes.nwb)|NWBShowcase example file for 1D and 2D spatial series | datatypes.nwb | see below |


## Potential features/fixes

### fixes/small changes
* experimenter ID and related publications section not always filled with info
* time values like start time/file create date could be added to general tab
* units and electrodes values end up being displayed as objects in general tab
* time series plots when data has more than one dimension 
* change color of comments in python console bc hard to see right now

### bigger features
* Single unit rasters/mean waveforms
* Trials/intervals/epochs table - ability to select data from specific trials
* licks/single event time points, toggle display to visualize
* display imaging series
* visualization of electrodes and channels
* have tab with processing module or show all context index from the start?
* load up small chunk of the data to plot instead of the whole session if very big
* local file loading or instructions on how to do that
* ability to see size of file/progress of download
* kill/quit command if it's taking a while
* loading files from dandi links directly without getting redirected ones

## Notes from test datasets

### things to check for
* all the general fields populate/all the content from the file is output somewhere
* differences in plotting/display between explorer windows and nwbwidgets
* what content is in the content index that could be added to acquisition/details/general

### notes

__dandiset 000004__
* content index info
  * electrodes/units display as objects in details tab
  * file create date not displayed
* in nwb widgets
  * stimulus presentation shows up in widgets and series of pictures, errors out when try to visualize from content view
  * acquisition.events plots look different in the nwbwidgets vs the nwb plot output
  * acquisition.experiment_ids would want lines+markers to see data details since lots of similar values

__dandiset 000005__
* content index info
  * show all content breaks the explorer, it just goes to a blank screen?
* in nwb widgets
  * lick trace binary array does not show up in nwb window but does here
    * other binary arrays do get plotted normally so I'm not sure exactly what happened
  * related publications link works here, not showing up in general tab so not sure if it works there
  * single unit raster plot with nice spike times
  
__dandiset 000006__
* content index info
  * intervals.trials.columns, electrodes.columns shows start times as list of [object, object]
  * spike_times_index, electrodes_index show up as VectorIndex type in content index list.
    * part of units.columns, but other rows of units.columns do not show up
    * not sure exactly what the VectorIndex vs VectorData means
* in nwb widgets
  * related publications doi link does not work in general tab but does in the nwbwidgets
  * lick times shows up as straight line bc all values are 1, need lines+markers to visualize
  * units raster plots/tables, trial tables not visualized
  
__dandiset 000007__
* content index info
  * spike times, obs intervals, and electrodes index for units columns dataframe
* in nwb widgets
  * the location section of ogen_sites, electrode groups shows up as brackets/key value mappings in the nwb details tab
    * not sure if should be broken up into individual sections/columns or  displayed like this
    * nwb widgets just shows the python console output which looks similar so might just be normal

__dandiset 000009__
* similar to other files, tables of electrodes, units, intervals/trials don't display
* think the main data in this file is from the single units
  
__dandiset 000011__
* content index
  * example behavioral events time series where the data is all the same value but the time stamps indicate event times 
  * seems like BehavioralEvents might be a data type that could be used as a condition to change the display to lines+markers
* in nwb widgets
  * lots of good single units in this example and they display nicely
  * BehavioralEvents show up as single dots/markers for the relevant time stamps

__dandiset 000016__ 
* lots of single trial broken up examples of roi response series in this one if that ends up being useful
* in nwb widgets
  * the roi response series error out, but they work fine in the nwb explorer. Will have to check with HDFView to see if there is more than one value
  
__dandiset 000039__
* content index info
  * multiple sections in details tab display [object, object], not sure if this will be fixed by the changes I made for the units column or if these are all separate issues
    * examples - DfOverF, intervals.epochs.columns 
  * some modules(?) only in context index, ex. intervals, processing, imaging planes
  * device not displayed in general tab, not sure if it's very useful or helpful through
  * stimulus in the processing module here, not sure how common that is or if that's recommended
* in nwbwidgets
  * some of the fields error out in the nwbwidgets so hard to say exactly what's going on with that

__dandiset 000048__
* looks like it's just a placeholder dataset? for the ophys/ephys allen institute calibration data, not sure if it will be filled in the future
 
__dandiset 000049__
* content index info
  * processing roi responses does not display all of them, only the last one
    * processing.brain_observatory_pipeline.data_interfaces.Fluorescence.roi_response_series.DfOverF
  * units.columns is a compositeList where the values end up being displayed as objects
    * similar thing with intervals.epochs except some of the columns are the vector index type   
  * file_create_date is a composite list, could display as the time
* in nwb widgets
  * imaging plane is a whole section here, but it does not show up in content index tab
  * devices does not show up in the general tab even though its filled
  
__dandiset 000067__
* content index info
  * file_create_date - composite list, could make this more readable and put in the metadata
  * electrodes is a dynamic table type
    * vector data from electrodes.columns is displayed as a bunch of objects for each column
* looked in NWB widgets
  * time values like 'timestamps_reference_time' and 'session_start_time' are not displayed anywhere

__test dataset from showcase__
* spatial series only display first dimension even when 2D
* some details have underscore instead of second space
* all the units compared to nwb widgets look good  

    
# NWB Explorer testing with datasets

## test datasets I'm using
| Dataset ID | Example files | Title | Example filename | Notes |
| ----------- | ----------- | ----------- | ----------- | ----------- |
| [000004](https://gui.dandiarchive.org/#/dandiset/000004) | [example file](https://dandiarchive.s3.amazonaws.com/blobs/284/eb3/284eb346-0bc5-42a6-9b33-268e6b0b0bde) | single neurons recorded from the medial temporal lobes of 59 human subjects undergoing intracranial monitoring while they performed a recognition memory task. | sub-P10HMH_ses-20060901_ecephys+image.nwb |  |
| [000005](https://gui.dandiarchive.org/#/dandiset/000005) | [example file](https://dandiarchive.s3.amazonaws.com/blobs/7ee/415/7ee41580-9b0b-44ca-8675-6959ddd8dc33)  | intracellular and extracellular electrophysiology recordings performed on mouse barrel cortex and ventral posterolateral nucleus (vpm) in whisker-based object locating task | sub-anm184389_ses-20130207_behavior+ecephys.nwb
| [000006](https://gui.dandiarchive.org/#/dandiset/000006) | [example file](https://dandiarchive.s3.amazonaws.com/blobs/063/b97/063b9771-b0c0-4b84-8b7d-fb52929b3087)| mouse anterior lateral motor cortex (ALM) in delay response task | sub-anm369962_ses-20170309.nwb  |
| [000007](https://gui.dandiarchive.org/#/dandiset/000007) | [example file](https://dandiarchive.s3.amazonaws.com/blobs/d38/726/d38726f8-81ec-4226-afa1-8bf6138efd0a) | A Cortico-cerebellar loop for motor planning | sub-BAYLORCD12_ses-20180125T191601.nwb | |
| [000009](https://gui.dandiarchive.org/#/dandiset/000009) | [example file](https://dandiarchive.s3.amazonaws.com/blobs/55b/2aa/55b2aa6b-3bbc-4b29-9637-e899d0ddb4e9) | Maintenance of persistent activity in a frontal thalamocortical loop | sub-anm184389_ses-20130207_behavior+ecephys.nwb| |
| [000011](https://gui.dandiarchive.org/#/dandiset/000011) | [example file](https://dandiarchive.s3.amazonaws.com/blobs/a1d/c8d/a1dc8d9a-bbb6-4260-b56e-78844dbd957e) | Robust neuronal dynamics in premotor cortex during motor planning | sub-255200_ses-20140910_behavior+ecephys+ogen.nwb|  |
| [000016](https://gui.dandiarchive.org/#/dandiset/000016) | [example file](https://dandiarchive.s3.amazonaws.com/blobs/295/a5d/295a5d42-e07f-482e-8022-78e2cc951678) | Excitatory and inhibitory subnetworks are equally selective during decision-making and emerge simultaneously during learning | sub-mouse1-fni16_ses-161220141515.nwb | |
| [000039](https://gui.dandiarchive.org/#/dandiset/000039) | [example file](https://dandiarchive.s3.amazonaws.com/blobs/52d/3c6/52d3c6f7-2460-4c03-9bfc-db992ab60365) | Contrast tuning in mouse visual cortex with calcium imaging | sub-661968859_ses-682746585_behavior+ophys.nwb |  |
| [000048](https://gui.dandiarchive.org/#/dandiset/000048) | [example file](https://dandiarchive.s3.amazonaws.com/blobs/bd8/95b/bd895bc6-7a8f-46c0-8564-d94fd4a0b690) | Electrical and optical physiology in in vivo population scale two photon calcium imaging | sub-222549_ecephys+ophys.nwb | |
| [000049](https://gui.dandiarchive.org/#/dandiset/000049) | [example file](https://dandiarchive.s3.amazonaws.com/blobs/2c5/2a3/2c52a341-bb7f-433f-9ade-340f1bb0bf75) | TFxSF tuning in mouse visual cortex with calcium imaging | sub-661968859_ses-681698752_behavior+ophys.nwb | |
| [000067](https://gui.dandiarchive.org/#/dandiset/000067)| [example file](https://dandiarchive.s3.amazonaws.com/blobs/3a1/87c/3a187ccc-27a5-4cb1-8fb7-d3ef68edaf96)|Behavior-dependent short-term assembly dynamics in the medial prefrontal cortex | sub-EE_ses-EE-042_ecephys.nwb||

## Potential features/fixes

### fixes/small changes
* experimenter ID and related publications section not always filled with info
* time values like start time/file create date could be added to general tab
* units and electrodes values end up being displayed as objects in general tab
* time series plots when data has more than one dimension 

### bigger features
* Single unit rasters/mean waveforms
* Trials/intervals/epochs table - ability to select data from specific trials
* licks/single event time points, toggle display to visualize
* ability to see size of file/progress of download
* kill/quit command if it's taking a while
* display imaging series
* visualization of electrodes and channels
* load up small chunk of the data to plot instead of the whole session if very big

## Notes from test datasets

### things to check for
* all the general fields populate/all the content from the file is output somewhere
* differences in plotting/display between explorer windows and nwbwidgets
* what content is in the content index that could be added to acquisition

### notes
__dandiset 000004__
* content index info
  * electrodes/units display as objects in details tab
  * file create date not displayed
* in nwb widgets
  * stimulus presentation shows up in widgets and series of pictures, errors out when try to visualize from content view

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

  

    
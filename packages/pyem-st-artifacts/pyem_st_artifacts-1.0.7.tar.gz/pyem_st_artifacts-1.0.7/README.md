# Algorithm of emotional states
### Description
The algorithm processes the data by a sliding window of a given length with a given frequency. If artifacts are detected on one of the bipolar channels, the artifacts on the second bipolar channel are checked, and if there are no artifacts, they are switched to that channel; in case of artifacts on both channels, the spectral values and values of mental levels are filled with previous actual values, while the counter of the number of successive artifact windows increases.

### Artifacts
When the maximum number of consecutive artifact windows is reached, `math.is_artifacted_sequence()` returns true, which allows you to give the user information about the need to check the position of the device. This flag is usually raised 4 sec after receiving continuous artifacts. If there is no need to give notification of momentary artifacts, you can use this function as the primary for artifact notifications. Otherwise, use `math.is_both_sides_artifacted()` to check for momentary artifacts, returning true for artifacts on both bipolar channels for the current window.

### Emotional states
The estimate of emotional states (mental levels - relaxation and concentration) is available in two variants:
1. immediate assessment through alpha and beta wave intensity (and theta in the case of independent assessment). 
2. relative to the baseline calibration values of alpha and beta wave intensity

In both cases, the current intensity of the waves is defined as the average for the last N windows.

The algorithm starts processing the data after the first N seconds after connecting the device and when the minimum number of points for the spectrum calculation is accumulated.
When reading spectral and mental values an array of appropriate structures (`SpectralDataPercents` and `MindData`) of length is returned, which is determined by the number of new recorded points, signal frequency and analysis frequency. 

In this version the filters are built-in and clearly defined: 
BandStop_45_55, BandStop_55_65, BandStop_62, HighPass_10, LowPass_30
### Calibration

According to the results of calibration, the average base value of alpha and beta waves expression is determined in percent, which are further used to calculate the relative mental levels.

### Library mode
The library can operate in two modes - bipolar and multichannel. In bipolar mode only two channels are processed - left and right bipolar. In multichannel mode you can process for any number of channels using the same algorithms.

## Parameters
### Main parameters description
Structure `MathLibSettings` with fields:
1. sampling_rate - raw signal sampling frequency, Hz, integer value
2. process_win_freq - frequency of spectrum analysis and emotional levels, Hz, integer value
3. fft_window - spectrum calculation window length, integer value
4. n_first_sec_skipped - skipping the first seconds after connecting to the device, integer value
5. bipolar_mode - enabled bipolar mode, boolean value
6. squared_spectrum - mode of calculating spectral values of frequencies. If squared = true then values are calculated as the sum of squares of FFT bins of the spectrum of the interval of the corresponding frequency (e.g. alpha), if squared = false then as the sum of FFT bins.
7. channels_number - count channels for multy-channel library mode, integer value
8. channel_for_analysis - in case of multichannel mode: channel by default for computing spectral values and emotional levels, integer value

`channels_number` and `channel_for_analysis` are not used explicitly for bipolar mode, you can leave the default ones.

Separate parameters:
1. MentalEstimationMode - type of evaluation of instant mental levels - disabled by default, boolean value
2. SpectNormalizationByBandsWidth - spectrum normalization by bandwidth - disabled by default, boolean value

### Artifact detection parameters description
Structure `ArtifactDetectSetting` with fields:
1. art_bord - boundary for the long amplitude artifact, mcV, integer value
2. allowed_percent_artpoints - percent of allowed artifact points in the window, integer value
3. raw_betap_limit - boundary for spectral artifact (beta power), detection of artifacts on the spectrum occurs by checking the excess of the absolute value of the raw beta wave power, integer value
4. total_pow_border - boundary for spectral artifact (in case of assessment by total power) and for channels signal quality estimation, integer value
5. global_artwin_sec - number of seconds for an artifact sequence, the maximum number of consecutive artifact windows (on both channels) before issuing a prolonged artifact notification / device position check, integer value  
6. spect_art_by_totalp - assessment of spectral artifacts by total power, boolean value
7. hanning_win_spectrum - setting the smoothing of the spectrum calculation by Hamming, boolean value
8. hamming_win_spectrum - setting the smoothing of the spectrum calculation by Henning, boolean value
9. num_wins_for_quality_avg - number of windows for estimation of signals quality, by default = 100, which, for example, with process_win_freq=25Hz, will be equal to 4 seconds, integer value

Structure `ShortArtifactDetectSetting` with fields:
1. ampl_art_detect_win_size - the length of the sliding window segments for the detection of short-term amplitude artifacts, ms, integer value
2. ampl_art_zerod_area - signal replacement area of the previous non-artefact to the left and right of the extremum point, ms, integer value
3. ampl_art_extremum_border - boundary for the extremum considered to be artifactual, mcV, integer value

Structure `MentalAndSpectralSetting` with fields:
1. n_sec_for_instant_estimation - the number of seconds to calculate the values of mental levels, integer value
2. n_sec_for_averaging - spectrum averaging, integer value

Separate setting is the number of windows after the artifact with the previous actual value - to smooth the switching process after artifacts (`SkipWinsAfterArtifact`).

## Initialization
### Main parameters

```python
mls = lib_settings.MathLibSetting(sampling_rate=250,
                                  process_win_freq=25,
                                  n_first_sec_skipped=4,
                                  fft_window=1000,
                                  bipolar_mode=True,
                                  squared_spectrum=True,
                                  channels_number=4,
                                  channel_for_analysis=0)

ads = lib_settings.ArtifactDetectSetting(art_bord=110,
                                         allowed_percent_artpoints=70,
                                         raw_betap_limit=800_000,
                                         global_artwin_sec=4,
                                         num_wins_for_quality_avg=125,
                                         hamming_win_spectrum=True,
                                         hanning_win_spectrum=False,
                                         total_pow_border=400_000_000,
                                         spect_art_by_totalp=True)

sads = lib_settings.ShortArtifactDetectSetting(ampl_art_detect_win_size=200,
                                               ampl_art_zerod_area=200,
                                               ampl_art_extremum_border=25)

mss = lib_settings.MentalAndSpectralSetting(n_sec_for_averaging=2,
                                            n_sec_for_instant_estimation=4)

math = EmotionalMath(mls, ads, sads, mss)
```

### Optional parameters

```python
# setting calibration length
calibration_length = 6
math.set_calibration_length(calibration_length)

# type of evaluation of instant mental levels
independent_mental_levels = False
math.set_mental_estimation_mode(independent_mental_levels)

# number of windows after the artifact with the previous actual value
nwins_skip_after_artifact = 10
math.set_skip_wins_after_artifact(nwins_skip_after_artifact)

# calculation of mental levels relative to calibration values
math.set_zero_spect_waves(True, 0, 1, 1, 1, 0)

# spectrum normalization by bandwidth
math.set_spect_normalization_by_bands_width(True)
```

## Types
#### RawChannels
Structure contains left and right bipolar values to bipolar library mode with fields:
1. LeftBipolar - left bipolar value, double value
2. RightBipolar - right bipolar value, double value

#### RawChannelsArray
Structure contains array of values of channels with field:
1. channels - double array

#### MindData
Mental levels. Struct with fields:
1. Rel_Attention - relative attention value
2. Rel_Relaxation - relative relaxation value
3. Inst_Attention - instantiate attention value
4. Inst_Relaxation - instantiate relaxation value

#### SpectralDataPercents
Relative spectral values. Struct with double fields:
1. Delta
2. Theta
3. Alpha
4. Beta
5. Gamma

#### SideType
Side of current artufact. Enum with values:
1. LEFT
2. RIGHT
3. NONE

## Usage
1. If you need calibration start calibration right after library init:

```python
math.start_calibration()
``` 

2. Adding and process data
In bipolar mode:

```python
def on_brain_bit_signal_data_received(sensor, data):
    raw_channels = []
    for sample in data:
        left_bipolar = sample.T3-sample.O1
        right_bipolar = sample.T4-sample.O2
        raw_channels.append(support_classes.RawChannels(left_bipolar, right_bipolar))
    
    math.push_data(raw_channels)
    math.process_data_arr()
...
sensor.signalDataReceived = on_brain_bit_signal_data_received
``` 

In multy-channel mode:

```python
samples = []
math.push_data_arr(samples)
math.process_data_arr()
``` 
2. Then check calibration status if you need to calibrate values:

```python
calibration_finished = math.calibration_finished()
# and calibration progress
calibration_progress = math.get_calibration_percents()
``` 
3. If calibration finished (or you don't need to calibrate) read output values:

```python
# Reading mental levels in percent
mental_data = math.read_mental_data_arr()
# Reading relative spectral values in percent
sp_data = math.read_spectral_data_percents_arr()
``` 
4. Check artifacts
4.1. During calibration

```python
if math.is_both_sides_artifacted():
    # signal corruption
``` 
4.2. After (without) calibration

```python
if math.is_artifacted_sequence():
    # signal corruption
``` 
## Finishing work with the library

```python
del math
``` 
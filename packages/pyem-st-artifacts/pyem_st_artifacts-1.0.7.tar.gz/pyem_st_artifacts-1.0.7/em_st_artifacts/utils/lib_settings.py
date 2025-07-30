from dataclasses import dataclass


@dataclass
class MathLibSetting:
    sampling_rate: int = 250
    process_win_freq: int = 25
    fft_window: int = 1000
    n_first_sec_skipped: int = 4
    bipolar_mode: bool = True
    squared_spectrum: bool = True
    channels_number: int = 4
    channel_for_analysis: int = 0


@dataclass
class ArtifactDetectSetting:
    art_bord: int = 110
    allowed_percent_artpoints: int = 70
    raw_betap_limit: int = 800000
    total_pow_border: int = 100
    global_artwin_sec: int = 4
    spect_art_by_totalp: bool = False
    hanning_win_spectrum: bool = False
    hamming_win_spectrum: bool = False
    num_wins_for_quality_avg: int = 100


@dataclass
class ShortArtifactDetectSetting:
    ampl_art_detect_win_size: int = 200
    ampl_art_zerod_area: int = 200
    ampl_art_extremum_border: int = 25


@dataclass
class MentalAndSpectralSetting:
    n_sec_for_instant_estimation: int = 2
    n_sec_for_averaging: int = 2

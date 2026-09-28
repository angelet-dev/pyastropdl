from dataclasses import dataclass, field
from pathlib import Path

import matplotlib.font_manager as fm

BASE_DIR = Path(__file__).resolve().parent
GEIST_DIR = BASE_DIR / "Geist" / "static"
IBM_DIR = BASE_DIR / "IBM_Plex_Mono"

fm.fontManager.addfont(str(GEIST_DIR / "Geist-Bold.ttf"))
fm.fontManager.addfont(str(GEIST_DIR / "Geist-Medium.ttf"))
fm.fontManager.addfont(str(GEIST_DIR / "Geist-Regular.ttf"))
fm.fontManager.addfont(str(IBM_DIR / "IBMPlexMono-Bold.ttf"))
fm.fontManager.addfont(str(IBM_DIR / "IBMPlexMono-Medium.ttf"))
fm.fontManager.addfont(str(IBM_DIR / "IBMPlexMono-Regular.ttf"))


@dataclass(frozen=True)
class RawFonts:

    geist_bold: fm.FontProperties = field(default_factory=lambda: fm.FontProperties(family="Geist", weight=700))
    geist_med: fm.FontProperties = field(default_factory=lambda: fm.FontProperties(family="Geist", weight=500))
    geist_reg: fm.FontProperties = field(default_factory=lambda: fm.FontProperties(family="Geist", weight=400))
    
    ibm_bold: fm.FontProperties = field(default_factory=lambda: fm.FontProperties(family="IBM Plex Mono", weight=700))
    ibm_med: fm.FontProperties = field(default_factory=lambda: fm.FontProperties(family="IBM Plex Mono", weight=500))
    ibm_reg: fm.FontProperties = field(default_factory=lambda: fm.FontProperties(family="IBM Plex Mono", weight=400))



@dataclass(frozen=True)
class FontSizesVideo:

    title_video: int = 21        
    axis_label_video: int = 21      
    tick_video: int = 16      
    offset: int = 12       

    hud_val: int = 21   
    hud_label: int = 21   
    hud_unit: int = 21
    hud_dots: int = 21
    hud_plabel: int = 28    
     


@dataclass(frozen=True)
class FontSizesPlots:

    title_trj: int = 21     
    axis_label_trj: int = 16    
    tick_trj: int = 12 

    title: int = 16
    axis_label: int = 12
    tick: int = 9         
    offset: int = 9 
    annotation: int = 9    
    legend: int = 12     


@dataclass(frozen=True)
class TypographyVideoPreset:

    raw_fonts: RawFonts = field(default_factory=RawFonts)
    sizes: FontSizesVideo = field(default_factory=FontSizesVideo)

    title_video: fm.FontProperties = field(init=False)
    axis_label_video: fm.FontProperties = field(init=False)
    tick_video: fm.FontProperties = field(init=False)

    offset: fm.FontProperties = field(init=False)
    hud_val: fm.FontProperties = field(init=False)
    hud_label: fm.FontProperties = field(init=False)
    hud_unit: fm.FontProperties = field(init=False) 
    hud_dots: fm.FontProperties = field(init=False) 
    hud_plabel: fm.FontProperties = field(init=False) 
    hud_title: fm.FontProperties = field(init=False)


    def __post_init__(self) -> None:
        rf = self.raw_fonts
        s = self.sizes

        def _build(font: fm.FontProperties, size: int) -> fm.FontProperties:
            f = font.copy()
            f.set_size(size)
            return f

        object.__setattr__(self, "title_video", _build(rf.geist_bold, s.title_video))
        object.__setattr__(self, "axis_label_video", _build(rf.ibm_bold, s.axis_label_video))
        object.__setattr__(self, "tick_video", _build(rf.geist_med, s.tick_video))
        object.__setattr__(self, "offset", _build(rf.ibm_bold, s.offset))
        object.__setattr__(self, "hud_val", _build(rf.ibm_med, s.hud_val))
        object.__setattr__(self, "hud_label", _build(rf.ibm_med, s.hud_label))
        object.__setattr__(self, "hud_unit", _build(rf.ibm_med, s.hud_unit))
        object.__setattr__(self, "hud_dots", _build(rf.ibm_med, s.hud_dots))
        object.__setattr__(self, "hud_plabel", _build(rf.ibm_med, s.hud_plabel))

FONTS_VIDEO = TypographyVideoPreset()

@dataclass(frozen=True)
class TypographyPlotsPreset:

    raw_fonts: RawFonts = field(default_factory=RawFonts)
    sizes: FontSizesPlots = field(default_factory=FontSizesPlots)

    title_trj: fm.FontProperties = field(init=False)
    axis_label_trj: fm.FontProperties = field(init=False)
    tick_trj: fm.FontProperties = field(init=False)

    title: fm.FontProperties = field(init=False)
    axis_label: fm.FontProperties = field(init=False)
    tick: fm.FontProperties = field(init=False)

    offset: fm.FontProperties = field(init=False)
    annotation: fm.FontProperties = field(init=False)
    legend: fm.FontProperties = field(init=False)


    def __post_init__(self) -> None:
        rf = self.raw_fonts
        s = self.sizes

        def _build(font: fm.FontProperties, size: int) -> fm.FontProperties:
            f = font.copy()
            f.set_size(size)
            return f

        object.__setattr__(self, "title_trj", _build(rf.ibm_bold, s.title_trj))
        object.__setattr__(self, "axis_label_trj", _build(rf.ibm_med, s.axis_label_trj))
        object.__setattr__(self, "tick_trj", _build(rf.ibm_bold, s.tick_trj))
        object.__setattr__(self, "title", _build(rf.ibm_bold, s.title))
        object.__setattr__(self, "axis_label", _build(rf.ibm_med, s.axis_label))
        object.__setattr__(self, "tick", _build(rf.ibm_bold, s.tick))
        object.__setattr__(self, "offset", _build(rf.ibm_bold, s.offset))
        object.__setattr__(self, "annotation", _build(rf.ibm_bold, s.annotation))
        object.__setattr__(self, "legend", _build(rf.ibm_med, s.legend))


FONTS_PLOTS = TypographyPlotsPreset()
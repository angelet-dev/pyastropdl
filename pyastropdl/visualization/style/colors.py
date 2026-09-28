from dataclasses import dataclass, field


@dataclass(frozen=True)
class Palette:
    black: str = "#000000"
    rich_black: str = "#040404" 
    white: str = "#FFFFFF"
    dark_charcoal: str = "#1f1e1e"
    off_black_alpha: str = "#13131357" 
    dark_graphite: str = "#232222"
    gunmetal: str = "#414141"
    silver: str = "#c4c4c4"
    gainsboro: str = "#DCDCDC"

    amber: str = "#FFB300"
    electric_mint: str = "#00FFAA"
    bright_coral: str = "#FF2A2A"
    electric_mint_alpha: str = "#00FFAA78"
    dark_spruce: str = "#1a2f2c"

    cerulean_cyan: str = "#09b1dc"
    crimson: str = "#dc0910"
    pale_teal: str = "#80ffe1"
    ice_mint: str = "#b2f5ea"

PALETTE = Palette()

@dataclass(frozen=True)
class DarkThemePreset:
    palette: Palette = field(default_factory=Palette)

    free_fall: str = field(init=False)
    braking: str = field(init=False)
    crash: str = field(init=False)
    zero_line: str = field(init=False)


    v_axes_fc: str = field(init=False)
    bg_main: str = field(init=False)
    bg_axes: str = field(init=False)
    back_grid_fc: str = field(init=False)  
    grid: str = field(init=False)
    text: str = field(init=False)


    v_hline: str = field(init=False)
    hline: str = field(init=False)
    vline: str = field(init=False)
    ff_line: str = field(init=False)
    bp_line: str = field(init=False)
    wbp_line: str = field(init=False)
    point: str = field(init=False)


    legend_fc: str = field(init=False)
    legend_ec: str = field(init=False)
    annotation_fc: str = field(init=False)
    annotation_ec: str = field(init=False)

    black: str = field(init=False)
    white: str = field(init=False)


    video_title: str = field(init=False)
    accent_blue: str = field(init=False)
    accent_red: str = field(init=False)
    hud_val: str = field(init=False)
    hud_label: str = field(init=False)
    hud_unit: str = field(init=False) 
    hud_dots: str = field(init=False) 
    hud_plabel_b: str = field(init=False) 
    hud_plabel_l: str = field(init=False) 
    hud_plabel_ff: str = field(init=False) 

    def __post_init__(self) -> None:
        p = self.palette
        
        object.__setattr__(self, "free_fall", p.amber)
        object.__setattr__(self, "braking", p.electric_mint)
        object.__setattr__(self, "crash", p.bright_coral)
        object.__setattr__(self, "zero_line", p.electric_mint_alpha)

        object.__setattr__(self, "v_axes_fc", p.rich_black)
        object.__setattr__(self, "bg_main", p.dark_charcoal)
        object.__setattr__(self, "bg_axes", p.dark_graphite)
        object.__setattr__(self, "back_grid_fc", p.black)
        object.__setattr__(self, "grid", p.gunmetal)
        object.__setattr__(self, "text", p.silver)

        object.__setattr__(self, "v_hline", p.electric_mint_alpha)
        object.__setattr__(self, "hline", p.gainsboro)
        object.__setattr__(self, "vline", p.gainsboro)
        object.__setattr__(self, "ff_line", p.amber)
        object.__setattr__(self, "bp_line", p.electric_mint)
        object.__setattr__(self, "wbp_line", p.bright_coral)
        object.__setattr__(self, "point", p.crimson)

        object.__setattr__(self, "legend_fc", p.dark_charcoal)
        object.__setattr__(self, "legend_ec", p.gunmetal)
        object.__setattr__(self, "annotation_fc", p.gunmetal)
        object.__setattr__(self, "annotation_ec", p.silver)

        object.__setattr__(self, "black", p.black)
        object.__setattr__(self, "white", p.white)

        object.__setattr__(self, "video_title", p.white)
        object.__setattr__(self, "accent_blue", p.cerulean_cyan)
        object.__setattr__(self, "accent_red", p.crimson)
        object.__setattr__(self, "hud_label", p.pale_teal)
        object.__setattr__(self, "hud_dots", p.dark_spruce)
        object.__setattr__(self, "hud_unit", p.ice_mint)
        object.__setattr__(self, "hud_val", p.white)
        object.__setattr__(self, "hud_plabel_b", p.amber)
        object.__setattr__(self, "hud_plabel_ff", p.bright_coral)
        object.__setattr__(self, "hud_plabel_l", p.electric_mint)

COLORS = DarkThemePreset()
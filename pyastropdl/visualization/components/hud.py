import matplotlib.offsetbox as osb

from pyastropdl.core.utils.types import (
    AnyType,
    FloatArray,
    MplAnchoredBox,
    MplAxes,
    MplTextArea,
)
from pyastropdl.visualization.style import COLORS, FONTS_VIDEO

HUD_TEMPLATE = r"""
[ PHASE: BRAKING ] 

-- TIME --------------------------- 
MISSION TIME | ....... | [ 00:02:45 ] 
NEXT EVENT | ......... | [ 00:00:14 ] 

-- KINEMATICS --------------------- 
ALTITUDE | ........... | 9,999,000 | m 
VELOCITY | ......... | -12.5 | m/s 

-- PROPULSION --------------------- 
ENGINE THRUST | ...... | [ 100 % ] 
PROP MASS | .......... | 12,630 | kg 
FLOW RATE | .......... | 10.0 | kg/s 
"""


def get_element_style(s_tag: str) -> dict[str, AnyType]:
    STYLES = {
        "S_VAL": {"fontproperties": FONTS_VIDEO.hud_val, "color": COLORS.hud_val},
        "S_LABEL": {"fontproperties": FONTS_VIDEO.hud_label, "color": COLORS.hud_label},
        "S_UNIT": {"fontproperties": FONTS_VIDEO.hud_unit, "color": COLORS.hud_unit},
        "S_DOTS": {"fontproperties": FONTS_VIDEO.hud_dots, "color": COLORS.hud_dots},
        "S_PLABEL": {"fontproperties": FONTS_VIDEO.hud_plabel, "color": COLORS.hud_plabel_ff,
        },
    }
    return STYLES.get(s_tag, {})


def multi_color_line(
    ax: MplAxes, line_data: tuple[list[str], list[str]], position: tuple[float, float]
) -> tuple[MplAnchoredBox, list[MplTextArea]]:

    text_segments, style_tags = line_data
    text_areas = [
        osb.TextArea(seg, textprops=get_element_style(tag))
        for seg, tag in zip(text_segments, style_tags)
    ]

    hpacker = osb.HPacker(children=text_areas, pad=0, align="baseline")
    anchored_box = osb.AnchoredOffsetbox(
        loc="lower left",
        child=hpacker,
        bbox_to_anchor=position,
        bbox_transform=ax.transAxes,
        frameon=False,
        pad=0,
        borderpad=0,
    )
    ax.add_artist(anchored_box)
    return anchored_box, text_areas


def parse_hud_template(
    ax: MplAxes,
    template_str: str,
    x_start: float = 0.0,
    y_start: float = 0.98,
    rh: float = 60 / 790,
) -> tuple[dict[str, MplTextArea], list[MplAnchoredBox]]:

    lines = template_str.split("\n")
    current_y = y_start
    dynamic_fields = {}
    artists = []

    for line in lines:
        if not line.strip():
            current_y -= rh * 0.5
            continue

        parts = [p for p in line.split(r"|")]
        n_parts = len(parts)

        if n_parts == 1:
            tag = "S_PLABEL" if parts[0].startswith("[") else "S_LABEL"
            box, areas = multi_color_line(ax, (parts, [tag]), (x_start, current_y))
            if parts[0].startswith("["):
                dynamic_fields["phase"] = areas[0]
            artists.append(box)

        elif n_parts in (3, 4):
            tags = ["S_LABEL", "S_DOTS", "S_VAL"]
            if n_parts == 4:
                tags.append("S_UNIT")

            box, areas = multi_color_line(ax, (parts, tags), (x_start, current_y))
            artists.append(box)

            key = parts[0].strip().lower().replace(" ", "_")
            dynamic_fields[key] = areas[2]

        current_y -= rh
    return dynamic_fields, artists


def form_update_data(
    state_history: FloatArray, 
    free_fall_phase:FloatArray, 
    phys_params: tuple[float, float, float], 
    n: int, 
    phase: str
) -> dict[str, AnyType]:
    
    ts = state_history[3, 0]
    tau = state_history[3, -1]
    m_dry = phys_params[2]

    if phase == "free_fall":
        t_val = free_fall_phase[3, n]
        ne_val = ts - t_val
        prop_mass = free_fall_phase[0, n] - m_dry
        mass_flow = 0.0
        alt = free_fall_phase[2, n]
        vel = free_fall_phase[1, n]
        phase_text = "[ PHASE: FREE FALL ]"
        engine_thrust = 0

    elif phase == "braking":
        t_val = state_history[3, n]
        ne_val = tau - t_val
        prop_mass = state_history[0, n] - m_dry
        mass_flow = phys_params[0] * phys_params[1]
        alt = state_history[2, n]
        vel = state_history[1, n]
        phase_text = "[ PHASE: BRAKING ]"
        engine_thrust = 100

    elif phase == "landed":
        t_val = state_history[3, n]
        ne_val = tau - t_val
        prop_mass = state_history[0, n] - m_dry
        mass_flow = 0
        alt = state_history[2, n]
        vel = state_history[1, n]
        phase_text = "[ PHASE: LANDED ]"
        engine_thrust = 0

    hours, minutes, seconds = int(t_val // 3600), int((t_val % 3600) // 60), t_val % 60
    ne_hour, ne_min, ne_sec = (
        int(ne_val // 3600),
        int((ne_val % 3600) // 60),
        ne_val % 60,
    )

    return {
        "mission_time": f"[ {hours:02d}:{minutes:02d}:{seconds:04.1f} ]",
        "next_event": f"[ {ne_hour:02d}:{ne_min:02d}:{ne_sec:04.1f} ]",
        "altitude": f"{alt:,.0f}",
        "velocity": f"{vel:,.1f}",
        "prop_mass": f"{prop_mass:,.1f}",
        "flow_rate": f"{mass_flow:,.2f}",
        "phase_text": {"key": phase, "value": phase_text},
        "engine_thrust": f"[ {engine_thrust}% ]",
    }


def update_hud(
    dynamic_fields: dict[str, MplTextArea], 
    anchored_boxes: list[MplAnchoredBox], 
    params_to_update: dict[str, AnyType]
) -> None:

    for key, data in params_to_update.items():
        if key in dynamic_fields:
            dynamic_fields[key].set_text(data)

    phase_text_element = anchored_boxes[0].get_child().get_children()[0]
    phase_text = params_to_update.get("phase_text", {}).get("value", "")
    phase_text_key = params_to_update.get("phase_text", {}).get("key", "")

    if phase_text_element.get_text() != phase_text:
        phase_text_element.set_text(phase_text)

        match phase_text_key:
            case "free_fall":
                phase_text_element._text.set_color(COLORS.hud_plabel_ff)
            case "braking":
                phase_text_element._text.set_color(COLORS.hud_plabel_b)
            case "landed":
                phase_text_element._text.set_color(COLORS.hud_plabel_l)

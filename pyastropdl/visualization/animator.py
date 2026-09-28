import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec
from matplotlib.animation import FuncAnimation
from matplotlib.ticker import MultipleLocator

from pyastropdl.core import Solver
from pyastropdl.core.utils.paths import resolve_output_path
from pyastropdl.core.utils.tools import get_data_bounds
from pyastropdl.core.utils.types import MplLine, PathType
from pyastropdl.visualization.components import (
    HUD_TEMPLATE,
    form_update_data,
    parse_hud_template,
    target_zoom,
    update_hud,
)
from pyastropdl.visualization.style import (
    COLORS,
    FONTS_VIDEO,
    apply_dark_theme,
    set_back_grid,
    set_video,
)


class Animator:
    def __init__(self, solver: 'Solver') -> None:
        self.init_cond = solver.init_cond
        self.phys_params = solver.phys_params 

        if solver.state_history is None or solver.ffphase is None:
            raise ValueError("Phase data is incomplete or missing. Unable to animate.")

        self.dt = solver.dt
        self.free_fall_phase = solver.ffphase
        self.braking_phase = solver.state_history
        self.crash_phase = solver.wbphase

        data = (self.braking_phase, self.free_fall_phase, self.crash_phase)
        limits = get_data_bounds(data)
        self.vel_bounds = limits[2:4]
        self.alt_bounds = limits[4:6]


        self.fig = None
        self.point = None
        self.fps = None
        self.duration = None


        self.total_frames = 0
        self.active_anim_frames = 0
        self.zoom_frames = 0
        self.steps_per_frame = 0.0
        self.total_ff_frames = 0

    def setup_canvas(self) -> None:
        self.fig = plt.figure(figsize=(16, 9), dpi=120, facecolor=COLORS.black)

        width_ratios = [100, 135, 720, 110, 795, 60]
        height_ratios = [100, 790, 90, 100]

        gs = gridspec.GridSpec(
            nrows=4,
            ncols=6,
            figure=self.fig,
            width_ratios=width_ratios,
            height_ratios=height_ratios,
            hspace=0,
            wspace=0,
        )

        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1, hspace=0, wspace=0)
        
        back_grid = self.fig.add_subplot(gs[:, :])
        set_back_grid(back_grid)

        self.ax_title = self.fig.add_subplot(gs[3, 4])
        self.ax_main = self.fig.add_subplot(gs[1, 2])
        self.ax_hud = self.fig.add_subplot(gs[1, 4])

        apply_dark_theme(self.fig, (self.ax_title, self.ax_main, self.ax_hud))

        self.ax_main.set_facecolor(COLORS.v_axes_fc)
        self.ax_title.axis("off")
        self.ax_hud.axis("off")

    def _init_anim(self) -> tuple[MplLine, MplLine, MplLine, MplLine]:
        self.ax_main.axhline(0, color=COLORS.v_hline, linestyle="--", lw=3)
        
        self.ff_line, = self.ax_main.plot([], [], color=COLORS.ff_line, lw=4.5)
        self.bp_line, = self.ax_main.plot([], [], color=COLORS.bp_line, lw=4.5)
        self.wbp_line, = self.ax_main.plot([], [], color=COLORS.wbp_line, lw=3, linestyle="--")
        self.point, = self.ax_main.plot([], [], color=COLORS.point, marker="o", markersize=12)

        title_opts = {
            "fontproperties": FONTS_VIDEO.title_video,
            "va": "center",
            "ha": "left",
            "color": COLORS.video_title
        }

        title_text = "LUNAR SOFT LANDING -\n1D DESCENT TRAJECTORY"
        self.ax_title.text(0.4, 1, title_text, **title_opts)
        
        self.hud, self.anchored_boxes = parse_hud_template(self.ax_hud, HUD_TEMPLATE)

        init_vel, init_alt = self.init_cond[1], self.init_cond[2]
        self.ax_main.xaxis.set_major_locator(MultipleLocator(20.0))
        self.ax_main.yaxis.set_major_locator(MultipleLocator(1000.0))
        
        self.ax_main.set_xlim(init_vel - 50, init_vel + 50)
        self.ax_main.set_ylim(init_alt - 500, init_alt + 500)

        self.ff_line.set_data([], [])
        self.bp_line.set_data([init_vel], [init_alt])
        self.point.set_data([init_vel], [init_alt])

        set_video(self.ax_main)

        return self.ff_line, self.bp_line, self.wbp_line, self.point

    def _precalculate_animation_params(self) -> None:

        self.total_frames = int(self.fps * self.duration)
        self.active_anim_frames = int(max(self.duration - 1.5, 1) * self.fps)
        self.zoom_frames = int(1.5 * self.fps)

        free_fall_steps = self.free_fall_phase.shape[1]
        braking_steps = self.braking_phase.shape[1]
        total_active_steps = free_fall_steps + braking_steps
        
        ff_ratio = free_fall_steps / total_active_steps
        self.total_ff_frames = int(np.round(self.active_anim_frames * ff_ratio))
        self.total_bp_frames = self.active_anim_frames - self.total_ff_frames

    def update(self, frame_idx: int) -> tuple[MplLine, MplLine, MplLine, MplLine]:
        

        free_fall_steps = self.free_fall_phase.shape[1]
        braking_steps = self.braking_phase.shape[1]
        crash_steps = self.crash_phase.shape[1]


        if frame_idx <= self.total_ff_frames:
            progress = frame_idx / self.total_ff_frames if self.total_ff_frames > 0 else 1.0
            step = int(np.round(progress * (free_fall_steps - 1)))
            
            vel = self.free_fall_phase[1, : step + 1]
            alt = self.free_fall_phase[2, : step + 1]
            
            self.ff_line.set_data(vel, alt)
            
            hud_data = form_update_data(
                self.braking_phase, self.free_fall_phase, self.phys_params, step, phase="free_fall"
            )
            
            if frame_idx == self.total_ff_frames:
                self.ax_main.plot([vel[step]], [alt[step]], marker="o", color=COLORS.ff_line, markersize=10)
        

        else:
            frames_since_ignition = frame_idx - self.total_ff_frames

            if self.total_bp_frames > 0:
                progress = min(frames_since_ignition / self.total_bp_frames, 1.0)
            else:
                progress = 1.0

            crash_step = int(np.round(progress * (crash_steps - 1)))
            
            vel_crash = self.crash_phase[1, : crash_step + 1]
            alt_crash = self.crash_phase[2, : crash_step + 1]
            self.wbp_line.set_data(vel_crash, alt_crash)


            step = int(np.round(progress * (braking_steps - 1)))
            vel = self.braking_phase[1, : step + 1]
            alt = self.braking_phase[2, : step + 1]
            self.bp_line.set_data(vel, alt)


            if frame_idx >= self.active_anim_frames:
                dv = self.vel_bounds[1] - self.vel_bounds[0]
                dh = self.alt_bounds[1] - self.alt_bounds[0]
                
                start_center = (vel[step], alt[step])
                target_center = (dv / 2, dh / 2)
                view_bounds = (50, 2500, dv * 0.55, dh * 0.55)

                curr_zoom_frame = frame_idx - self.active_anim_frames
                
                target_zoom(
                    self.ax_main, start_center, target_center, 
                    view_bounds, curr_zoom_frame, self.zoom_frames
                )
                
                hud_data = form_update_data(
                    self.braking_phase, self.free_fall_phase, self.phys_params, step, phase="landed"
                )
            

            else:
                hud_data = form_update_data(
                    self.braking_phase, self.free_fall_phase, self.phys_params, step, phase="braking"
                )


        update_hud(self.hud, self.anchored_boxes, hud_data)
        self.point.set_data([vel[step]], [alt[step]])


        if frame_idx < self.active_anim_frames:
            view_width, view_height = 50.0, 2500.0
            self.ax_main.set_xlim(vel[step] - view_width, vel[step] + view_width)
            self.ax_main.set_ylim(alt[step] - view_height, alt[step] + view_height)

        if frame_idx + 1 == self.total_frames:
            print(f"\rRendered frames: {frame_idx + 1}/{self.total_frames}", flush=True)
        else:
            print(f"\rRendered frames: {frame_idx + 1}/{self.total_frames}", end="", flush=True)

        return self.ff_line, self.bp_line, self.wbp_line, self.point

    def animate(self, fps: int, duration: int, fname: str | PathType = 'trajectory.mp4') -> FuncAnimation:
        self.fps, self.duration = fps, duration
        self.setup_canvas()
        self._precalculate_animation_params()
        
        anim = FuncAnimation(
            fig=self.fig,
            func=self.update,
            init_func=self._init_anim,
            frames=self.total_frames,
            interval=1000 / fps,
            blit=False,
        )

        output_path = resolve_output_path(fname)
        anim.save(output_path, writer="ffmpeg", fps=fps, dpi=120)

        return anim
"""
GRADIENT DESCENT — Cinematic Instagram Reel
=============================================
Manim Community Edition script.

INSTALL:
    pip install manim
    # you also need ffmpeg + (optionally) LaTeX for MathTex, e.g.:
    #   brew install ffmpeg mactex        (mac)
    #   sudo apt install ffmpeg texlive-full   (linux)

RENDER (vertical 1080x1920 @ 60fps, highest quality):
    manim -pqk --resolution 1080,1920 --fps 60 gradient_descent_reel.py GradientDescentReel

    -p  = preview after render
    -qk = 4K quality preset (we override resolution/fps below anyway)

    For a quick draft pass first (much faster):
    manim -pql --resolution 1080,1920 --fps 30 gradient_descent_reel.py GradientDescentReel

OUTPUT:
    media/videos/gradient_descent_reel/1080p60/GradientDescentReel.mp4

NOTE ON "UNREAL ENGINE / GLASSMORPHISM / VOLUMETRIC LIGHT":
    Manim is a vector + basic-3D renderer, not a path tracer or game engine.
    This script gets you dark neon glow, glassy panels, 3D surfaces, camera
    moves, particles, and glowing trails — genuinely cinematic for an
    educational reel. True volumetric fog / real-time GI / lens blur are
    out of scope for Manim itself. If you want that final 10%, export this
    render and pass it through After Effects / DaVinci Resolve with a
    bloom + glow + subtle DOF pass on top.
"""

import numpy as np
import random
from manim import *

# ------------------------------------------------------------------
# GLOBAL CONFIG — vertical reel, 60fps, dark background
# ------------------------------------------------------------------
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 60
config.frame_height = 14.2          # taller vertical frame in "manim units"
config.frame_width = config.frame_height * (1080 / 1920)
config.background_color = "#05050b"

# ------------------------------------------------------------------
# PALETTE — neon blue / cyan / purple / magenta
# ------------------------------------------------------------------
NEON_BLUE    = "#3B82F6"
NEON_CYAN    = "#22D3EE"
NEON_PURPLE  = "#A855F7"
NEON_MAGENTA = "#EC4899"
NEON_WHITE   = "#F5F7FF"
DARK_PANEL   = "#0B0B18"
GRID_LINE    = "#1B1B33"

NEON_CYCLE = [NEON_BLUE, NEON_CYAN, NEON_PURPLE, NEON_MAGENTA]


# ====================================================================
# HELPER FUNCTIONS — glow effects, particles, glass panels
# ====================================================================

def glow_copies(mobject, color, layers=6, width_step=3, opacity_start=0.35):
    """Return a VGroup of blurred-looking stroke copies behind `mobject`
    to fake a neon glow (Manim has no native gaussian blur)."""
    group = VGroup()
    for i in range(layers, 0, -1):
        copy = mobject.copy()
        copy.set_stroke(color=color, width=width_step * i, opacity=opacity_start * (i / layers))
        copy.set_fill(opacity=0)
        group.add(copy)
    group.add(mobject.copy().set_color(color))
    return group


def glow_text(text, color=NEON_CYAN, size=64, weight=BOLD, font="Helvetica Neue"):
    """A glowing headline: soft halo copies + crisp white core."""
    try:
        core = Text(text, font=font, weight=weight, font_size=size, color=WHITE)
    except Exception:
        core = Text(text, weight=weight, font_size=size, color=WHITE)
    halo = VGroup(*[
        core.copy().set_color(color).set_opacity(0.12 * (1 - i / 8)).scale(1 + i * 0.012)
        for i in range(8, 0, -1)
    ])
    return VGroup(halo, core)


def glow_dot(point, color=NEON_CYAN, radius=0.06, layers=5):
    """A single glowing particle / ball marker."""
    g = VGroup()
    for i in range(layers, 0, -1):
        g.add(Dot(point, radius=radius * (1 + i * 0.55), color=color, fill_opacity=0.10 * (layers - i + 1) / layers))
    g.add(Dot(point, radius=radius, color=WHITE, fill_opacity=1))
    return g


def particle_field(n=60, x_range=(-7, 7), y_range=(-13, 13), colors=NEON_CYCLE, seed=7):
    """Ambient floating background particles for depth."""
    rnd = random.Random(seed)
    dots = VGroup()
    for _ in range(n):
        p = np.array([rnd.uniform(*x_range), rnd.uniform(*y_range), 0])
        c = rnd.choice(colors)
        r = rnd.uniform(0.01, 0.035)
        dots.add(Dot(p, radius=r, color=c, fill_opacity=rnd.uniform(0.25, 0.7)))
    return dots


def drift_particles(scene, particles, run_time=4, shift=0.6):
    """Slow ambient drift + twinkle animation for particle_field."""
    anims = []
    rnd = random.Random(3)
    for p in particles:
        dx = rnd.uniform(-shift, shift)
        dy = rnd.uniform(-shift, shift)
        anims.append(p.animate.shift(np.array([dx, dy, 0])).set_opacity(rnd.uniform(0.15, 0.8)))
    scene.play(LaggedStart(*anims, lag_ratio=0.01), run_time=run_time, rate_func=there_and_back)


def glass_panel(width, height, color=NEON_CYAN, corner_radius=0.25, fill_opacity=0.06):
    """A frosted-glass-style rounded rectangle (approximation)."""
    panel = RoundedRectangle(
        width=width, height=height, corner_radius=corner_radius,
        fill_color=DARK_PANEL, fill_opacity=fill_opacity + 0.55,
        stroke_color=color, stroke_width=1.5, stroke_opacity=0.9,
    )
    inner_line = RoundedRectangle(
        width=width - 0.06, height=height - 0.06, corner_radius=corner_radius,
        stroke_color=WHITE, stroke_width=0.5, stroke_opacity=0.15, fill_opacity=0,
    )
    return VGroup(panel, inner_line)


def loss_surface_func(x, y):
    """Bowl-shaped convex loss landscape z = f(x, y)."""
    return 0.35 * (x ** 2 + y ** 2) + 0.4 * np.sin(x) * np.cos(y) * 0.3


def loss_1d(x):
    """1D loss curve used for scene 6 (learning-rate comparison)."""
    return (x - 0.0) ** 2


def flash_transition(scene, color=NEON_CYAN):
    """Quick full-screen light flash used as a scene transition."""
    flash = FullScreenRectangle(fill_color=color, fill_opacity=0, stroke_width=0)
    scene.add(flash)
    scene.play(flash.animate.set_fill(opacity=0.55), run_time=0.12, rate_func=rush_into)
    scene.play(flash.animate.set_fill(opacity=0), run_time=0.22, rate_func=rush_from)
    scene.remove(flash)


# ====================================================================
# MAIN SCENE
# ====================================================================
class GradientDescentReel(ThreeDScene):
    def construct(self):
        self.camera.background_color = config.background_color

        self.scene_1_hook()
        flash_transition(self, NEON_CYAN)
        self.scene_2_goal()
        flash_transition(self, NEON_BLUE)
        self.scene_3_gradient_vector()
        flash_transition(self, NEON_PURPLE)
        self.scene_4_descent_steps()
        flash_transition(self, NEON_MAGENTA)
        self.scene_5_formula()
        flash_transition(self, NEON_CYAN)
        self.scene_6_learning_rates()
        flash_transition(self, NEON_BLUE)
        self.scene_7_regression_example()
        flash_transition(self, NEON_PURPLE)
        self.scene_8_global_minimum()
        flash_transition(self, WHITE)
        self.scene_9_outro()

    # ----------------------------------------------------------------
    # SCENE 1 — HOOK
    # ----------------------------------------------------------------
    def scene_1_hook(self):
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES, zoom=1)
        bg_particles = particle_field(70)
        self.add_fixed_in_frame_mobjects(bg_particles)
        self.play(FadeIn(bg_particles, lag_ratio=0.01), run_time=0.8)

        title = glow_text("How Machines\nActually Learn", color=NEON_CYAN, size=76)
        title.move_to(ORIGIN)
        self.add_fixed_in_frame_mobjects(title)
        title.set_opacity(0)
        self.play(
            FadeIn(title, shift=UP * 0.4),
            title.animate.set_opacity(1),
            run_time=1.0,
        )
        self.wait(0.5)
        drift_particles(self, bg_particles, run_time=1.2)

        # subtitle punch-in
        sub = Text("The math behind every AI model", font_size=30, color=GREY_B)
        sub.next_to(title, DOWN, buff=0.6)
        self.add_fixed_in_frame_mobjects(sub)
        self.play(FadeIn(sub, shift=UP * 0.2), run_time=0.5)
        self.wait(0.5)

        self.play(FadeOut(title, shift=UP * 0.3), FadeOut(sub, shift=UP * 0.2), run_time=0.5)

        # 3D loss-surface reveal + rapid zoom-in
        axes = ThreeDAxes(
            x_range=[-4, 4, 1], y_range=[-4, 4, 1], z_range=[0, 6, 1],
            x_length=7, y_length=7, z_length=5,
        )
        surface = Surface(
            lambda u, v: axes.c2p(u, v, loss_surface_func(u, v)),
            u_range=[-4, 4], v_range=[-4, 4],
            resolution=(40, 40), fill_opacity=0.85, checkerboard_colors=[NEON_BLUE, NEON_PURPLE],
            stroke_color=NEON_CYAN, stroke_width=0.4, stroke_opacity=0.5,
        )
        self.move_camera(phi=70 * DEGREES, theta=-60 * DEGREES, zoom=0.5)
        self.play(FadeOut(bg_particles), run_time=0.3)
        self.play(Create(surface), run_time=1.4, rate_func=smooth)
        self.begin_ambient_camera_rotation(rate=0.15)
        self.move_camera(zoom=1.6, phi=55 * DEGREES, run_time=1.3, rate_func=rush_into)
        self.wait(0.4)
        self.stop_ambient_camera_rotation()

        self.surface = surface
        self.axes = axes
        self.move_camera(zoom=1.0, phi=65 * DEGREES, theta=-50 * DEGREES, run_time=0.6)

    # ----------------------------------------------------------------
    # SCENE 2 — GOAL
    # ----------------------------------------------------------------
    def scene_2_goal(self):
        axes, surface = self.axes, self.surface

        start_x, start_y = 3.0, -3.2
        start_point = axes.c2p(start_x, start_y, loss_surface_func(start_x, start_y))
        ball = Sphere(radius=0.13, resolution=(12, 12)).set_color(NEON_MAGENTA)
        ball.move_to(start_point)
        ball_glow = Sphere(radius=0.28, resolution=(8, 8)).set_color(NEON_MAGENTA).set_opacity(0.25)
        ball_glow.move_to(start_point)

        self.play(FadeIn(ball_glow), GrowFromCenter(ball), run_time=0.6)

        label = Text("Goal: Find the Lowest Error", font_size=34, color=WHITE, weight=BOLD)
        label_bg = glass_panel(label.width + 0.8, label.height + 0.5, color=NEON_MAGENTA)
        label_group = VGroup(label_bg, label).arrange(ORIGIN)
        label_group.to_edge(UP, buff=1.0)
        self.add_fixed_in_frame_mobjects(label_group)
        label_group.set_opacity(0)
        self.play(label_group.animate.set_opacity(1), run_time=0.5)

        self.move_camera(phi=60 * DEGREES, theta=-40 * DEGREES, zoom=1.1, run_time=1.5)
        self.wait(0.6)

        self.play(FadeOut(label_group), run_time=0.4)
        self.ball, self.ball_glow = ball, ball_glow
        self.cur_x, self.cur_y = start_x, start_y

    # ----------------------------------------------------------------
    # SCENE 3 — GRADIENT VECTOR
    # ----------------------------------------------------------------
    def scene_3_gradient_vector(self):
        axes = self.axes
        x, y = self.cur_x, self.cur_y

        # numerical gradient of loss_surface_func
        h = 1e-3
        dzdx = (loss_surface_func(x + h, y) - loss_surface_func(x - h, y)) / (2 * h)
        dzdy = (loss_surface_func(x, y + h) - loss_surface_func(x, y - h)) / (2 * h)
        grad_vec = np.array([dzdx, dzdy, 0])
        grad_unit = grad_vec / np.linalg.norm(grad_vec)

        base = axes.c2p(x, y, loss_surface_func(x, y))
        uphill_tip = axes.c2p(x + grad_unit[0] * 1.4, y + grad_unit[1] * 1.4,
                               loss_surface_func(x + grad_unit[0] * 1.4, y + grad_unit[1] * 1.4))
        downhill_tip = axes.c2p(x - grad_unit[0] * 1.4, y - grad_unit[1] * 1.4,
                                 loss_surface_func(x - grad_unit[0] * 1.4, y - grad_unit[1] * 1.4))

        up_arrow = Arrow3D(start=base, end=uphill_tip, color=NEON_MAGENTA, thickness=0.02, height=0.25, base_radius=0.05)
        label_up = Text("Steepest Ascent (Gradient)", font_size=26, color=NEON_MAGENTA, weight=BOLD)
        label_up.to_edge(UP, buff=1.0)
        self.add_fixed_in_frame_mobjects(label_up)
        label_up.set_opacity(0)

        self.play(GrowFromPoint(up_arrow, base), label_up.animate.set_opacity(1), run_time=0.8)
        self.wait(0.5)

        down_arrow = Arrow3D(start=base, end=downhill_tip, color=NEON_CYAN, thickness=0.02, height=0.25, base_radius=0.05)
        label_down = Text("Move Opposite to the Gradient", font_size=26, color=NEON_CYAN, weight=BOLD)
        label_down.to_edge(UP, buff=1.0)
        self.add_fixed_in_frame_mobjects(label_down)
        label_down.set_opacity(0)

        self.play(
            Transform(up_arrow, down_arrow),
            FadeOut(label_up),
            run_time=0.9,
        )
        self.play(label_down.animate.set_opacity(1), run_time=0.4)
        self.wait(0.6)

        self.play(FadeOut(up_arrow), FadeOut(label_down), run_time=0.4)
        self.grad_unit = grad_unit

    # ----------------------------------------------------------------
    # SCENE 4 — DESCENT STEPS + GLOWING TRAIL
    # ----------------------------------------------------------------
    def scene_4_descent_steps(self):
        axes = self.axes
        ball, ball_glow = self.ball, self.ball_glow
        x, y = self.cur_x, self.cur_y
        lr = 0.35
        trail_points = [axes.c2p(x, y, loss_surface_func(x, y))]

        title = Text("Gradient Descent, Step by Step", font_size=30, color=WHITE, weight=BOLD)
        title.to_edge(UP, buff=1.0)
        self.add_fixed_in_frame_mobjects(title)
        title.set_opacity(0)
        self.play(title.animate.set_opacity(1), run_time=0.4)

        trail = VGroup()
        n_steps = 9
        for i in range(n_steps):
            h = 1e-3
            dzdx = (loss_surface_func(x + h, y) - loss_surface_func(x - h, y)) / (2 * h)
            dzdy = (loss_surface_func(x, y + h) - loss_surface_func(x, y - h)) / (2 * h)
            x -= lr * dzdx
            y -= lr * dzdy
            z = loss_surface_func(x, y)
            new_point = axes.c2p(x, y, z)

            segment = Line3D(trail_points[-1], new_point, color=NEON_CYCLE[i % 4], thickness=0.012)
            trail.add(segment)
            trail_points.append(new_point)

            step_color = NEON_CYCLE[i % 4]
            step_marker = Dot3D(new_point, radius=0.05, color=step_color)

            self.play(
                ball.animate.move_to(new_point),
                ball_glow.animate.move_to(new_point).set_color(step_color),
                Create(segment),
                FadeIn(step_marker, scale=0.3),
                run_time=0.32,
                rate_func=rush_into,
            )
            # subtle camera follow
            if i % 3 == 0:
                self.move_camera(theta=(-50 + i * 3) * DEGREES, run_time=0.3)

        self.wait(0.4)
        self.play(FadeOut(title), run_time=0.4)
        self.cur_x, self.cur_y = x, y
        self.trail = trail

    # ----------------------------------------------------------------
    # SCENE 5 — THE FORMULA
    # ----------------------------------------------------------------
    def scene_5_formula(self):
        self.move_camera(phi=0, theta=-90 * DEGREES, zoom=1, run_time=1.0)
        self.play(FadeOut(self.surface), FadeOut(self.trail), FadeOut(self.ball), FadeOut(self.ball_glow), run_time=0.6)

        formula = Text("θ = θ - α ∇J(θ)", font_size=60, color=WHITE)
        formula.set_color(WHITE)
        formula_glow = glow_copies(formula, NEON_CYAN, layers=5)
        group = VGroup(formula_glow, formula).move_to(ORIGIN)
        self.add_fixed_in_frame_mobjects(group)
        group.set_opacity(0)

        # animate term-by-term build
        parts = formula
        self.play(FadeIn(parts[0], shift=UP * 0.3), group.animate.set_opacity(1), run_time=0.5)
        for i in range(1, len(parts)):
            self.play(FadeIn(parts[i], shift=UP * 0.2), run_time=0.35)
        self.wait(0.3)

        # highlight learning rate alpha
        alpha = parts[4]
        highlight_ring = SurroundingRectangle(alpha, color=NEON_MAGENTA, buff=0.15, corner_radius=0.1)
        alpha_glow = glow_copies(alpha, NEON_MAGENTA, layers=6)
        self.add_fixed_in_frame_mobjects(alpha_glow, highlight_ring)
        self.play(
            alpha.animate.set_color(NEON_MAGENTA),
            Create(highlight_ring),
            FadeIn(alpha_glow),
            run_time=0.6,
        )
        caption = Text("The Learning Rate", font_size=30, color=NEON_MAGENTA, weight=BOLD)
        caption.next_to(formula, DOWN, buff=0.8)
        self.add_fixed_in_frame_mobjects(caption)
        self.play(FadeIn(caption, shift=UP * 0.2), run_time=0.4)
        self.wait(0.9)

        self.play(FadeOut(VGroup(group, alpha_glow, highlight_ring, caption)), run_time=0.5)

    # ----------------------------------------------------------------
    # SCENE 6 — LEARNING RATE COMPARISON (SPLIT SCREEN)
    # ----------------------------------------------------------------
    def scene_6_learning_rates(self):
        header = Text("Choosing the Learning Rate", font_size=34, color=WHITE, weight=BOLD)
        header.to_edge(UP, buff=0.9)
        self.add_fixed_in_frame_mobjects(header)
        header.set_opacity(0)
        self.play(header.animate.set_opacity(1), run_time=0.5)

        configs = [
            ("Too Small", NEON_BLUE, 0.05, 40, False),
            ("Optimal", NEON_CYAN, 0.35, 14, True),
            ("Too Large", NEON_MAGENTA, 1.05, 10, False),
        ]

        panels = VGroup()
        for label_text, color, lr, steps, converges in configs:
            ax = Axes(
                x_range=[0, steps, max(1, steps // 5)], y_range=[0, 5, 1],
                x_length=2.6, y_length=3.6,
                axis_config={"color": GRID_LINE, "stroke_width": 1.5},
            )
            xs = list(range(steps))
            pos = 4.0
            ys = []
            for _ in xs:
                grad = 2 * pos
                pos -= lr * grad
                ys.append(min(abs(pos) ** 2 if converges else abs(pos) + random.uniform(-0.2, 0.2) * (0 if converges else 1), 5))
            if not converges and lr < 0.1:
                ys = [5 * np.exp(-0.05 * i) for i in xs]  # slow crawl
            if not converges and lr > 1.0:
                ys = [min(4.5 * (1 + 0.3 * np.sin(i)) * (1 + i * 0.05), 5) for i in xs]  # diverging oscillation

            curve_points = [ax.c2p(i, y) for i, y in enumerate(ys)]
            curve = VMobject(color=color, stroke_width=4)
            curve.set_points_smoothly(curve_points)
            curve_glow = glow_copies(curve, color, layers=4)

            panel_label = Text(label_text, font_size=24, color=color, weight=BOLD)
            panel_label.next_to(ax, UP, buff=0.15)

            panel_bg = glass_panel(3.0, 4.6, color=color)
            panel_content = VGroup(panel_bg, ax, curve_glow, curve, panel_label)
            panels.add(panel_content)

        panels.arrange(RIGHT, buff=0.35)
        panels.scale(0.85)
        panels.move_to(ORIGIN)
        self.add_fixed_in_frame_mobjects(panels)
        panels.set_opacity(0)

        self.play(LaggedStart(*[p.animate.set_opacity(1) for p in panels], lag_ratio=0.25), run_time=1.4)
        self.wait(1.0)

        verdict = Text("The right rate = fast AND stable convergence", font_size=24, color=NEON_CYAN)
        verdict.to_edge(DOWN, buff=1.1)
        self.add_fixed_in_frame_mobjects(verdict)
        self.play(FadeIn(verdict, shift=UP * 0.2), run_time=0.5)
        self.wait(0.8)

        self.play(FadeOut(panels), FadeOut(header), FadeOut(verdict), run_time=0.5)

    # ----------------------------------------------------------------
    # SCENE 7 — REAL REGRESSION EXAMPLE
    # ----------------------------------------------------------------
    def scene_7_regression_example(self):
        header = Text("Watch It Learn a Real Line", font_size=32, color=WHITE, weight=BOLD)
        header.to_edge(UP, buff=0.9)
        self.add_fixed_in_frame_mobjects(header)
        header.set_opacity(0)
        self.play(header.animate.set_opacity(1), run_time=0.5)

        # synthetic data
        rnd = random.Random(1)
        xs = np.linspace(-3, 3, 18)
        true_m, true_b = 1.4, 0.3
        ys = true_m * xs + true_b + np.array([rnd.uniform(-0.8, 0.8) for _ in xs])

        ax_main = Axes(x_range=[-4, 4, 1], y_range=[-6, 6, 2], x_length=5.6, y_length=5.6,
                        axis_config={"color": GRID_LINE})
        ax_main.move_to(UP * 1.0)
        dots = VGroup(*[Dot(ax_main.c2p(x, y), radius=0.045, color=NEON_CYAN, fill_opacity=0.85) for x, y in zip(xs, ys)])

        ax_loss = Axes(x_range=[0, 20, 5], y_range=[0, 12, 3], x_length=3.6, y_length=2.2,
                        axis_config={"color": GRID_LINE})
        ax_loss.next_to(ax_main, DOWN, buff=0.8)
        loss_label = Text("Loss", font_size=20, color=GREY_B).next_to(ax_loss, UP, buff=0.1)

        group = VGroup(ax_main, dots, ax_loss, loss_label)
        self.add_fixed_in_frame_mobjects(group)
        group.set_opacity(0)
        self.play(group.animate.set_opacity(1), run_time=0.6)

        # gradient descent on m, b (simple linear regression)
        m, b = -1.0, -3.0
        lr = 0.02
        n_iters = 20
        loss_history = []

        def mse(m_, b_):
            preds = m_ * xs + b_
            return np.mean((preds - ys) ** 2)

        line = Line(ax_main.c2p(-4, m * -4 + b), ax_main.c2p(4, m * 4 + b), color=NEON_MAGENTA, stroke_width=5)
        line_glow = glow_copies(line, NEON_MAGENTA, layers=4)
        self.add_fixed_in_frame_mobjects(line_glow, line)

        loss_curve = VMobject(color=NEON_PURPLE, stroke_width=4)
        self.add_fixed_in_frame_mobjects(loss_curve)

        for i in range(n_iters):
            preds = m * xs + b
            error = preds - ys
            dm = np.mean(2 * error * xs)
            db = np.mean(2 * error)
            m -= lr * dm
            b -= lr * db
            loss_history.append(mse(m, b))

            new_line = Line(ax_main.c2p(-4, m * -4 + b), ax_main.c2p(4, m * 4 + b), color=NEON_MAGENTA, stroke_width=5)
            new_glow = glow_copies(new_line, NEON_MAGENTA, layers=4)

            loss_pts = [ax_loss.c2p(j, min(v, 12)) for j, v in enumerate(loss_history)]
            new_loss_curve = VMobject(color=NEON_PURPLE, stroke_width=4)
            if len(loss_pts) > 1:
                new_loss_curve.set_points_smoothly(loss_pts)

            self.play(
                Transform(line, new_line),
                Transform(line_glow, new_glow),
                Transform(loss_curve, new_loss_curve),
                run_time=0.18,
                rate_func=linear,
            )

        self.wait(0.6)
        self.play(FadeOut(group), FadeOut(line), FadeOut(line_glow), FadeOut(loss_curve), FadeOut(header), run_time=0.5)

    # ----------------------------------------------------------------
    # SCENE 8 — GLOBAL MINIMUM REACHED
    # ----------------------------------------------------------------
    def scene_8_global_minimum(self):
        self.move_camera(phi=65 * DEGREES, theta=-50 * DEGREES, zoom=1.0, run_time=0.1)
        axes = self.axes
        surface2 = Surface(
            lambda u, v: axes.c2p(u, v, loss_surface_func(u, v)),
            u_range=[-4, 4], v_range=[-4, 4], resolution=(40, 40),
            fill_opacity=0.85, checkerboard_colors=[NEON_BLUE, NEON_PURPLE],
            stroke_color=NEON_CYAN, stroke_width=0.4, stroke_opacity=0.5,
        )
        min_point = axes.c2p(0, 0, loss_surface_func(0, 0))
        ball = glow_dot(min_point, color=NEON_CYAN, radius=0.1)
        # glow_dot builds 2D dots; convert to fixed-in-frame-safe 3D marker instead:
        ball3d = Sphere(radius=0.13, resolution=(12, 12)).set_color(NEON_CYAN).move_to(min_point)

        self.play(FadeIn(surface2), run_time=0.5)
        self.play(FadeIn(ball3d, scale=0.3), run_time=0.4)
        self.move_camera(zoom=1.5, run_time=1.0)

        label = Text("Global Minimum Reached", font_size=32, color=NEON_CYAN, weight=BOLD)
        label.to_edge(UP, buff=1.0)
        self.add_fixed_in_frame_mobjects(label)
        label.set_opacity(0)
        self.play(label.animate.set_opacity(1), run_time=0.4)

        # energy pulse rings (2D overlay, fixed in frame, centered on screen)
        pulse_center = ORIGIN
        rings = VGroup()
        for i in range(3):
            ring = Circle(radius=0.1, color=NEON_CYCLE[i], stroke_width=6)
            ring.move_to(pulse_center)
            rings.add(ring)
        self.add_fixed_in_frame_mobjects(rings)

        self.play(
            *[ring.animate.scale(14).set_stroke(opacity=0) for ring in rings],
            run_time=1.1,
            lag_ratio=0.15,
        )

        # particle explosion
        explosion = VGroup()
        rnd = random.Random(9)
        for _ in range(90):
            angle = rnd.uniform(0, TAU)
            dist = rnd.uniform(1.5, 6.5)
            end_pt = np.array([np.cos(angle) * dist, np.sin(angle) * dist, 0])
            color = rnd.choice(NEON_CYCLE)
            p = Dot(ORIGIN, radius=rnd.uniform(0.02, 0.05), color=color, fill_opacity=1)
            explosion.add(p)
        self.add_fixed_in_frame_mobjects(explosion)

        anims = []
        rnd2 = random.Random(9)
        for p in explosion:
            angle = rnd2.uniform(0, TAU)
            dist = rnd2.uniform(1.5, 6.5)
            end_pt = np.array([np.cos(angle) * dist, np.sin(angle) * dist, 0])
            anims.append(p.animate.move_to(end_pt).set_opacity(0))
        self.play(LaggedStart(*anims, lag_ratio=0.005), run_time=1.0, rate_func=rush_from)

        self.wait(0.3)
        self.play(FadeOut(label), FadeOut(surface2), FadeOut(ball3d), FadeOut(explosion), FadeOut(rings), run_time=0.5)

    # ----------------------------------------------------------------
    # SCENE 9 — OUTRO
    # ----------------------------------------------------------------
    def scene_9_outro(self):
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES, zoom=1)

        headline = glow_text("Gradient Descent", color=NEON_CYAN, size=64)
        subhead = Text("The Engine Behind Machine Learning", font_size=30, color=WHITE, weight=BOLD)
        headline.move_to(UP * 3.6)
        subhead.next_to(headline, DOWN, buff=0.5)

        self.add_fixed_in_frame_mobjects(headline, subhead)
        headline.set_opacity(0)
        subhead.set_opacity(0)
        self.play(FadeIn(headline, shift=UP * 0.3), headline.animate.set_opacity(1), run_time=0.6)
        self.play(FadeIn(subhead, shift=UP * 0.2), subhead.animate.set_opacity(1), run_time=0.5)

        items = ["Neural Networks", "Linear Regression", "Deep Learning", "LLMs"]
        item_group = VGroup()
        for i, txt in enumerate(items):
            dot = Dot(radius=0.08, color=NEON_CYCLE[i])
            label = Text(txt, font_size=32, color=WHITE, weight=BOLD)
            row = VGroup(dot, label).arrange(RIGHT, buff=0.35)
            panel = glass_panel(row.width + 1.0, row.height + 0.4, color=NEON_CYCLE[i])
            entry = VGroup(panel, row)
            row.move_to(panel.get_center())
            item_group.add(entry)

        item_group.arrange(DOWN, buff=0.35)
        item_group.move_to(DOWN * 0.4)
        self.add_fixed_in_frame_mobjects(item_group)
        item_group.set_opacity(0)

        self.play(
            LaggedStart(*[entry.animate.set_opacity(1) for entry in item_group], lag_ratio=0.25),
            run_time=1.4,
        )
        self.wait(0.8)

        # ambient particles rising for premium outro feel
        outro_particles = particle_field(50, colors=NEON_CYCLE, seed=22)
        self.add_fixed_in_frame_mobjects(outro_particles)
        outro_particles.set_opacity(0)
        self.play(outro_particles.animate.set_opacity(0.5), run_time=0.6)

        rise_anims = [p.animate.shift(UP * random.uniform(1, 3)).set_opacity(0) for p in outro_particles]
        self.play(LaggedStart(*rise_anims, lag_ratio=0.01), run_time=2.0)

        logo = Text("AI EXPLAINED", font_size=26, color=NEON_PURPLE, weight=BOLD)
        logo_glow = glow_copies(logo, NEON_PURPLE, layers=4)
        logo_group = VGroup(logo_glow, logo).to_edge(DOWN, buff=1.0)
        self.add_fixed_in_frame_mobjects(logo_group)
        logo_group.set_opacity(0)
        self.play(logo_group.animate.set_opacity(1), run_time=0.5)
        self.wait(1.0)

        self.play(
            FadeOut(headline), FadeOut(subhead), FadeOut(item_group), FadeOut(logo_group),
            run_time=0.8,
        )
        self.wait(0.3)

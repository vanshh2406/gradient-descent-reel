"""
AI GRADIENT DESCENT — 15-18s Instagram Reel
Manim Community v0.20.1
No LaTeX. No external assets. No custom fonts. Runs headless on GitHub Actions.

RENDER:
    manim -qh --resolution 1080,1920 --fps 60 reel.py AIGradientDescentReel

OUTPUT:
    media/videos/reel/1080p60/AIGradientDescentReel.mp4
"""

from manim import *

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 60
config.background_color = "#05050b"
config.frame_height = 8
config.frame_width = config.frame_height * (1080 / 1920)

CYAN = "#22D3EE"
BLUE = "#3B82F6"
PURPLE = "#A855F7"


def glow_text(text, color=CYAN, font_size=60, weight=BOLD):
    core = Text(text, font_size=font_size, weight=weight, color=WHITE)
    halo = VGroup(*[
        core.copy().set_color(color).set_opacity(0.10 * (1 - i / 6)).scale(1 + i * 0.02)
        for i in range(6, 0, -1)
    ])
    return VGroup(halo, core)


def glow_dot3d(point, color=CYAN, radius=0.14):
    inner = Sphere(radius=radius, resolution=(10, 10)).set_color(color).move_to(point)
    outer = Sphere(radius=radius * 2.2, resolution=(8, 8)).set_color(color)
    outer.set_opacity(0.18).move_to(point)
    return VGroup(outer, inner)


def loss_fn(x, y):
    return 0.25*(x**2+y**2) + 0.25*np.sin(1.5*x)*np.cos(1.5*y)

class AIGradientDescentReel(ThreeDScene):
    def construct(self):
        self.camera.background_color = "#05050b"
        self.scene_1_hook()
        self.scene_2_landscape()
        self.scene_3_descent()
        self.scene_4_formula()
        self.scene_5_outro()

    # ---------------- SCENE 1 : ~0-2s ----------------
    def scene_1_hook(self):
        title = glow_text("How Does AI Learn?", color=CYAN, font_size=60)
        sub = Text("In 15 Seconds", font_size=34, color=BLUE, weight=BOLD)
        title.move_to(UP * 0.6)
        sub.next_to(title, DOWN, buff=0.4)

        title.scale(0.3).set_opacity(0)
        sub.set_opacity(0)
        self.add(title, sub)

        self.play(title.animate.scale(1 / 0.3).set_opacity(1), run_time=0.7, rate_func=rush_from)
        self.play(sub.animate.set_opacity(1), run_time=0.35, rate_func=smooth)
        self.wait(0.55)
        self.play(FadeOut(title), FadeOut(sub), run_time=0.3)

    # ---------------- SCENE 2 : ~2-6s ----------------
    def scene_2_landscape(self):
        axes = ThreeDAxes(
            x_range=[-3, 3, 1], y_range=[-3, 3, 1], z_range=[0, 4, 1],
            x_length=6, y_length=6, z_length=4,
        )
        surface = Surface(
            lambda u, v: axes.c2p(u, v, loss_fn(u, v)),
            u_range=[-3, 3], v_range=[-3, 3], resolution=(26, 26),
            fill_opacity=0.9, checkerboard_colors=[BLUE, PURPLE],
            stroke_color=CYAN, stroke_width=0.3, stroke_opacity=0.4,
        )
        self.set_camera_orientation(phi=65 * DEGREES, theta=-50 * DEGREES, zoom=0.55)
        self.play(Create(surface), run_time=1.0)
        self.move_camera(zoom=1.0, run_time=0.5)

        start = axes.c2p(2.6, -2.6, loss_fn(2.6, -2.6))
        ball = glow_dot3d(start, color=CYAN)
        self.play(FadeIn(ball, scale=0.4), run_time=0.4)

        label = Text("AI starts with huge mistakes", font_size=30, color=WHITE, weight=BOLD)
        label.to_edge(UP, buff=1.0)
        self.add_fixed_in_frame_mobjects(label)
        label.set_opacity(0)
        self.play(label.animate.set_opacity(1), run_time=0.45)
        self.wait(0.9)
        self.play(FadeOut(label), run_time=0.4)

        self.axes, self.surface, self.ball = axes, surface, ball
        self.pos = (2.6, -2.6)

    # ---------------- SCENE 3 : ~6-10s ----------------
    def scene_3_descent(self):
        axes, ball = self.axes, self.ball
        x, y = self.pos
        losses = ["98%", "74%", "41%", "12%", "2%"]

        counter = Text(losses[0], font_size=52, color=PURPLE, weight=BOLD)
        counter.to_edge(UP, buff=1.0)
        self.add_fixed_in_frame_mobjects(counter)

        lr = 0.28
        for val in losses:
            h = 1e-3
            dzdx = (loss_fn(x + h, y) - loss_fn(x - h, y)) / (2 * h)
            dzdy = (loss_fn(x, y + h) - loss_fn(x, y - h)) / (2 * h)
            x -= lr * dzdx
            y -= lr * dzdy
            new_point = axes.c2p(x, y, loss_fn(x, y))

            new_counter = Text(val, font_size=52, color=PURPLE, weight=BOLD)
            new_counter.to_edge(UP, buff=1.0)

            self.play(
                ball.animate.move_to(new_point),
                Transform(counter, new_counter),
                run_time=0.65, rate_func=rush_into,
            )

        self.play(FadeOut(counter), run_time=0.3)
        self.pos = (x, y)

    # ---------------- SCENE 4 : ~10-13s ----------------
    def scene_4_formula(self):
        self.move_camera(phi=0, theta=-90 * DEGREES, zoom=1.0, run_time=0.5)
        self.play(FadeOut(self.surface), FadeOut(self.ball), run_time=0.4)

        formula = Text("theta = theta - alpha * grad J(theta)", font_size=40, color=WHITE, weight=BOLD)
        halo = VGroup(*[
            formula.copy().set_color(CYAN).set_opacity(0.1 * (1 - i / 5)).scale(1 + i * 0.02)
            for i in range(5, 0, -1)
        ])
        group = VGroup(halo, formula).move_to(ORIGIN)
        self.add_fixed_in_frame_mobjects(group)
        group.set_opacity(0)
        self.play(group.animate.set_opacity(1), run_time=0.55)
        self.wait(0.5)

        move_text = Text("Move opposite to the error", font_size=32, color=BLUE, weight=BOLD)
        move_text.move_to(ORIGIN)
        self.add_fixed_in_frame_mobjects(move_text)
        move_text.set_opacity(0)
        self.play(FadeOut(group), move_text.animate.set_opacity(1), run_time=0.6)
        self.wait(0.4)
        self.play(FadeOut(move_text), run_time=0.3)

    # ---------------- SCENE 5 : ~13-18s ----------------
    def scene_5_outro(self):
        self.set_camera_orientation(phi=65 * DEGREES, theta=-50 * DEGREES, zoom=1.0)
        surface2 = Surface(
            lambda u, v: self.axes.c2p(u, v, loss_fn(u, v)),
            u_range=[-3, 3], v_range=[-3, 3], resolution=(26, 26),
            fill_opacity=0.9, checkerboard_colors=[BLUE, PURPLE],
            stroke_color=CYAN, stroke_width=0.3, stroke_opacity=0.4,
        )
        min_pt = self.axes.c2p(0, 0, loss_fn(0, 0))
        ball = glow_dot3d(min_pt, color=CYAN, radius=0.16)
        self.play(FadeIn(surface2), FadeIn(ball, scale=0.4), run_time=0.55)

        rings = VGroup(*[Circle(radius=0.1, color=c, stroke_width=6) for c in (CYAN, BLUE, PURPLE)])
        self.add_fixed_in_frame_mobjects(rings)
        self.play(*[r.animate.scale(16).set_stroke(opacity=0) for r in rings], run_time=0.7)

        title = glow_text("This is Gradient Descent", color=CYAN, font_size=42)
        title.move_to(UP * 2.6)
        self.add_fixed_in_frame_mobjects(title)
        title.set_opacity(0)
        self.play(title.animate.set_opacity(1), run_time=0.45)

        powers = Text(
            "Powers:\n- ChatGPT\n- Neural Networks\n- LLMs",
            font_size=30, color=WHITE, weight=BOLD, line_spacing=1.2,
        )
        powers.move_to(DOWN * 1.0)
        self.add_fixed_in_frame_mobjects(powers)
        powers.set_opacity(0)
        self.play(powers.animate.set_opacity(1), run_time=0.55)
        self.wait(0.9)

        self.play(
            FadeOut(title), FadeOut(powers), FadeOut(surface2), FadeOut(ball), FadeOut(rings),
            run_time=0.6,
        )

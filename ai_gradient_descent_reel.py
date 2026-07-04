from manim import *
import numpy as np

# Vertical Reel Configuration
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9
config.frame_height = 16


class AIGradientDescentReel(ThreeDScene):
    def construct(self):
        # Colors
        BG = "#05050b"
        CYAN = "#22D3EE"
        BLUE = "#3B82F6"
        PURPLE = "#A855F7"

        self.camera.background_color = BG

        # --------------------------------------------------
        # SCENE 1 (0-2s)
        # --------------------------------------------------
        title = Text(
            "How Does AI Learn?",
            color=CYAN,
            weight=BOLD,
            font_size=64,
        )

        subtitle = Text(
            "In 15 Seconds",
            color=PURPLE,
            font_size=32,
        ).next_to(title, DOWN, buff=0.25)

        title_group = VGroup(title, subtitle)

        title_group.scale(0.6)
        self.play(
            title_group.animate.scale(1.6),
            FadeIn(title_group),
            run_time=1.2,
        )

        self.play(
            title_group.animate.scale(1.15),
            run_time=0.8,
        )

        self.play(
            FadeOut(title_group, scale=1.1),
            run_time=0.3,
        )

        # --------------------------------------------------
        # SCENE 2 (2-6s)
        # --------------------------------------------------

        axes = ThreeDAxes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            z_range=[-1, 6, 1],
            x_length=7,
            y_length=7,
            z_length=4,
        )

        def loss_surface(u, v):
            z = (
                0.22 * (u**2 + v**2)
                + 0.18 * np.sin(1.6 * u)
                + 0.15 * np.cos(1.4 * v)
            )
            return np.array([u, v, z])

        surface = Surface(
            loss_surface,
            u_range=[-3, 3],
            v_range=[-3, 3],
            resolution=(28, 28),
            fill_opacity=0.9,
            checkerboard_colors=[BLUE, PURPLE],
        )

        surface.set_stroke(CYAN, width=0.6, opacity=0.4)

        start_u = 2.4
        start_v = 2.2
        start_point = loss_surface(start_u, start_v)

        sphere = Sphere(
            radius=0.16,
            resolution=(18, 18),
        )
        sphere.set_color(CYAN)
        sphere.move_to(start_point)

        mistake_text = Text(
            "AI starts with huge mistakes",
            color=CYAN,
            font_size=32,
            weight=BOLD,
        ).to_edge(UP)

        self.set_camera_orientation(
            phi=65 * DEGREES,
            theta=-45 * DEGREES,
            zoom=1.1,
        )

        self.play(
            FadeIn(surface),
            FadeIn(sphere),
            FadeIn(mistake_text),
            run_time=1.0,
        )

        self.begin_ambient_camera_rotation(rate=0.08)

        self.play(
            sphere.animate.scale(1.15),
            run_time=1.0,
        )

        # --------------------------------------------------
        # SCENE 3 (6-10s)
        # --------------------------------------------------

        path_points = [
            (2.4, 2.2),
            (1.6, 1.4),
            (1.0, 0.8),
            (0.5, 0.3),
            (0.15, 0.1),
        ]

        loss_labels = ["98%", "74%", "41%", "12%", "2%"]

        current_label = Text(
            loss_labels[0],
            color=PURPLE,
            font_size=42,
            weight=BOLD,
        ).to_edge(DOWN)

        self.add_fixed_in_frame_mobjects(current_label)
        self.play(FadeIn(current_label), run_time=0.3)

        for i in range(1, len(path_points)):
            u, v = path_points[i]
            next_pos = loss_surface(u, v)

            new_label = Text(
                loss_labels[i],
                color=PURPLE,
                font_size=42,
                weight=BOLD,
            ).to_edge(DOWN)

            self.add_fixed_in_frame_mobjects(new_label)

            self.play(
                sphere.animate.move_to(next_pos),
                Transform(current_label, new_label),
                self.camera.animate.set_zoom(
                    1.1 + i * 0.06
                ),
                run_time=0.7,
            )

        self.play(
            FadeOut(mistake_text),
            FadeOut(current_label),
            run_time=0.3,
        )

        # --------------------------------------------------
        # SCENE 4 (10-13s)
        # --------------------------------------------------

        self.stop_ambient_camera_rotation()

        self.move_camera(
            phi=0 * DEGREES,
            theta=-90 * DEGREES,
            zoom=1.0,
            run_time=1.0,
        )

        formula = Text(
            "θ = θ − α∇J(θ)",
            color=CYAN,
            font_size=54,
            weight=BOLD,
        )

        explanation = Text(
            "Move opposite to the error",
            color=PURPLE,
            font_size=34,
        ).next_to(formula, DOWN, buff=0.4)

        formula_group = VGroup(formula, explanation)

        self.add_fixed_in_frame_mobjects(formula_group)

        self.play(
            Write(formula),
            run_time=0.8,
        )

        self.play(
            FadeIn(explanation, shift=UP * 0.2),
            run_time=0.7,
        )

        self.play(
            FadeOut(formula_group),
            run_time=0.4,
        )

        # --------------------------------------------------
        # SCENE 5 (13-18s)
        # --------------------------------------------------

        self.move_camera(
            phi=65 * DEGREES,
            theta=-45 * DEGREES,
            zoom=1.25,
            run_time=0.8,
        )

        minimum_glow = Sphere(radius=0.28)
        minimum_glow.set_color(PURPLE)
        minimum_glow.set_opacity(0.25)
        minimum_glow.move_to(loss_surface(0.0, 0.0))

        final_title = Text(
            "This is Gradient Descent",
            color=CYAN,
            font_size=50,
            weight=BOLD,
        )

        powers = Text(
            "Powers:\n• ChatGPT\n• Neural Networks\n• LLMs",
            color=PURPLE,
            font_size=28,
        ).next_to(final_title, DOWN, buff=0.35)

        outro = VGroup(final_title, powers)
        outro.to_edge(UP)

        self.add_fixed_in_frame_mobjects(outro)

        self.play(
            FadeIn(minimum_glow),
            FadeIn(outro),
            sphere.animate.scale(1.25),
            run_time=0.8,
        )

        for _ in range(2):
            self.play(
                minimum_glow.animate.scale(1.35).set_opacity(0.45),
                sphere.animate.scale(1.08),
                run_time=0.4,
            )
            self.play(
                minimum_glow.animate.scale(0.74).set_opacity(0.22),
                sphere.animate.scale(0.93),
                run_time=0.4,
            )

        self.play(
            FadeOut(outro),
            FadeOut(surface),
            FadeOut(sphere),
            FadeOut(minimum_glow),
            run_time=1.0,
        )

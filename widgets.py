import math
import random
from collections import deque
from PySide6.QtCore import Qt, QPointF, QRectF, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPen,
    QBrush,
    QPolygonF,
    QLinearGradient,
    QRadialGradient,
)
from PySide6.QtWidgets import QWidget


class CameraMode:
    CHASE = "CHASE"
    ORBIT = "ORBIT"
    FPV = "FPV"
    TOP_DOWN = "TOP-DOWN"
    ALL = [CHASE, ORBIT, FPV, TOP_DOWN]


class EnvTheme:
    DAY = "DAY"
    SUNSET = "SUNSET"
    NIGHT = "NIGHT"
    ALL = [DAY, SUNSET, NIGHT]


# Dark Carbon FPV Color Tokens
COLOR_HULL = QColor(42, 46, 54)        # #2A2E36
COLOR_CARBON = QColor(30, 34, 39)      # #1E2227
COLOR_GUNMETAL = QColor(58, 64, 72)    # #3A4048
COLOR_ACCENT_ORANGE = QColor(255, 140, 42)  # #FF8C2A
COLOR_ACCENT_CYAN = QColor(53, 213, 240)    # #35D5F0

# Environment Color Tokens
SKY_TOP = QColor(16, 32, 58)
SKY_BOTTOM = QColor(115, 155, 200)
GROUND_TOP = QColor(34, 64, 40)
GROUND_BOTTOM = QColor(15, 30, 20)
GRID_COLOR = QColor(60, 130, 80, 80)
GRID_MAJOR_COLOR = QColor(53, 213, 240, 130)


class GroundParticle:
    def __init__(self, x, y, z):
        self.x = x + random.uniform(-0.6, 0.6)
        self.y = y + random.uniform(-0.6, 0.6)
        self.z = z
        ang = random.uniform(0, 2.0 * math.pi)
        spd = random.uniform(0.6, 2.2)
        self.vx = math.cos(ang) * spd
        self.vy = math.sin(ang) * spd
        self.vz = random.uniform(0.2, 0.9)
        self.life = 1.0
        self.max_life = random.uniform(0.4, 0.8)
        self.size = random.uniform(2.5, 5.0)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt
        self.vz -= 0.8 * dt
        self.life -= dt / self.max_life
        return self.life > 0.0 and self.z >= 0.0


class SimView(QWidget):
    ARM_LEN = 1.0
    F = 550.0

    camera_mode_changed = Signal(str)
    theme_changed = Signal(str)

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.rotor_phase = 0.0
        self.strobe_timer = 0.0
        self.zoom = 1.0
        self.camera_mode = CameraMode.CHASE
        self.env_theme = EnvTheme.DAY

        # Toggles
        self.hud_visible = True
        self.radar_visible = True
        self.osd_scanlines = True
        self.spotlight_on = True

        # Camera orientation & damping
        self.cam_az = math.pi / 2.0
        self.cam_elev = math.radians(40)
        self.orbit_az = math.pi / 2.0
        self.orbit_elev = math.radians(40)
        self.orbit_vel_az = 0.0
        self.orbit_vel_el = 0.0
        self.cam_shake_x = 0.0
        self.cam_shake_y = 0.0

        # Mouse state
        self.is_dragging = False
        self.last_mouse_pos = QPointF()

        # Dust particles & history telemetry graph
        self.particles = []
        self.telemetry_history = deque(maxlen=80)  # (alt, spd)

        # World Props: 3D Racing Gates (x, y, z, radius, heading_deg)
        self.racing_gates = [
            {"pos": (7.0, 6.0, 2.2), "r": 2.2, "yaw": math.radians(30), "passed": False},
            {"pos": (-7.0, 12.0, 3.5), "r": 2.5, "yaw": math.radians(-45), "passed": False},
            {"pos": (2.0, 20.0, 4.5), "r": 2.8, "yaw": math.radians(0), "passed": False},
        ]

        # World Props: Elevated Helipad Platforms (x, y, height, radius)
        self.elevated_helipads = [
            {"pos": (12.0, -7.0), "h": 3.0, "r": 2.6, "name": "P1"},
            {"pos": (-11.0, -9.0), "h": 5.5, "r": 3.0, "name": "P2"},
        ]

        # World Props: 3D Trees (x, y, height, radius)
        self.trees = [
            {"pos": (15.0, 12.0), "h": 4.5, "r": 1.6},
            {"pos": (-14.0, 8.0), "h": 5.0, "r": 1.8},
            {"pos": (18.0, -14.0), "h": 4.2, "r": 1.5},
            {"pos": (-16.0, -16.0), "h": 5.2, "r": 1.9},
            {"pos": (5.0, -18.0), "h": 4.0, "r": 1.4},
        ]

        # Wind Turbine at (-22, 22)
        self.turbine_blade_angle = 0.0

        self.setMinimumSize(480, 360)
        self.setAutoFillBackground(False)
        self.setFocusPolicy(Qt.StrongFocus)

    # ------------------------------------------------------------------ State Toggles
    def set_camera_mode(self, mode):
        if mode in CameraMode.ALL and self.camera_mode != mode:
            self.camera_mode = mode
            if mode == CameraMode.ORBIT:
                self.orbit_az = self.cam_az
                self.orbit_elev = self.cam_elev
            elif mode == CameraMode.TOP_DOWN:
                self.cam_elev = math.radians(88)
            self.camera_mode_changed.emit(self.camera_mode)
            self.update()

    def cycle_camera_mode(self):
        idx = CameraMode.ALL.index(self.camera_mode)
        next_mode = CameraMode.ALL[(idx + 1) % len(CameraMode.ALL)]
        self.set_camera_mode(next_mode)

    def cycle_theme(self):
        idx = EnvTheme.ALL.index(self.env_theme)
        next_theme = EnvTheme.ALL[(idx + 1) % len(EnvTheme.ALL)]
        self.env_theme = next_theme
        self.theme_changed.emit(self.env_theme)
        self.update()

    def toggle_spotlight(self):
        self.spotlight_on = not self.spotlight_on
        self.update()

    def toggle_hud(self):
        self.hud_visible = not self.hud_visible
        self.update()

    def toggle_radar(self):
        self.radar_visible = not self.radar_visible
        self.update()

    def toggle_osd_scanlines(self):
        self.osd_scanlines = not self.osd_scanlines
        self.update()

    # ------------------------------------------------------------------ Camera Advance & Physics Updates
    def advance_cam(self, dt):
        self.strobe_timer = (self.strobe_timer + dt) % 1.2
        self.turbine_blade_angle = (self.turbine_blade_angle + 1.2 * dt) % (2.0 * math.pi)
        m = self.model

        # Record telemetry history
        self.telemetry_history.append((m.z, m.speed()))

        # Update Dust Particles
        if m.armed and m.z < 1.2 and m.rotor_speed > 0.1:
            if random.random() < 0.6:
                self.particles.append(GroundParticle(m.x, m.y, 0.05))

        self.particles = [p for p in self.particles if p.update(dt)]

        # Camera Speed Shake Effect
        spd = m.speed()
        if spd > 3.5:
            intensity = min(1.0, (spd - 3.5) / 10.0)
            self.cam_shake_x = math.sin(self.strobe_timer * 45.0) * 3.5 * intensity
            self.cam_shake_y = math.cos(self.strobe_timer * 38.0) * 3.5 * intensity
        else:
            self.cam_shake_x *= 0.85
            self.cam_shake_y *= 0.85

        # Check Gate Pass Logic
        for gate in self.racing_gates:
            gx, gy, gz = gate["pos"]
            dist = math.hypot(m.x - gx, math.hypot(m.y - gy, m.z - gz))
            gate["passed"] = dist < gate["r"] * 1.2

        # Camera Mode Tracking
        if self.camera_mode == CameraMode.CHASE:
            target_az = math.pi / 2.0 - m.yaw
            diff = (target_az - self.cam_az + math.pi) % (2.0 * math.pi) - math.pi
            k_az = 1.0 - math.exp(-3.5 * dt)
            self.cam_az += diff * k_az

            target_elev = math.radians(38) + max(0.0, m.z) * 0.015
            k_el = 1.0 - math.exp(-2.5 * dt)
            self.cam_elev += (target_elev - self.cam_elev) * k_el

        elif self.camera_mode == CameraMode.ORBIT:
            if not self.is_dragging:
                self.orbit_az += self.orbit_vel_az * dt
                self.orbit_elev = max(math.radians(5), min(math.radians(88), self.orbit_elev + self.orbit_vel_el * dt))
                self.orbit_vel_az *= 0.92
                self.orbit_vel_el *= 0.92

            self.cam_az = self.orbit_az
            self.cam_elev = self.orbit_elev

        elif self.camera_mode == CameraMode.TOP_DOWN:
            target_az = math.pi / 2.0 - m.yaw
            self.cam_az = target_az
            self.cam_elev = math.radians(89.5)

        elif self.camera_mode == CameraMode.FPV:
            self.cam_az = math.pi / 2.0 - m.yaw
            self.cam_elev = math.radians(0.0)

    def _cam_dist(self):
        if self.camera_mode == CameraMode.TOP_DOWN:
            return (18.0 + max(self.model.z, 0.0) * 1.5) * self.zoom
        return (10.0 + max(self.model.z, 0.0) * 1.5) * self.zoom

    # ------------------------------------------------------------------ Mouse Events
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.last_mouse_pos = event.position()
            self.orbit_vel_az = 0.0
            self.orbit_vel_el = 0.0
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            pos = event.position()
            dx = pos.x() - self.last_mouse_pos.x()
            dy = pos.y() - self.last_mouse_pos.y()
            self.last_mouse_pos = pos

            sensitivity = 0.007
            self.orbit_vel_az = -dx * 0.5
            self.orbit_vel_el = dy * 0.5

            self.orbit_az -= dx * sensitivity
            self.orbit_elev = max(math.radians(5), min(math.radians(88), self.orbit_elev + dy * sensitivity))

            if self.camera_mode != CameraMode.ORBIT:
                self.set_camera_mode(CameraMode.ORBIT)
            else:
                self.cam_az = self.orbit_az
                self.cam_elev = self.orbit_elev
                self.update()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            event.accept()

    def wheelEvent(self, event):
        steps = event.angleDelta().y() / 120.0
        self.zoom = max(0.25, min(4.5, self.zoom * (1.15 ** (-steps))))
        self.update()
        event.accept()

    # ------------------------------------------------------------------ 3D Math Projection
    def _cam(self, p):
        x, y, z = p
        m = self.model

        if self.camera_mode == CameraMode.FPV:
            cx = m.x + math.cos(m.yaw) * 0.35
            cy = m.y + math.sin(m.yaw) * 0.35
            cz = m.z + 0.18

            rx, ry, rz = x - cx, y - cy, z - cz

            cyaw, syaw = math.cos(-m.yaw), math.sin(-m.yaw)
            x1 = rx * cyaw - ry * syaw
            y1 = rx * syaw + ry * cyaw
            z1 = rz

            cpitch, spitch = math.cos(-m.pitch), math.sin(-m.pitch)
            x2 = x1 * cpitch + z1 * spitch
            y2 = y1
            z2 = -x1 * spitch + z1 * cpitch

            croll, sroll = math.cos(-m.roll), math.sin(-m.roll)
            x3 = x2
            y3 = y2 * croll - z2 * sroll
            z3 = y2 * sroll + z2 * croll

            return y3, z3, x3

        else:
            tx, ty, tz = m.x, m.y, m.z + 0.15
            rx, ry, rz = x - tx, y - ty, z - tz

            a = self.cam_az
            ca, sa = math.cos(a), math.sin(a)
            xa = rx * ca - ry * sa
            ya = rx * sa + ry * ca
            za = rz

            el = self.cam_elev - math.pi / 2.0
            ce, se = math.cos(el), math.sin(el)
            ye = ya * ce - za * se
            ze = ya * se + za * ce
            return xa, ye, ze

    def project(self, p):
        xa, ye, ze = self._cam(p)
        cx = self.width() / 2.0 + self.cam_shake_x
        cy = self.height() * (0.50 if self.camera_mode == CameraMode.TOP_DOWN else 0.55) + self.cam_shake_y

        if self.camera_mode == CameraMode.FPV:
            depth = max(0.15, ze)
            return QPointF(cx + (xa * self.F) / depth, cy - (ye * self.F) / depth)
        else:
            d = self._cam_dist()
            denom = max(0.15, d - ze)
            return QPointF(cx + (xa * self.F) / denom, cy - (ye * self.F) / denom)

    def _project_3d(self, p):
        xa, ye, ze = self._cam(p)
        cx = self.width() / 2.0 + self.cam_shake_x
        cy = self.height() * (0.50 if self.camera_mode == CameraMode.TOP_DOWN else 0.55) + self.cam_shake_y

        if self.camera_mode == CameraMode.FPV:
            depth = ze
            if depth < 0.15:
                return None, depth
            return QPointF(cx + (xa * self.F) / depth, cy - (ye * self.F) / depth), depth
        else:
            d = self._cam_dist()
            denom = d - ze
            if denom < 0.15:
                return None, denom
            return QPointF(cx + (xa * self.F) / denom, cy - (ye * self.F) / denom), denom

    def _project_or_none(self, p):
        pt, _ = self._project_3d(p)
        return pt

    def _visible(self, p):
        if p is None:
            return False
        return -250 < p.x() < self.width() + 250 and -250 < p.y() < self.height() + 250

    def _unproject_ground(self, sx, sy):
        if self.camera_mode == CameraMode.FPV:
            return None
        d = self._cam_dist()
        el = self.cam_elev - math.pi / 2.0
        cx = self.width() / 2.0
        cy = self.height() * (0.50 if self.camera_mode == CameraMode.TOP_DOWN else 0.55)
        t = math.tan(el) if abs(math.cos(el)) > 1e-4 else 100.0
        denom = d / (1.0 + (cy - sy) * t / self.F)
        if denom <= 0.15:
            return None
        xa = (sx - cx) * denom / self.F
        ye = (cy - sy) * denom / self.F
        ya = ye / (math.cos(el) if abs(math.cos(el)) > 1e-4 else 1e-4)
        ca, sa = math.cos(self.cam_az), math.sin(self.cam_az)
        rx = xa * ca + ya * sa
        ry = -xa * sa + ya * ca
        return (self.model.x + rx, self.model.y + ry)

    def _visible_ground_extent(self):
        w, h = self.width(), self.height()
        m = self.model
        samples = []
        for y in (0.0, h * 0.25, h * 0.5, h * 0.75, h):
            samples.append((0.0, y))
            samples.append((float(w), y))
        for x in (0.0, w * 0.25, w * 0.5, w * 0.75, w):
            samples.append((x, 0.0))
            samples.append((x, float(h)))
        pts = []
        for sx, sy in samples:
            g = self._unproject_ground(sx, sy)
            if g is not None:
                pts.append(g)
        if not pts:
            return (m.x - 35, m.x + 35, m.y - 35, m.y + 35)
        xs = [p[0] for p in pts] + [m.x]
        ys = [p[1] for p in pts] + [m.y]
        return min(xs), max(xs), min(ys), max(ys)

    # ------------------------------------------------------------------ Painting
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        self._draw_environment(painter, w, h)
        if self.env_theme != EnvTheme.NIGHT:
            self._draw_clouds(painter, w, h)
        else:
            self._draw_stars(painter, w, h)

        self._draw_grid(painter)
        self._draw_helipad(painter)
        self._draw_elevated_helipads(painter)
        self._draw_racing_gates(painter)
        self._draw_trees_and_props(painter)
        self._draw_dust_particles(painter)
        self._draw_trail(painter)
        self._draw_shadow(painter)
        self._draw_spotlight_beam(painter)
        self._draw_prop_wash(painter)

        if self.camera_mode != CameraMode.FPV:
            self._draw_drone_3d(painter)
        else:
            self._draw_fpv_osd(painter, w, h)

        # Dynamic Speed Lines & Alerts
        self._draw_speed_lines(painter, w, h)
        self._draw_battery_alert(painter, w, h)

        if self.hud_visible and self.camera_mode != CameraMode.FPV:
            self._draw_labels(painter)
            self._draw_telemetry_chart(painter, w, h)
            self._draw_hud(painter, w, h)

        if self.radar_visible:
            self._draw_radar(painter, w, h)

        # Border Frame
        border_col = COLOR_ACCENT_CYAN if self.env_theme != EnvTheme.SUNSET else COLOR_ACCENT_ORANGE
        painter.setPen(QPen(border_col, 1.5))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(1, 1, w - 2, h - 2, 10, 10)

    # ------------------------------------------------------------------ Environment & Themes
    def _draw_environment(self, painter, w, h):
        if self.camera_mode == CameraMode.FPV:
            horizon_pitch = math.degrees(self.model.pitch) * 4.0
            horizon_y = h * 0.5 + horizon_pitch
        else:
            horizon_p = self.project(
                (
                    self.model.x + math.cos(self.model.yaw) * 300.0,
                    self.model.y + math.sin(self.model.yaw) * 300.0,
                    0.0,
                )
            )
            horizon_y = horizon_p.y()

        hy = max(-h * 2, min(h * 3, horizon_y))

        # Palette by Theme
        if self.env_theme == EnvTheme.DAY:
            sky_top, sky_bot = SKY_TOP, SKY_BOTTOM
            gnd_top, gnd_bot = GROUND_TOP, GROUND_BOTTOM
            sun_col = QColor(255, 255, 230, 230)
        elif self.env_theme == EnvTheme.SUNSET:
            sky_top, sky_bot = QColor(45, 20, 60), QColor(235, 120, 70)
            gnd_top, gnd_bot = QColor(48, 42, 32), QColor(24, 20, 16)
            sun_col = QColor(255, 180, 80, 240)
        else:  # NIGHT
            sky_top, sky_bot = QColor(6, 8, 16), QColor(18, 24, 38)
            gnd_top, gnd_bot = QColor(12, 18, 16), QColor(6, 10, 8)
            sun_col = QColor(210, 235, 255, 190)  # Moon

        # Sky Linear Gradient
        sky = QLinearGradient(0, 0, 0, max(hy, 1))
        sky.setColorAt(0.0, sky_top)
        sky.setColorAt(1.0, sky_bot)
        painter.fillRect(0, 0, w, max(0, int(hy)), sky)

        # Sun / Moon Glow
        if hy > 10:
            sun_x = w * 0.75
            sun_y = min(hy * 0.45, h * 0.35)
            sun_grad = QRadialGradient(QPointF(sun_x, sun_y), 130)
            sun_grad.setColorAt(0.0, sun_col)
            sun_grad.setColorAt(0.35, QColor(sun_col.red(), sun_col.green(), sun_col.blue(), 100))
            sun_grad.setColorAt(1.0, QColor(sun_col.red(), sun_col.green(), sun_col.blue(), 0))
            painter.setPen(Qt.NoPen)
            painter.setBrush(sun_grad)
            painter.drawEllipse(QPointF(sun_x, sun_y), 130, 130)

        # Ground Linear Gradient
        ground = QLinearGradient(0, hy, 0, h)
        ground.setColorAt(0.0, gnd_top)
        ground.setColorAt(1.0, gnd_bot)
        painter.fillRect(0, max(0, int(hy)), w, max(0, h - int(hy)), ground)

        # Horizon Fog Band
        fog_band_h = 36
        if 0 < hy < h + fog_band_h:
            fog = QLinearGradient(0, hy - fog_band_h / 2, 0, hy + fog_band_h / 2)
            fog.setColorAt(0.0, QColor(sky_bot.red(), sky_bot.green(), sky_bot.blue(), 0))
            fog.setColorAt(0.5, QColor(sky_bot.red(), sky_bot.green(), sky_bot.blue(), 80))
            fog.setColorAt(1.0, QColor(gnd_top.red(), gnd_top.green(), gnd_top.blue(), 0))
            painter.fillRect(0, max(0, int(hy - fog_band_h / 2)), w, fog_band_h, fog)

    def _draw_clouds(self, painter, w, h):
        t = self.model.time * 0.04
        painter.setPen(Qt.NoPen)
        for i, (base_x, base_y, rw, rh) in enumerate([
            (0.2, 0.18, 90, 26),
            (0.55, 0.28, 120, 32),
            (0.85, 0.15, 80, 22),
            (-0.15, 0.22, 100, 28)
        ]):
            cx = ((base_x + t * (0.5 + i * 0.2)) % 1.4 - 0.2) * w
            cy = base_y * h * 0.75
            c_grad = QRadialGradient(QPointF(cx, cy), rw)
            c_grad.setColorAt(0.0, QColor(255, 255, 255, 40))
            c_grad.setColorAt(0.7, QColor(240, 248, 255, 20))
            c_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
            painter.setBrush(c_grad)
            painter.drawEllipse(QPointF(cx, cy), rw, rh)

    def _draw_stars(self, painter, w, h):
        # Twinkling stars at night
        painter.setPen(Qt.NoPen)
        for i in range(35):
            sx = (i * 97 + 13) % w
            sy = (i * 61 + 7) % int(h * 0.45)
            twinkle = int(140 + 100 * math.sin(self.model.time * 3.0 + i))
            painter.setBrush(QColor(220, 240, 255, twinkle))
            painter.drawEllipse(QPointF(sx, sy), 1.5, 1.5)

    def _draw_grid(self, painter):
        ext = self._visible_ground_extent()
        if ext is None:
            return
        x0, x1, y0, y1 = ext
        span = max(x1 - x0, y1 - y0)
        if span < 1e-6:
            return

        steps = [1.5, 5.0, 10.0, 25.0, 50.0, 100.0, 250.0]
        step = next((s for s in steps if span / s <= 50), steps[-1])
        major = max(1, int(round(5.0 / step)))

        grid_col = GRID_COLOR if self.env_theme != EnvTheme.NIGHT else QColor(30, 80, 70, 70)
        grid_maj = GRID_MAJOR_COLOR if self.env_theme != EnvTheme.SUNSET else COLOR_ACCENT_ORANGE

        def draw_line(ax, ay, bx, by, is_major):
            painter.setPen(QPen(grid_maj if is_major else grid_col, 2 if is_major else 1))
            subdivs = 4
            for f in range(subdivs):
                p1 = self._project_or_none(
                    (ax + (bx - ax) * f / subdivs, ay + (by - ay) * f / subdivs, 0.0)
                )
                p2 = self._project_or_none(
                    (
                        ax + (bx - ax) * (f + 1) / subdivs,
                        ay + (by - ay) * (f + 1) / subdivs,
                        0.0,
                    )
                )
                if p1 is not None and p2 is not None:
                    painter.drawLine(p1, p2)

        i = 0
        v = math.floor(x0 / step) * step
        while v <= x1 + 1e-9:
            draw_line(v, y0, v, y1, i % major == 0)
            v += step
            i += 1

        i = 0
        v = math.floor(y0 / step) * step
        while v <= y1 + 1e-9:
            draw_line(x0, v, x1, v, i % major == 0)
            v += step
            i += 1

    def _draw_helipad(self, painter):
        center = self.project((0.0, 0.0, 0.0))
        if not self._visible(center):
            return

        pts_outer = []
        pts_inner = []
        for i in range(16):
            ang = i * (2.0 * math.pi / 16.0)
            p_out = self.project((math.cos(ang) * 2.8, math.sin(ang) * 2.8, 0.0))
            p_in = self.project((math.cos(ang) * 2.2, math.sin(ang) * 2.2, 0.0))
            pts_outer.append(p_out)
            pts_inner.append(p_in)

        painter.setPen(QPen(COLOR_ACCENT_CYAN, 2))
        painter.setBrush(QColor(24, 28, 36, 190))
        painter.drawPolygon(QPolygonF(pts_outer))

        painter.setPen(QPen(QColor(255, 255, 255, 230), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawPolygon(QPolygonF(pts_inner))

        hp1 = self.project((-0.8, -1.0, 0.0))
        hp2 = self.project((-0.8, 1.0, 0.0))
        hp3 = self.project((0.8, -1.0, 0.0))
        hp4 = self.project((0.8, 1.0, 0.0))
        hpm1 = self.project((-0.8, 0.0, 0.0))
        hpm2 = self.project((0.8, 0.0, 0.0))

        painter.setPen(QPen(COLOR_ACCENT_ORANGE, 4, Qt.SolidLine, Qt.SquareCap))
        painter.drawLine(hp1, hp2)
        painter.drawLine(hp3, hp4)
        painter.drawLine(hpm1, hpm2)

        ch1 = self.project((0.0, 1.6, 0.0))
        ch2 = self.project((-0.5, 2.0, 0.0))
        ch3 = self.project((0.5, 2.0, 0.0))
        painter.setPen(QPen(COLOR_ACCENT_ORANGE, 2))
        painter.drawLine(ch1, ch2)
        painter.drawLine(ch1, ch3)

        l_pt = self.project((0.0, -3.2, 0.0))
        if self._visible(l_pt):
            painter.setFont(QFont("Consolas", 10, QFont.Bold))
            painter.setPen(COLOR_ACCENT_CYAN)
            painter.drawText(l_pt.x() - 32, l_pt.y() + 4, "HOME [0,0]")

    # ------------------------------------------------------------------ 3D Elevated Helipads, Racing Gates, & Props
    def _draw_elevated_helipads(self, painter):
        for pad in self.elevated_helipads:
            px, py = pad["pos"]
            ph = pad["h"]
            pr = pad["r"]
            pname = pad["name"]

            for leg_x, leg_y in [(-pr * 0.7, -pr * 0.7), (pr * 0.7, -pr * 0.7), (pr * 0.7, pr * 0.7), (-pr * 0.7, pr * 0.7)]:
                p_bot = self.project((px + leg_x, py + leg_y, 0.0))
                p_top = self.project((px + leg_x, py + leg_y, ph))
                if self._visible(p_bot) and self._visible(p_top):
                    painter.setPen(QPen(QColor(50, 58, 70, 220), 3))
                    painter.drawLine(p_bot, p_top)

            pts_top = []
            for i in range(8):
                ang = i * (2.0 * math.pi / 8.0)
                pt = self.project((px + math.cos(ang) * pr, py + math.sin(ang) * pr, ph))
                pts_top.append(pt)

            painter.setPen(QPen(COLOR_ACCENT_ORANGE, 2))
            painter.setBrush(QColor(28, 34, 42, 220))
            painter.drawPolygon(QPolygonF(pts_top))

            lbl_pt = self.project((px, py, ph + 0.1))
            if self._visible(lbl_pt):
                painter.setFont(QFont("Consolas", 10, QFont.Bold))
                painter.setPen(COLOR_ACCENT_ORANGE)
                painter.drawText(lbl_pt.x() - 10, lbl_pt.y() + 4, pname)

    def _draw_racing_gates(self, painter):
        for idx, gate in enumerate(self.racing_gates):
            gx, gy, gz = gate["pos"]
            gr = gate["r"]
            gyaw = gate["yaw"]
            is_passed = gate["passed"]

            ring_pts = []
            num_sides = 12
            for i in range(num_sides):
                ang = i * (2.0 * math.pi / num_sides)
                lx = 0.0
                ly = math.cos(ang) * gr
                lz = math.sin(ang) * gr

                wx = gx + lx * math.cos(gyaw) - ly * math.sin(gyaw)
                wy = gy + lx * math.sin(gyaw) + ly * math.cos(gyaw)
                wz = gz + lz

                pt = self.project((wx, wy, wz))
                ring_pts.append(pt)

            c_neon = QColor(60, 250, 160, 240) if is_passed else QColor(255, 40, 180, 230)
            painter.setPen(QPen(c_neon, 4 if is_passed else 3, Qt.SolidLine, Qt.RoundCap))
            painter.setBrush(Qt.NoBrush)
            painter.drawPolygon(QPolygonF(ring_pts))

            p_bot = self.project((gx, gy, 0.0))
            p_center = self.project((gx, gy, gz - gr))
            if self._visible(p_bot) and self._visible(p_center):
                painter.setPen(QPen(QColor(70, 80, 95, 220), 3))
                painter.drawLine(p_bot, p_center)

            lbl_pt = self.project((gx, gy, gz + gr + 0.3))
            if self._visible(lbl_pt):
                painter.setFont(QFont("Consolas", 9, QFont.Bold))
                painter.setPen(c_neon)
                painter.drawText(lbl_pt.x() - 20, lbl_pt.y(), f"GATE {idx+1}")

    def _draw_trees_and_props(self, painter):
        # 3D Low-Poly Pine Trees
        for tree in self.trees:
            tx, ty = tree["pos"]
            th = tree["h"]
            tr = tree["r"]

            # Trunk
            p_base = self.project((tx, ty, 0.0))
            p_mid = self.project((tx, ty, th * 0.3))
            if self._visible(p_base) and self._visible(p_mid):
                painter.setPen(QPen(QColor(70, 50, 35), 4))
                painter.drawLine(p_base, p_mid)

            # Cone Foliage 1 (Lower)
            pts_c1 = []
            for i in range(6):
                ang = i * (2.0 * math.pi / 6.0)
                pts_c1.append(self.project((tx + math.cos(ang) * tr, ty + math.sin(ang) * tr, th * 0.3)))
            p_tip1 = self.project((tx, ty, th * 0.7))
            if self._visible(p_tip1):
                painter.setPen(QPen(QColor(30, 75, 45), 1))
                painter.setBrush(QColor(40, 95, 55))
                painter.drawPolygon(QPolygonF(pts_c1))

            # Cone Foliage 2 (Upper)
            pts_c2 = []
            for i in range(6):
                ang = i * (2.0 * math.pi / 6.0)
                pts_c2.append(self.project((tx + math.cos(ang) * tr * 0.7, ty + math.sin(ang) * tr * 0.7, th * 0.6)))
            p_top = self.project((tx, ty, th))
            if self._visible(p_top):
                painter.setPen(QPen(QColor(40, 95, 55), 1))
                painter.setBrush(QColor(55, 125, 75))
                painter.drawPolygon(QPolygonF(pts_c2))

        # 3D Wind Turbine at (-22, 22)
        wx, wy, wh = -22.0, 22.0, 10.0
        p_tbase = self.project((wx, wy, 0.0))
        p_thub = self.project((wx, wy, wh))
        if self._visible(p_tbase) and self._visible(p_thub):
            painter.setPen(QPen(QColor(180, 190, 205), 4))
            painter.drawLine(p_tbase, p_thub)

            # 3 Rotating Turbine Blades
            for b in range(3):
                ang = self.turbine_blade_angle + b * (2.0 * math.pi / 3.0)
                btip = self.project((wx + math.cos(ang) * 4.0, wy, wh + math.sin(ang) * 4.0))
                painter.setPen(QPen(QColor(230, 240, 250), 2.5))
                painter.drawLine(p_thub, btip)

    # ------------------------------------------------------------------ 3D Spotlight Beam & Dust
    def _draw_spotlight_beam(self, painter):
        m = self.model
        if not self.spotlight_on:
            return

        nose_world = (m.x + math.cos(m.yaw) * 0.35, m.y + math.sin(m.yaw) * 0.35, m.z + 0.15)
        nose_pt = self.project(nose_world)

        # Ground Light Pool Center
        target_dist = 3.2
        target_gnd = (m.x + math.cos(m.yaw) * target_dist, m.y + math.sin(m.yaw) * target_dist, 0.0)
        gnd_pt = self.project(target_gnd)

        if not self._visible(gnd_pt):
            return

        # Ground Pool Ellipse
        r_pool = 32.0 * math.sqrt(self.zoom)
        pool_grad = QRadialGradient(gnd_pt, r_pool)
        pool_grad.setColorAt(0.0, QColor(255, 255, 230, 140))
        pool_grad.setColorAt(0.6, QColor(255, 255, 200, 60))
        pool_grad.setColorAt(1.0, QColor(255, 255, 200, 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(pool_grad)
        painter.drawEllipse(gnd_pt, r_pool, r_pool * 0.5)

        # 3D Beam Cone (from nose to ground pool)
        if self._visible(nose_pt):
            beam_pts = [
                nose_pt,
                QPointF(gnd_pt.x() - r_pool * 0.7, gnd_pt.y()),
                QPointF(gnd_pt.x() + r_pool * 0.7, gnd_pt.y()),
            ]
            beam_grad = QLinearGradient(nose_pt, gnd_pt)
            beam_grad.setColorAt(0.0, QColor(255, 255, 230, 90))
            beam_grad.setColorAt(1.0, QColor(255, 255, 200, 15))
            painter.setBrush(beam_grad)
            painter.drawPolygon(QPolygonF(beam_pts))

    def _draw_dust_particles(self, painter):
        for p in self.particles:
            pt = self.project((p.x, p.y, p.z))
            if not self._visible(pt):
                continue
            alpha = int(p.life * 130)
            sz = p.size * math.sqrt(self.zoom)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(180, 170, 150, alpha))
            painter.drawEllipse(pt, sz, sz * 0.6)

    # ------------------------------------------------------------------ Trail, Shadow, & Prop Wash
    def _draw_trail(self, painter):
        if len(self.model.trail) < 2:
            return
        pts = [self.project(pt) for pt in self.model.trail if pt is not None]
        if len(pts) < 2:
            return

        n = len(pts)
        for i in range(n - 1):
            alpha = int(40 + 190 * (i / n))
            w = max(1.5, 4.0 * (i / n) * math.sqrt(self.zoom))
            painter.setPen(QPen(QColor(COLOR_ACCENT_ORANGE.red(), COLOR_ACCENT_ORANGE.green(), COLOR_ACCENT_ORANGE.blue(), alpha), w, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(pts[i], pts[i + 1])

    def _draw_shadow(self, painter):
        shadow = self.project((self.model.x, self.model.y, 0.0))
        if not self._visible(shadow):
            return

        painter.setPen(Qt.NoPen)
        r = (30.0 / (1.0 + self.model.z * 0.12)) * math.sqrt(self.zoom)
        alpha = int(max(15, 120 / (1.0 + self.model.z * 0.2)))

        shadow_grad = QRadialGradient(shadow, max(4.0, r))
        shadow_grad.setColorAt(0.0, QColor(0, 0, 0, alpha))
        shadow_grad.setColorAt(0.7, QColor(0, 0, 0, int(alpha * 0.5)))
        shadow_grad.setColorAt(1.0, QColor(0, 0, 0, 0))

        painter.setBrush(shadow_grad)
        painter.drawEllipse(shadow, max(4.0, r), max(2.0, r * 0.45))

    def _draw_prop_wash(self, painter):
        m = self.model
        if not m.armed or m.z > 2.8 or m.rotor_speed < 0.1:
            return

        gnd = self.project((m.x, m.y, 0.0))
        if not self._visible(gnd):
            return

        intensity = (1.0 - m.z / 2.8) * m.rotor_speed
        phase = (self.strobe_timer * 3.0) % 1.0

        for ring in range(3):
            r_scale = (ring * 0.35 + phase * 0.35) + 0.4
            r_px = 45.0 * r_scale * intensity * math.sqrt(self.zoom)
            alpha = int(max(0, (1.0 - r_scale / 1.5) * 160 * intensity))

            painter.setPen(QPen(QColor(180, 240, 255, alpha), 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(gnd, r_px, r_px * 0.42)

    # ------------------------------------------------------------------ 3D Drone Faceted Engine
    def _world(self, local):
        x, y, z = local
        m = self.model
        yaw, pitch, roll = m.yaw, m.pitch, m.roll

        x1 = x * math.cos(yaw) - y * math.sin(yaw)
        y1 = x * math.sin(yaw) + y * math.cos(yaw)
        z1 = z

        y2 = y1 * math.cos(roll) - z1 * math.sin(roll)
        z2 = y1 * math.sin(roll) + z1 * math.cos(roll)
        x2 = x1

        xw = x2 * math.cos(pitch) + z2 * math.sin(pitch)
        yw = y2
        zw = -x2 * math.sin(pitch) + z2 * math.cos(pitch)

        return (m.x + xw, m.y + yw, m.z + 0.15 + zw)

    def _draw_drone_3d(self, painter):
        m = self.model
        self.rotor_phase += 0.7 + m.rotor_speed * 2.8

        # Directional light vector by theme
        if self.env_theme == EnvTheme.DAY:
            lx, ly, lz = 0.45, -0.35, 0.85
        elif self.env_theme == EnvTheme.SUNSET:
            lx, ly, lz = 0.75, -0.20, 0.35
        else:
            lx, ly, lz = 0.20, -0.20, 0.90

        l_len = math.hypot(lx, math.hypot(ly, lz))
        lx, ly, lz = lx / l_len, ly / l_len, lz / l_len

        facets = []

        def add_polygon(vertices_local, base_color, is_shiny=False):
            world_verts = [self._world(v) for v in vertices_local]
            cam_verts = [self._cam(w) for w in world_verts]
            avg_depth = sum(c[2] for c in cam_verts) / len(cam_verts)

            v0, v1, v2 = world_verts[0], world_verts[1], world_verts[2]
            e1 = (v1[0] - v0[0], v1[1] - v0[0], v1[2] - v0[2])
            e2 = (v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2])
            nx = e1[1] * e2[2] - e1[2] * e2[1]
            ny = e1[2] * e2[0] - e1[0] * e2[2]
            nz = e1[0] * e2[1] - e1[1] * e2[0]
            n_len = math.hypot(nx, math.hypot(ny, nz))
            if n_len > 1e-6:
                nx, ny, nz = nx / n_len, ny / n_len, nz / n_len
            else:
                nx, ny, nz = 0.0, 0.0, 1.0

            dot = max(0.0, nx * lx + ny * ly + nz * lz)
            ambient = 0.45
            diffuse = 0.55 * dot

            specular = 0.0
            if is_shiny:
                rx = 2.0 * dot * nx - lx
                ry = 2.0 * dot * ny - ly
                rz = 2.0 * dot * nz - lz
                specular = max(0.0, rz) ** 14 * 0.45

            r = int(min(255, base_color.red() * (ambient + diffuse) + 255 * specular))
            g = int(min(255, base_color.green() * (ambient + diffuse) + 255 * specular))
            b = int(min(255, base_color.blue() * (ambient + diffuse) + 255 * specular))
            color = QColor(r, g, b, base_color.alpha())

            screen_pts = [self.project(w) for w in world_verts]
            facets.append((avg_depth, screen_pts, color, is_shiny))

        arm_endpoints = [
            (0.707, 0.707, 0.0),    # FR
            (0.707, -0.707, 0.0),   # FL
            (-0.707, 0.707, 0.0),   # RR
            (-0.707, -0.707, 0.0),  # RL
        ]

        w_arm = 0.06
        h_arm = 0.04
        for idx, (ex, ey, ez) in enumerate(arm_endpoints):
            length = math.hypot(ex, ey)
            ux, uy = ex / length, ey / length
            px, py = -uy, ux

            c_arm = COLOR_CARBON if idx >= 2 else COLOR_GUNMETAL

            add_polygon([
                (0.0 + px * w_arm, 0.0 + py * w_arm, h_arm),
                (ex + px * w_arm, ey + py * w_arm, h_arm),
                (ex - px * w_arm, ey - py * w_arm, h_arm),
                (0.0 - px * w_arm, 0.0 - py * w_arm, h_arm),
            ], c_arm)

            add_polygon([
                (ex + px * w_arm, ey + py * w_arm, h_arm),
                (ex + px * w_arm, ey + py * w_arm, -h_arm),
                (ex - px * w_arm, ey - py * w_arm, -h_arm),
                (ex - px * w_arm, ey - py * w_arm, h_arm),
            ], COLOR_HULL)

            if idx < 2:
                add_polygon([
                    (ex * 0.6 + px * w_arm * 1.05, ey * 0.6 + py * w_arm * 1.05, h_arm * 1.05),
                    (ex * 0.8 + px * w_arm * 1.05, ey * 0.8 + py * w_arm * 1.05, h_arm * 1.05),
                    (ex * 0.8 - px * w_arm * 1.05, ey * 0.8 - py * w_arm * 1.05, h_arm * 1.05),
                    (ex * 0.6 - px * w_arm * 1.05, ey * 0.6 - py * w_arm * 1.05, h_arm * 1.05),
                ], COLOR_ACCENT_ORANGE)

            add_polygon([
                (ex - 0.03, ey - 0.03, -h_arm), (ex + 0.03, ey - 0.03, -h_arm),
                (ex + 0.03, ey + 0.03, -h_arm - 0.12), (ex - 0.03, ey + 0.03, -h_arm - 0.12)
            ], COLOR_CARBON)

        add_polygon([
            (0.20, -0.10, -0.08), (0.20, 0.10, -0.08),
            (-0.25, 0.10, -0.08), (-0.25, -0.10, -0.08)
        ], COLOR_HULL)

        add_polygon([
            (0.20, 0.10, -0.01), (0.20, 0.10, -0.08),
            (0.20, -0.10, -0.08), (0.20, -0.10, -0.01)
        ], COLOR_GUNMETAL)

        add_polygon([
            (0.04, -0.102, -0.082), (0.04, 0.102, -0.082),
            (-0.06, 0.102, -0.082), (-0.06, -0.102, -0.082)
        ], COLOR_ACCENT_ORANGE)

        c_top = COLOR_GUNMETAL
        c_side = COLOR_HULL
        c_front = QColor(100, 112, 128)

        add_polygon([(0.42, 0.0, 0.04), (0.18, 0.15, 0.08), (0.18, 0.0, 0.14)], c_front, True)
        add_polygon([(0.42, 0.0, 0.04), (0.18, 0.0, 0.14), (0.18, -0.15, 0.08)], c_front, True)
        add_polygon([(0.18, 0.15, 0.08), (-0.25, 0.14, 0.07), (0.0, 0.0, 0.16), (0.18, 0.0, 0.14)], c_top, True)
        add_polygon([(0.18, 0.0, 0.14), (0.0, 0.0, 0.16), (-0.25, -0.14, 0.07), (0.18, -0.15, 0.08)], c_top, True)
        add_polygon([(0.0, 0.0, 0.16), (-0.35, 0.0, 0.05), (-0.25, 0.14, 0.07)], c_side)
        add_polygon([(0.0, 0.0, 0.16), (-0.25, -0.14, 0.07), (-0.35, 0.0, 0.05)], c_side)

        add_polygon([
            (0.38, -0.06, 0.02), (0.38, 0.06, 0.02),
            (0.38, 0.06, -0.05), (0.38, -0.06, -0.05)
        ], COLOR_CARBON)

        add_polygon([
            (0.40, -0.04, 0.01), (0.40, 0.04, 0.01),
            (0.40, 0.04, -0.03), (0.40, -0.04, -0.03)
        ], COLOR_ACCENT_CYAN, True)

        r_m = 0.11
        h_m = 0.08
        for ex, ey, ez in arm_endpoints:
            add_polygon([
                (ex + r_m, ey, ez + h_m), (ex, ey + r_m, ez + h_m),
                (ex - r_m, ey, ez + h_m), (ex, ey - r_m, ez + h_m)
            ], COLOR_GUNMETAL)

        facets.sort(key=lambda item: item[0], reverse=True)

        for depth, screen_pts, color, is_shiny in facets:
            poly = QPolygonF(screen_pts)
            painter.setPen(QPen(QColor(15, 18, 22, 140), 1))
            painter.setBrush(color)
            painter.drawPolygon(poly)

        for idx, (ex, ey, ez) in enumerate(arm_endpoints):
            m_center_w = self._world((ex, ey, ez + h_m + 0.02))
            pt_m = self.project(m_center_w)
            if not self._visible(pt_m):
                continue

            r_blade = max(10.0, 32.0 * math.sqrt(self.zoom))

            if m.rotor_speed > 0.05:
                painter.setPen(QPen(QColor(255, 255, 255, 80), 1.5))
                painter.setBrush(QColor(230, 240, 255, 30 + int(45 * m.rotor_speed)))
                painter.drawEllipse(pt_m, r_blade, r_blade * 0.75)

            rot_dir = 1.0 if idx % 2 == 0 else -1.0
            base_angle = self.rotor_phase * rot_dir + idx * (math.pi / 2.0)

            for b in range(3):
                angle = base_angle + b * (2.0 * math.pi / 3.0)
                b_tip_local = (
                    ex + math.cos(angle) * 0.45,
                    ey + math.sin(angle) * 0.45,
                    ez + h_m + 0.03,
                )
                pt_tip = self.project(self._world(b_tip_local))

                if m.rotor_speed > 0.05:
                    painter.setPen(QPen(QColor(245, 248, 252, 210), max(1.8, 2.5 * math.sqrt(self.zoom)), Qt.SolidLine, Qt.RoundCap))
                else:
                    painter.setPen(QPen(COLOR_CARBON, max(2.0, 3.0 * math.sqrt(self.zoom)), Qt.SolidLine, Qt.RoundCap))
                painter.drawLine(pt_m, pt_tip)

            painter.setPen(QPen(QColor(20, 24, 30), 1))
            painter.setBrush(QColor(220, 230, 240))
            painter.drawEllipse(pt_m, 3.0, 3.0)

        is_strobe_on = self.strobe_timer > 0.95
        led_data = [
            (arm_endpoints[0], QColor(60, 240, 110), "FRONT_RIGHT"),
            (arm_endpoints[1], QColor(255, 255, 255), "FRONT_LEFT"),
            (arm_endpoints[2], QColor(255, 50, 50), "REAR_RIGHT"),
            (arm_endpoints[3], QColor(255, 50, 50), "REAR_LEFT"),
        ]

        for (ex, ey, ez), color, name in led_data:
            l_world = self._world((ex * 1.05, ey * 1.05, ez))
            l_pt = self.project(l_world)
            if not self._visible(l_pt):
                continue

            active_color = color
            if "REAR" in name and is_strobe_on:
                active_color = QColor(255, 255, 255)

            glow_r = 12.0 * math.sqrt(self.zoom)
            glow = QRadialGradient(l_pt, glow_r)
            glow.setColorAt(0.0, active_color)
            glow.setColorAt(0.4, QColor(active_color.red(), active_color.green(), active_color.blue(), 120))
            glow.setColorAt(1.0, QColor(active_color.red(), active_color.green(), active_color.blue(), 0))

            painter.setPen(Qt.NoPen)
            painter.setBrush(glow)
            painter.drawEllipse(l_pt, glow_r, glow_r)

            painter.setBrush(QColor(255, 255, 255) if m.armed else active_color)
            painter.drawEllipse(l_pt, 3.0, 3.0)

        tail_world = self._world((-0.38, 0.0, 0.06))
        tail_pt = self.project(tail_world)
        if self._visible(tail_pt):
            strobe_col = QColor(255, 255, 255) if is_strobe_on else QColor(80, 80, 90)
            painter.setPen(Qt.NoPen)
            painter.setBrush(strobe_col)
            painter.drawEllipse(tail_pt, 2.5, 2.5)

    # ------------------------------------------------------------------ Dynamic Speed Lines & Alerts
    def _draw_speed_lines(self, painter, w, h):
        spd = self.model.speed()
        if spd < 6.5:
            return

        intensity = min(1.0, (spd - 6.5) / 8.0)
        num_lines = int(12 * intensity)
        cx, cy = w / 2.0, h / 2.0

        painter.setPen(QPen(QColor(255, 255, 255, int(70 * intensity)), 1.5))
        for i in range(num_lines):
            ang = random.uniform(0, 2.0 * math.pi)
            r1 = min(w, h) * random.uniform(0.38, 0.45)
            r2 = min(w, h) * random.uniform(0.55, 0.65)
            p1 = QPointF(cx + math.cos(ang) * r1, cy + math.sin(ang) * r1)
            p2 = QPointF(cx + math.cos(ang) * r2, cy + math.sin(ang) * r2)
            painter.drawLine(p1, p2)

    def _draw_battery_alert(self, painter, w, h):
        m = self.model
        if m.battery < 20.0:
            pulse = int(120 * (0.5 + 0.5 * math.sin(self.model.time * 6.0)))
            painter.setPen(QPen(QColor(239, 68, 68, pulse), 4))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(3, 3, w - 6, h - 6, 8, 8)

        # Ground Proximity / Descent Alarm
        if m.z < 1.4 and m.vz < -2.0 and m.armed:
            painter.setFont(QFont("Consolas", 12, QFont.Bold))
            painter.setPen(QColor(255, 50, 50, 230))
            painter.drawText(QRectF(0, h * 0.35, w, 24), Qt.AlignCenter, "⚠ WARNING: LOW ALTITUDE / PULL UP ⚠")

    # ------------------------------------------------------------------ Telemetry Trend Graph
    def _draw_telemetry_chart(self, painter, w, h):
        if len(self.telemetry_history) < 2:
            return

        gw, gh = 150, 48
        gx, gy = 8, h - 84
        self._panel(painter, QRectF(gx, gy, gw, gh), 150, 6)

        painter.setFont(QFont("Consolas", 7, QFont.Bold))
        painter.setPen(COLOR_ACCENT_CYAN)
        painter.drawText(gx + 6, gy + 11, "ALT (m)")
        painter.setPen(COLOR_ACCENT_ORANGE)
        painter.drawText(gx + gw - 46, gy + 11, "SPD (m/s)")

        # Sparklines
        n = len(self.telemetry_history)
        step = (gw - 12) / max(1, n - 1)
        max_alt = 20.0
        max_spd = 15.0

        pts_alt = []
        pts_spd = []
        for i, (alt, spd) in enumerate(self.telemetry_history):
            px = gx + 6 + i * step
            py_alt = gy + gh - 4 - max(0.0, min(1.0, alt / max_alt)) * (gh - 18)
            py_spd = gy + gh - 4 - max(0.0, min(1.0, spd / max_spd)) * (gh - 18)
            pts_alt.append(QPointF(px, py_alt))
            pts_spd.append(QPointF(px, py_spd))

        painter.setPen(QPen(COLOR_ACCENT_CYAN, 1.5))
        for i in range(len(pts_alt) - 1):
            painter.drawLine(pts_alt[i], pts_alt[i + 1])

        painter.setPen(QPen(COLOR_ACCENT_ORANGE, 1.5))
        for i in range(len(pts_spd) - 1):
            painter.drawLine(pts_spd[i], pts_spd[i + 1])

    # ------------------------------------------------------------------ FPV Betaflight OSD Overlay
    def _draw_fpv_osd(self, painter, w, h):
        m = self.model
        cx, cy = w / 2.0, h / 2.0

        if self.osd_scanlines:
            painter.setPen(QPen(QColor(0, 0, 0, 22), 1))
            for y in range(0, h, 4):
                painter.drawLine(0, y, w, y)

        # Reticle Crosshair
        painter.setPen(QPen(COLOR_ACCENT_CYAN, 2))
        painter.drawLine(int(cx - 20), int(cy), int(cx - 6), int(cy))
        painter.drawLine(int(cx + 6), int(cy), int(cx + 20), int(cy))
        painter.drawLine(int(cx), int(cy - 20), int(cx), int(cy - 6))
        painter.drawLine(int(cx), int(cy + 6), int(cx), int(cy + 20))
        painter.drawEllipse(QPointF(cx, cy), 3, 3)

        painter.setFont(QFont("Consolas", 10, QFont.Bold))
        painter.setPen(COLOR_ACCENT_CYAN)

        painter.drawText(24, h - 60, f"ALT: {m.z:5.1f} m")
        painter.drawText(24, h - 42, f"SPD: {m.speed():5.1f} m/s")
        painter.drawText(24, h - 24, f"BAT: {m.battery:3.0f} %")

        painter.drawText(w - 180, h - 60, f"HDG: {m.heading_deg():03.0f}°")
        painter.drawText(w - 180, h - 42, f"PIT: {m.pitch_deg:+4.0f}°")
        painter.drawText(w - 180, h - 24, f"ROL: {m.roll_deg:+4.0f}°")

        painter.drawText(int(cx - 50), 32, "FPV CAM 1080P")

    # ------------------------------------------------------------------ 2D Mini-Map / Radar Overlay
    def _draw_radar(self, painter, w, h):
        rw, rh = 130, 130
        rx = w - rw - 14
        ry = 14
        rcx, rcy = rx + rw / 2.0, ry + rh / 2.0
        r_radius = 54.0

        self._panel(painter, QRectF(rx, ry, rw, rh), 175, 10)
        painter.setPen(QPen(QColor(53, 213, 240, 100), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QPointF(rcx, rcy), r_radius, r_radius)
        painter.drawEllipse(QPointF(rcx, rcy), r_radius * 0.5, r_radius * 0.5)
        painter.drawLine(int(rcx - r_radius), int(rcy), int(rcx + r_radius), int(rcy))
        painter.drawLine(int(rcx), int(rcy - r_radius), int(rcx), int(rcy + r_radius))

        m = self.model
        scale = r_radius / 35.0

        def to_radar(wx, wy):
            dx = (wx - m.x) * scale
            dy = (wy - m.y) * scale
            a = self.cam_az - math.pi / 2.0
            rx_p = dx * math.cos(a) - dy * math.sin(a)
            ry_p = dx * math.sin(a) + dy * math.cos(a)
            return QPointF(rcx + rx_p, rcy - ry_p)

        # Plot HOME
        p_home = to_radar(0.0, 0.0)
        if math.hypot(p_home.x() - rcx, p_home.y() - rcy) <= r_radius:
            painter.setPen(Qt.NoPen)
            painter.setBrush(COLOR_ACCENT_ORANGE)
            painter.drawEllipse(p_home, 3.5, 3.5)

        # Plot Elevated Helipads
        for pad in self.elevated_helipads:
            p_pad = to_radar(pad["pos"][0], pad["pos"][1])
            if math.hypot(p_pad.x() - rcx, p_pad.y() - rcy) <= r_radius:
                painter.setBrush(COLOR_ACCENT_ORANGE)
                painter.drawEllipse(p_pad, 3.0, 3.0)

        # Plot Racing Gates
        for gate in self.racing_gates:
            p_gate = to_radar(gate["pos"][0], gate["pos"][1])
            if math.hypot(p_gate.x() - rcx, p_gate.y() - rcy) <= r_radius:
                painter.setBrush(QColor(255, 40, 180))
                painter.drawEllipse(p_gate, 3.0, 3.0)

        # Drone Marker Arrow
        painter.save()
        painter.translate(rcx, rcy)
        radar_rot = math.degrees(m.yaw + self.cam_az - math.pi / 2.0)
        painter.rotate(radar_rot)
        painter.setPen(QPen(COLOR_ACCENT_CYAN, 1.5))
        painter.setBrush(COLOR_ACCENT_CYAN)
        painter.drawPolygon(QPolygonF([
            QPointF(0, -6), QPointF(-4, 4), QPointF(4, 4)
        ]))
        painter.restore()

        painter.setFont(QFont("Consolas", 8, QFont.Bold))
        painter.setPen(QColor(COLOR_ACCENT_CYAN.red(), COLOR_ACCENT_CYAN.green(), COLOR_ACCENT_CYAN.blue(), 200))
        painter.drawText(QRectF(rx, ry + rh - 18, rw, 14), Qt.AlignCenter, "RADAR 35m [M]")

    # ------------------------------------------------------------------ Glassmorphism HUD & Labels
    def _panel(self, painter, rect, alpha=150, radius=8):
        painter.setPen(QPen(QColor(53, 213, 240, 50), 1))
        painter.setBrush(QColor(14, 18, 26, alpha))
        painter.drawRoundedRect(rect, radius, radius)

    def _draw_labels(self, painter):
        m = self.model
        painter.setFont(QFont("Consolas", 9))
        text = f"X:{m.x:+5.1f}  Y:{m.y:+5.1f}  Z:{m.z:5.1f}m"
        fm = painter.fontMetrics()
        tw = fm.horizontalAdvance(text)
        self._panel(painter, QRectF(8, self.height() - 30, tw + 16, 22), 160, 6)
        painter.setPen(QColor(240, 245, 255, 240))
        painter.drawText(QRectF(16, self.height() - 28, tw, 18), Qt.AlignLeft | Qt.AlignVCenter, text)

    def _draw_hud(self, painter, w, h):
        m = self.model

        # Camera & Theme Badge (Top Left)
        badge_text = f"{self.camera_mode} [C] • {self.env_theme} [T]"
        painter.setFont(QFont("Consolas", 9, QFont.Bold))
        fm = painter.fontMetrics()
        bw = fm.horizontalAdvance(badge_text) + 16
        self._panel(painter, QRectF(66, 10, bw, 24), 160, 6)
        painter.setPen(COLOR_ACCENT_CYAN)
        painter.drawText(QRectF(74, 12, bw - 16, 20), Qt.AlignLeft | Qt.AlignVCenter, badge_text)

        self._draw_status(painter, w, h)
        self._draw_heading(painter, w, h)
        self._draw_tape(painter, m.z, "ALT m", COLOR_ACCENT_CYAN, w - 28, y0=60, max_val=30)
        self._draw_tape(painter, m.speed(), "SPD m/s", COLOR_ACCENT_ORANGE, w - 28, y0=155, max_val=20)
        self._draw_attitude(painter, w - 176, h - 90, box=66)
        self._draw_compass(painter, w - 90, h - 90)
        self._draw_throttle(painter, m.throttle_pct, w, h)

        if m.connected and not m.has_frames:
            self._draw_warning(painter, w, h)
        else:
            self._draw_hint(painter, w, h)

    def _draw_attitude(self, painter, cx, cy, box=66.0):
        roll = self.model.roll_deg
        pitch = self.model.pitch_deg
        clip = QRectF(cx - box / 2, cy - box / 2, box, box)

        painter.save()
        painter.setClipRect(clip)
        painter.translate(cx, cy)
        painter.rotate(roll)

        painter.setPen(QPen(QColor(255, 255, 255, 220), 1))
        painter.setBrush(QColor(70, 130, 200, 180))
        painter.drawRect(-box, -box, box * 2, box)
        painter.setPen(QPen(QColor(80, 80, 90, 220), 1))
        painter.setBrush(QColor(55, 95, 60, 180))
        painter.drawRect(-box, 0, box * 2, box)

        step = 8.0
        shift = pitch * (box / 2) / 15.0
        for i in range(-3, 4):
            y = i * step + shift
            if i == 0:
                continue
            width = box * 0.35 if abs(i) == 1 else (box * 0.22 if abs(i) == 2 else box * 0.14)
            x = -width / 2
            painter.setPen(QPen(QColor(255, 255, 255, 230), 2))
            painter.drawLine(x, y, x + width, y)

        painter.restore()

        painter.setPen(QPen(QColor(255, 65, 65, 240), 2))
        painter.drawLine(cx - 16, cy, cx + 16, cy)
        painter.drawLine(cx, cy - 6, cx, cy + 6)

        painter.setPen(QPen(COLOR_ACCENT_CYAN, 1.5))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(clip, 6, 6)

        label = f"R {self.model.roll_deg:+3.0f}°  P {self.model.pitch_deg:+3.0f}°"
        painter.setFont(QFont("Consolas", 8))
        fm = painter.fontMetrics()
        lw = fm.horizontalAdvance("R +00°  P +00°")
        rx = cx - lw / 2.0 - 6
        ry = cy - box / 2.0 - 22
        self._panel(painter, QRectF(rx, ry, lw + 12, 18), 140, 4)
        painter.setPen(QColor(255, 255, 255, 235))
        painter.drawText(QRectF(rx, ry, lw + 12, 18), Qt.AlignCenter, label)

    def _draw_compass(self, painter, cx, cy, r=36.0):
        heading = self.model.heading_deg()
        rad = math.radians

        self._panel(painter, QRectF(cx - r, cy - r, 2 * r, 2 * r), 150, r)

        for deg in range(0, 360, 15):
            a = rad(deg - heading)
            outer = r - 3
            inner = r - 9 if deg % 45 == 0 else r - 6
            painter.setPen(QPen(QColor(255, 255, 255, 190), 2 if deg % 45 == 0 else 1))
            painter.drawLine(
                QPointF(cx + math.sin(a) * outer, cy - math.cos(a) * outer),
                QPointF(cx + math.sin(a) * inner, cy - math.cos(a) * inner),
            )

        letters = {0: "N", 90: "E", 180: "S", 270: "W"}
        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
        for deg, ch in letters.items():
            a = rad(deg - heading)
            px = cx + math.sin(a) * (r - 15)
            py = cy - math.cos(a) * (r - 15)
            painter.setPen(COLOR_ACCENT_CYAN if deg == 0 else QColor(255, 255, 255, 225))
            painter.drawText(QRectF(px - 8, py - 7, 16, 14), Qt.AlignCenter, ch)

        text = f"{heading:03.0f}°"
        painter.setFont(QFont("Consolas", 8))
        self._panel(painter, QRectF(cx - 18, cy + r - 2, 36, 16), 140, 4)
        painter.setPen(QColor(255, 255, 255, 235))
        painter.drawText(QRectF(cx - 18, cy + r - 2, 36, 16), Qt.AlignCenter, text)

    def _draw_heading(self, painter, w, h):
        heading = self.model.heading_deg()
        painter.setFont(QFont("Consolas", 10, QFont.Bold))
        text = f"H: {heading:03.0f}°"
        fm = painter.fontMetrics()
        tw = fm.horizontalAdvance(text)
        x0 = w / 2.0 - (tw + 16) / 2.0
        self._panel(painter, QRectF(x0, 8, tw + 16, 24), 150, 6)
        painter.setPen(QColor(255, 255, 255, 235))
        painter.drawText(QRectF(x0 + 8, 10, tw, 20), Qt.AlignLeft | Qt.AlignVCenter, text)

    def _draw_tape(self, painter, value, label, color, x, y0=60, max_val=30.0):
        bar_h = 75
        self._panel(painter, QRectF(x - 2, y0 - 2, 26, bar_h + 4), 160, 5)
        frac = max(0.0, min(value / max_val, 1.0))
        fill_h = int(bar_h * frac)
        if fill_h > 0:
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            painter.drawRoundedRect(QRectF(x, y0 + bar_h - fill_h, 22, fill_h), 3, 3)

        painter.setFont(QFont("Consolas", 8))
        fm = painter.fontMetrics()
        text_v = f"{value:.1f}"
        wl = max(fm.horizontalAdvance(label), fm.horizontalAdvance(text_v)) + 10
        self._panel(painter, QRectF(x - wl - 4, y0 - 34, wl, 34), 140, 5)
        painter.setPen(QColor(255, 255, 255, 235))
        painter.drawText(QRectF(x - wl + 2, y0 - 30, wl - 6, 14), Qt.AlignLeft, label)
        painter.drawText(QRectF(x - wl + 2, y0 - 18, wl - 6, 14), Qt.AlignLeft, text_v)

    def _draw_throttle(self, painter, throttle, w, h):
        cx = w / 2.0
        y = h - 32
        self._panel(painter, QRectF(cx - 52, y - 2, 104, 18), 150, 5)
        frac = max(0.0, min(throttle / 100.0, 1.0))
        if frac > 0.02:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(16, 185, 129))
            painter.drawRoundedRect(QRectF(cx - 50, y, max(6, int(100 * frac)), 14), 3, 3)

        painter.setFont(QFont("Consolas", 9))
        text = f"THR {throttle:3.0f}%"
        fm = painter.fontMetrics()
        tw = fm.horizontalAdvance(text)
        self._panel(painter, QRectF(cx - tw / 2.0 - 8, y - 24, tw + 16, 20), 140, 5)
        painter.setPen(QColor(255, 255, 255, 235))
        painter.drawText(QRectF(cx - tw / 2.0, y - 22, tw, 16), Qt.AlignCenter, text)

    def _draw_status(self, painter, w, h):
        m = self.model
        x0, y0 = 10, 10
        pw, ph = 48, 82

        self._panel(painter, QRectF(x0, y0, pw, ph), 160, 10)

        c = QColor(16, 185, 129) if m.armed else QColor(239, 68, 68)
        painter.setPen(QPen(QColor(20, 22, 28), 2))
        painter.setBrush(c)
        painter.drawEllipse(QPointF(x0 + 24, y0 + 22), 7, 7)

        cy = y0 + 48
        bar_col = QColor(16, 185, 129) if m.connected else QColor(100, 116, 139)
        for i, bh in enumerate((5, 9, 13)):
            bx = x0 + 16 + i * 6
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(51, 65, 85))
            painter.drawRect(QRectF(bx, cy + 2 - 3, 3, 3))
            painter.setBrush(bar_col)
            painter.drawRect(QRectF(bx, cy + 2 - bh, 3, bh))

        cy = y0 + 74
        bcol = QColor(16, 185, 129)
        if m.battery < 30:
            bcol = COLOR_ACCENT_ORANGE
        if m.battery < 10:
            bcol = QColor(239, 68, 68)
        bx = x0 + 13
        bw, bh = 22, 11
        by = cy - bh / 2.0
        painter.setBrush(QColor(30, 41, 59))
        painter.setPen(QPen(QColor(148, 163, 184), 1))
        painter.drawRoundedRect(QRectF(bx, by, bw, bh), 2, 2)
        fill = int(bw * m.battery / 100.0)
        if fill > 1:
            painter.setPen(Qt.NoPen)
            painter.setBrush(bcol)
            painter.drawRect(QRectF(bx + 1.5, by + 1.5, fill - 3, bh - 3))
        painter.setPen(QPen(QColor(148, 163, 184), 1))
        painter.drawLine(QPointF(bx + bw + 1, by + 3), QPointF(bx + bw + 1, by + bh - 3))

    def _draw_warning(self, painter, w, h):
        painter.setFont(QFont("Consolas", 11))
        fm = painter.fontMetrics()
        t1 = "TERHUBUNG TAPI TIDAK ADA DATA CH"
        t2 = "Cek baud 115200 & firmware JoystickTest"
        ww = max(fm.horizontalAdvance(t1), fm.horizontalAdvance(t2)) + 26
        x0 = w / 2.0 - ww / 2.0
        self._panel(painter, QRectF(x0, 120, ww, 44), 170, 8)
        painter.setPen(QColor(239, 68, 68))
        painter.drawText(QRectF(x0, 126, ww, 16), Qt.AlignCenter, t1)
        painter.setPen(COLOR_ACCENT_ORANGE)
        painter.drawText(QRectF(x0, 142, ww, 16), Qt.AlignCenter, t2)

    def _draw_hint(self, painter, w, h):
        m = self.model
        hint = None
        if not m.armed:
            hint = "DISARMED - tekan SPASI atau tombol ARM"
        elif m.z < 0.05:
            hint = "Dorong THROTTLE (+) ke atas untuk terbang"
        elif abs(m.ch1) < 5 and abs(m.ch3) < 5 and abs(m.ch4) < 5:
            hint = "C: Kamera | T: Tema (Day/Sunset/Night) | L: Spotlight | M: Radar | H: HUD"
        if not hint:
            return
        painter.setFont(QFont("Consolas", 9))
        fm = painter.fontMetrics()
        tw = fm.horizontalAdvance(hint)
        x0 = w / 2.0 - (tw + 16) / 2.0
        self._panel(painter, QRectF(x0, h - 96, tw + 16, 24), 150, 6)
        painter.setPen(QColor(255, 255, 255, 235))
        painter.drawText(QRectF(x0 + 8, h - 94, tw, 20), Qt.AlignLeft | Qt.AlignVCenter, hint)

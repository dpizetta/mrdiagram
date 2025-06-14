import numpy

# ============================================================================
# SHAPE CLASSES
# ============================================================================

class Shape():
    def __init__(self, num_points: int = 100):
        self.num_points = num_points
        self.shape = None

    def generate(self):
        """Generate the array with shape amplitudes based on the shape function.
        Returns:
            numpy.ndarray: Array of shape amplitudes normalized to [-1, 1].
        """
        return self.shape

    def normalize(self, data):
        """Normalize data to [-1, 1] range"""
        if numpy.max(data) == numpy.min(data):
            return numpy.zeros_like(data)
        return 2 * (data - numpy.min(data)) / (numpy.max(data) - numpy.min(data)) - 1

# RF PULSE SHAPES
class RectangularShape(Shape):
    def __init__(self, num_points: int = 100):
        super().__init__(num_points)
        self.generate()

    def generate(self):
        t = numpy.linspace(-1, 1, self.num_points)
        raw_shape = numpy.where(numpy.abs(t) <= 0.8, 1.0, 0.0)
        self.shape = self.normalize(raw_shape)
        return self.shape

class SincShape(Shape):
    def __init__(self, num_points: int = 100, bandwidth: float = 4):
        super().__init__(num_points)
        self.bandwidth = bandwidth
        self.generate()

    def generate(self):
        t = numpy.linspace(-2, 2, self.num_points)
        x = self.bandwidth * numpy.pi * t
        raw_shape = numpy.where(numpy.abs(x) < 1e-10, 1.0, numpy.sin(x) / x)
        self.shape = self.normalize(raw_shape)
        return self.shape

class GaussianShape(Shape):
    def __init__(self, num_points: int = 100, sigma: float = 0.5):
        super().__init__(num_points)
        self.sigma = sigma
        self.generate()

    def generate(self):
        t = numpy.linspace(-2, 2, self.num_points)
        raw_shape = numpy.exp(-0.5 * (t / self.sigma) ** 2)
        self.shape = self.normalize(raw_shape)
        return self.shape

class HammingSincShape(Shape):
    def __init__(self, num_points: int = 100, bandwidth: float = 3):
        super().__init__(num_points)
        self.bandwidth = bandwidth
        self.generate()

    def generate(self):
        t = numpy.linspace(-2, 2, self.num_points)
        x = self.bandwidth * numpy.pi * t
        sinc_vals = numpy.where(numpy.abs(x) < 1e-10, 1.0, numpy.sin(x) / x)
        hamming_window = 0.54 + 0.46 * numpy.cos(numpy.pi * t / 2)
        raw_shape = sinc_vals * hamming_window
        self.shape = self.normalize(raw_shape)
        return self.shape

class ChessShape(Shape):
    def __init__(self, num_points: int = 100, sigma: float = 0.6, omega: float = 8):
        super().__init__(num_points)
        self.sigma = sigma
        self.omega = omega
        self.generate()

    def generate(self):
        t = numpy.linspace(-2, 2, self.num_points)
        envelope = numpy.exp(-0.5 * (t / self.sigma) ** 2)
        modulation = numpy.cos(self.omega * t)
        raw_shape = envelope * numpy.abs(modulation)
        self.shape = self.normalize(raw_shape)
        return self.shape

class AdiabaticShape(Shape):
    def __init__(self, num_points: int = 100, beta: float = 5):
        super().__init__(num_points)
        self.beta = beta
        self.generate()

    def generate(self):
        t = numpy.linspace(-2, 2, self.num_points)
        raw_shape = 1 / numpy.cosh(self.beta * t)
        self.shape = self.normalize(raw_shape)
        return self.shape

class SLRShape(Shape):
    def __init__(self, num_points: int = 100, multiplier: float = 0.1):
        super().__init__(num_points)
        self.generate()

    def generate(self):
        t = numpy.linspace(-1, 1, self.num_points)
        x = numpy.abs(t)
        raw_shape = numpy.where(x <= 1,
                               numpy.sqrt(1 - x**2) * (1 + 0.5 * numpy.sin(5 * numpy.pi * x)),
                               0.0)
        self.shape = self.normalize(raw_shape)
        return self.shape

class VerseShape(Shape):
    def __init__(self, num_points: int = 100):
        super().__init__(num_points)
        self.generate()

    def generate(self):
        t = numpy.linspace(-2, 2, self.num_points)
        phase = numpy.linspace(0, 1, self.num_points)
        rate_modulation = 1 + 0.8 * numpy.sin(6 * numpy.pi * phase)
        envelope = numpy.exp(-2 * t**2) * rate_modulation
        raw_shape = numpy.abs(envelope)
        self.shape = self.normalize(raw_shape)
        return self.shape

class FermiShape(Shape):
    def __init__(self, num_points: int = 100, transition: float = 0.2, plateau_width: float = 0.8):
        super().__init__(num_points)
        self.transition = transition
        self.plateau_width = plateau_width
        self.generate()

    def generate(self):
        t = numpy.linspace(-2, 2, self.num_points)
        abs_t = numpy.abs(t)
        raw_shape = 1 / (1 + numpy.exp((abs_t - self.plateau_width) / self.transition))
        self.shape = self.normalize(raw_shape)
        return self.shape

class SPSPShape(Shape):
    def __init__(self, num_points: int = 100, spatial_freq: float = 4, spectral_freq: float = 12):
        super().__init__(num_points)
        self.spatial_freq = spatial_freq
        self.spectral_freq = spectral_freq
        self.generate()

    def generate(self):
        t = numpy.linspace(-2, 2, self.num_points)
        envelope = numpy.exp(-t**2)
        spatial = numpy.cos(self.spatial_freq * numpy.pi * t)
        spectral = numpy.cos(self.spectral_freq * numpy.pi * t)
        raw_shape = envelope * numpy.abs(spatial * spectral)
        self.shape = self.normalize(raw_shape)
        return self.shape

class CompositeShape(Shape):
    def __init__(self, num_points: int = 100):
        super().__init__(num_points)
        self.generate()

    def generate(self):
        t = numpy.linspace(-2, 2, self.num_points)
        raw_shape = numpy.zeros_like(t)

        mask1 = numpy.abs(t + 1.2) <= 0.3
        raw_shape[mask1] = 0.5
        mask2 = numpy.abs(t) <= 0.4
        raw_shape[mask2] = 1.0
        mask3 = numpy.abs(t - 1.2) <= 0.3
        raw_shape[mask3] = 0.5

        self.shape = self.normalize(raw_shape)
        return self.shape

class DanteShape(Shape):
    def __init__(self, num_points: int = 100, num_pulses: int = 12, pulse_width: float = 0.08, spacing: float = 0.32):
        super().__init__(num_points)
        self.num_pulses = num_pulses
        self.pulse_width = pulse_width
        self.spacing = spacing
        self.generate()

    def generate(self):
        t = numpy.linspace(-2, 2, self.num_points)
        raw_shape = numpy.zeros_like(t)

        for p in range(self.num_pulses):
            pulse_center = -1.8 + p * self.spacing
            mask = numpy.abs(t - pulse_center) <= self.pulse_width
            raw_shape[mask] = 0.25 * (1 + 0.5 * numpy.sin(p))

        self.shape = self.normalize(raw_shape)
        return self.shape

class HyperbolicSecantShape(Shape):
    def __init__(self, num_points: int = 100, beta: float = 5, mu: float = 4.9):
        super().__init__(num_points)
        self.beta = beta
        self.mu = mu
        self.generate()

    def generate(self):
        t = numpy.linspace(-1, 1, self.num_points)
        raw_shape = (1 / numpy.cosh(self.beta * t)) * numpy.tanh(self.mu * t)
        self.shape = self.normalize(raw_shape)
        return self.shape

class BIRShape(Shape):
    def __init__(self, num_points: int = 100, n: int = 4):
        super().__init__(num_points)
        self.n = n
        self.generate()

    def generate(self):
        t = numpy.linspace(-1, 1, self.num_points)
        raw_shape = numpy.tanh(self.n * t) / numpy.cosh(self.n * t)
        self.shape = self.normalize(raw_shape)
        return self.shape

# SIGNAL SHAPES (FID and Echo)
class FIDShape(Shape):
    def __init__(self, num_points: int = 100, t2_star: float = 50.0, frequency: float = 100.0, phase: float = 0.0):
        super().__init__(num_points)
        self.t2_star = t2_star  # in ms
        self.frequency = frequency  # in Hz
        self.omega = 2 * numpy.pi * frequency  # rad/s
        self.phase = phase  # in radians
        self.generate()

    def generate(self):
        t_max = 5 * self.t2_star
        t = numpy.linspace(0, t_max, self.num_points)
        t_seconds = t / 1000.0
        decay = numpy.exp(-t / self.t2_star)
        oscillation = numpy.exp(-1j * (self.omega * t_seconds - self.phase))
        raw_shape = decay * oscillation
        self.shape = numpy.real(self.normalize(raw_shape))
        return self.shape

class EchoShape(Shape):
    def __init__(self, num_points: int = 100, t2: float = 80.0, t2_star: float = 50.0,
                 echo_time: float = 50.0, frequency: float = 100.0, phase: float = 0.0):
        super().__init__(num_points)
        self.t2 = t2  # in ms
        self.t2_star = t2_star  # in ms
        self.echo_time = echo_time  # in ms (TE)
        self.frequency = frequency  # in Hz
        self.omega = 2 * numpy.pi * frequency  # rad/s
        self.phase = phase  # in radians
        self.generate()

    def generate(self):
        # Time array centered around echo time
        t_max = 2 * self.echo_time  # Go to 2*TE for symmetry
        t = numpy.linspace(0, t_max, self.num_points)
        t_seconds = t / 1000.0
        te_seconds = self.echo_time / 1000.0
        t2_decay = numpy.exp(-self.echo_time / self.t2)
        t2_star_envelope = numpy.exp(-numpy.abs(t - self.echo_time) / self.t2_star)
        oscillation = numpy.cos(self.omega * (t_seconds - te_seconds) + self.phase)
        raw_shape = t2_decay * t2_star_envelope * oscillation
        self.shape = numpy.real(self.normalize(raw_shape))
        return self.shape

class STIRShape(Shape):
    def __init__(self, num_points: int = 100, t1: float = 1000, ti: float = 200):
        super().__init__(num_points)
        self.t1 = t1
        self.ti = ti
        self.generate()

    def generate(self):
        t = numpy.linspace(0, 2000, self.num_points)
        inversion_recovery = 1 - 2 * numpy.exp(-self.ti / self.t1)
        raw_shape = inversion_recovery * numpy.exp(-t / self.t1)
        self.shape = self.normalize(raw_shape)
        return self.shape

# TRIGGER SHAPES
class TriggerShape(Shape):
    def __init__(self, num_points: int = 100):
        super().__init__(num_points)
        self.generate()

    def generate(self):
        raw_shape = numpy.zeros(self.num_points)
        center = self.num_points // 2
        raw_shape[center-5:center+5] = 1.0  # 10-point wide trigger
        self.shape = self.normalize(raw_shape)
        return self.shape

# FLAG SHAPES
class FlagShape(Shape):
    def __init__(self, num_points: int = 100):
        super().__init__(num_points)
        self.generate()

    def generate(self):
        raw_shape = numpy.zeros(self.num_points)
        center = self.num_points // 2
        raw_shape[center] = 1.0  # Single point delta
        self.shape = self.normalize(raw_shape)
        return self.shape

# GRADIENT SHAPES
class TrapezoidShape(Shape):
    def __init__(self, num_points: int = 100, rise_fraction: float = 0.2, plateau_fraction: float = 0.6, fall_fraction: float = 0.2):
        super().__init__(num_points)
        self.rise_fraction = rise_fraction
        self.plateau_fraction = plateau_fraction
        self.fall_fraction = fall_fraction
        self.generate()

    def generate(self):
        raw_shape = numpy.zeros(self.num_points)

        rise_points = int(self.rise_fraction * self.num_points)
        plateau_points = int(self.plateau_fraction * self.num_points)
        fall_points = int(self.fall_fraction * self.num_points)

        # Ensure total points don't exceed num_points
        total_defined = rise_points + plateau_points + fall_points
        if total_defined > self.num_points:
            # Proportionally reduce
            scale = self.num_points / total_defined
            rise_points = int(rise_points * scale)
            plateau_points = int(plateau_points * scale)
            fall_points = self.num_points - rise_points - plateau_points

        # Rise
        if rise_points > 0:
            raw_shape[:rise_points] = numpy.linspace(0, 1, rise_points)

        # Plateau
        if plateau_points > 0:
            raw_shape[rise_points:rise_points+plateau_points] = 1.0

        # Fall
        if fall_points > 0:
            start_fall = rise_points + plateau_points
            raw_shape[start_fall:start_fall+fall_points] = numpy.linspace(1, 0, fall_points)

        self.shape = self.normalize(raw_shape)
        return self.shape

class RampUpShape(Shape):
    def __init__(self, num_points: int = 100):
        super().__init__(num_points)
        self.generate()

    def generate(self):
        raw_shape = numpy.linspace(0, 1, self.num_points)
        self.shape = self.normalize(raw_shape)
        return self.shape

class RampDownShape(Shape):
    def __init__(self, num_points: int = 100):
        super().__init__(num_points)
        self.generate()

    def generate(self):
        raw_shape = numpy.linspace(1, 0, self.num_points)
        self.shape = self.normalize(raw_shape)
        return self.shape

class RadialShape(Shape):
    def __init__(self, num_points: int = 100, phase: float = 0, cycles: float = 1):
        super().__init__(num_points)
        self.phase = phase
        self.cycles = cycles
        self.generate()

    def generate(self):
        t = numpy.linspace(0, self.cycles * 2 * numpy.pi, self.num_points)
        raw_shape = numpy.cos(t + self.phase)
        self.shape = self.normalize(raw_shape)
        return self.shape

class SpiralShape(Shape):
    def __init__(self, num_points: int = 100, turns: float = 3, phase: float = 0):
        super().__init__(num_points)
        self.turns = turns
        self.phase = phase
        self.generate()

    def generate(self):
        t = numpy.linspace(0, self.turns * 2 * numpy.pi, self.num_points)
        radius = numpy.linspace(0, 1, self.num_points)
        raw_shape = radius * numpy.cos(t + self.phase)
        self.shape = self.normalize(raw_shape)
        return self.shape

class EPIShape(Shape):
    def __init__(self, num_points: int = 100, lines: int = 8):
        super().__init__(num_points)
        self.lines = lines
        self.generate()

    def generate(self):
        t = numpy.linspace(0, self.lines, self.num_points)
        raw_shape = numpy.sin(2 * numpy.pi * t) * (1 - numpy.abs(2 * (t % 1) - 1))
        self.shape = self.normalize(raw_shape)
        return self.shape

class BipolarShape(Shape):
    def __init__(self, num_points: int = 100):
        super().__init__(num_points)
        self.generate()

    def generate(self):
        half = self.num_points // 2
        raw_shape = numpy.zeros(self.num_points)
        raw_shape[:half] = 1.0
        raw_shape[half:] = -1.0
        # For bipolar, we want to keep the -1, +1 structure, so normalize differently
        self.shape = raw_shape  # Already in [-1, 1] range
        return self.shape

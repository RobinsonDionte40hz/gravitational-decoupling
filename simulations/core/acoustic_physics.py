"""
Acoustic Physics Module
Real infrasound wave physics for gravitational decoupling experiments
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple

# Constants
RHO_AIR = 1.225  # kg/m³ - air density at sea level
C_SOUND = 343  # m/s - speed of sound in air
P_REF = 20e-6  # Pa - reference pressure for dB SPL (20 micropascals)


@dataclass
class AcousticProperties:
    """Physical properties of infrasound wave"""
    frequency: float  # Hz
    sound_pressure_level: float  # dB SPL
    distance_from_source: float = 0.1  # meters (object distance from speaker)
    
    def pressure_pascals(self) -> float:
        """Convert dB SPL to pressure in Pascals"""
        return P_REF * 10**(self.sound_pressure_level / 20)
    
    def intensity(self) -> float:
        """Acoustic intensity in W/m²"""
        p = self.pressure_pascals()
        return p**2 / (RHO_AIR * C_SOUND)
    
    def power_at_distance(self, area: float = 0.01) -> float:
        """
        Acoustic power hitting object
        area: object cross-sectional area in m²
        """
        return self.intensity() * area
    
    def wavelength(self) -> float:
        """Wavelength of infrasound"""
        return C_SOUND / self.frequency
    
    def particle_velocity(self) -> float:
        """Peak particle velocity in air"""
        p = self.pressure_pascals()
        return p / (RHO_AIR * C_SOUND)
    
    def particle_displacement(self) -> float:
        """Peak displacement of air particles"""
        v = self.particle_velocity()
        omega = 2 * np.pi * self.frequency
        return v / omega


@dataclass
class MaterialVibration:
    """How material responds to infrasound"""
    mass: float  # kg
    elastic_modulus: float  # Pa (Young's modulus)
    damping_coefficient: float = 0.1  # 0-1
    cross_section_area: float = 0.01  # m²
    
    def natural_frequency(self, length: float = 0.1) -> float:
        """
        Approximate natural frequency of object
        Simplified for small objects
        """
        # f = (1/2π) * sqrt(k/m) where k = EA/L
        k = self.elastic_modulus * self.cross_section_area / length
        return (1 / (2 * np.pi)) * np.sqrt(k / self.mass)
    
    def displacement_amplitude(self, force: float, frequency: float) -> float:
        """
        Vibrational displacement from applied acoustic force
        Using damped harmonic oscillator model
        """
        omega = 2 * np.pi * frequency
        omega_n = 2 * np.pi * self.natural_frequency()
        
        # Frequency response
        denominator = np.sqrt((omega_n**2 - omega**2)**2 + (2 * self.damping_coefficient * omega_n * omega)**2)
        
        # Avoid division by zero
        if denominator < 1e-10:
            denominator = 1e-10
            
        amplitude = force / (self.mass * denominator)
        return amplitude
    
    def resonance_amplification(self, frequency: float) -> float:
        """
        How much resonance amplifies response at given frequency
        Returns amplification factor (1.0 = no amplification)
        """
        omega = 2 * np.pi * frequency
        omega_n = 2 * np.pi * self.natural_frequency()
        
        # Peak at resonance
        if abs(omega - omega_n) < 1.0:  # Near resonance
            return 1.0 / (2 * self.damping_coefficient)
        else:
            return 1.0


def acoustic_force_on_object(acoustic: AcousticProperties, material: MaterialVibration) -> float:
    """
    Calculate force exerted by infrasound on object
    Simple radiation pressure model
    """
    pressure = acoustic.pressure_pascals()
    area = material.cross_section_area
    return pressure * area


def vibrational_energy(material: MaterialVibration, amplitude: float, frequency: float) -> float:
    """
    Energy stored in vibrating object
    E = (1/2) * m * ω² * A²
    """
    omega = 2 * np.pi * frequency
    return 0.5 * material.mass * omega**2 * amplitude**2


def coupling_intensity_from_vibration(
    amplitude: float,
    frequency: float,
    material: MaterialVibration
) -> float:
    """
    Convert physical vibration to decoupling intensity parameter
    
    Theory: Higher amplitude vibration at specific frequencies
    creates stronger decoupling effect
    
    Returns: 0-1 intensity for decoupling equations
    """
    # Normalize amplitude by object size (displacement/size ratio)
    typical_size = (material.mass / 2700)**(1/3)  # Assume density ~2700 kg/m³
    normalized_amplitude = amplitude / typical_size
    
    # Resonance amplification
    resonance_factor = material.resonance_amplification(frequency)
    
    # Combined effect
    intensity = normalized_amplitude * resonance_factor
    
    # Clamp to 0-1 range
    intensity = np.clip(intensity, 0, 1)
    
    return intensity


def required_spl_for_intensity(
    target_intensity: float,
    frequency: float,
    material: MaterialVibration
) -> float:
    """
    Calculate required sound pressure level (dB) to achieve
    a target decoupling intensity
    
    Returns: dB SPL needed
    """
    # Work backwards from intensity to vibration to force to pressure
    
    # Typical size
    typical_size = (material.mass / 2700)**(1/3)
    
    # Target amplitude
    resonance = material.resonance_amplification(frequency)
    target_amplitude = (target_intensity / resonance) * typical_size
    
    # Force needed for this amplitude
    omega = 2 * np.pi * frequency
    omega_n = 2 * np.pi * material.natural_frequency()
    denominator = np.sqrt((omega_n**2 - omega**2)**2 + (2 * material.damping_coefficient * omega_n * omega)**2)
    
    if denominator < 1e-10:
        denominator = 1e-10
    
    force = target_amplitude * material.mass * denominator
    
    # Pressure needed
    pressure = force / material.cross_section_area
    
    # Convert to dB SPL
    if pressure < P_REF:
        pressure = P_REF
    
    spl = 20 * np.log10(pressure / P_REF)
    
    return spl


# Material presets
MATERIAL_PRESETS = {
    'granite': MaterialVibration(
        mass=0.1,
        elastic_modulus=50e9,  # 50 GPa
        damping_coefficient=0.05,
        cross_section_area=0.01
    ),
    'aluminum': MaterialVibration(
        mass=0.1,
        elastic_modulus=69e9,  # 69 GPa
        damping_coefficient=0.02,
        cross_section_area=0.01
    ),
    'water_container': MaterialVibration(
        mass=0.1,
        elastic_modulus=2.2e9,  # Water bulk modulus
        damping_coefficient=0.3,  # High damping
        cross_section_area=0.01
    ),
    'steel': MaterialVibration(
        mass=0.1,
        elastic_modulus=200e9,  # 200 GPa
        damping_coefficient=0.01,
        cross_section_area=0.01
    )
}


if __name__ == "__main__":
    print("="*70)
    print("ACOUSTIC PHYSICS MODULE")
    print("="*70)
    
    # Example: 100 dB SPL at 10 Hz
    acoustic = AcousticProperties(frequency=10.0, sound_pressure_level=100)
    
    print(f"\nInfrasound properties at {acoustic.frequency} Hz, {acoustic.sound_pressure_level} dB:")
    print(f"  Pressure: {acoustic.pressure_pascals():.2f} Pa")
    print(f"  Intensity: {acoustic.intensity():.6f} W/m²")
    print(f"  Wavelength: {acoustic.wavelength():.2f} m")
    print(f"  Particle velocity: {acoustic.particle_velocity():.4f} m/s")
    print(f"  Particle displacement: {acoustic.particle_displacement()*1000:.4f} mm")
    
    # Material response
    material = MATERIAL_PRESETS['aluminum']
    force = acoustic_force_on_object(acoustic, material)
    amplitude = material.displacement_amplitude(force, acoustic.frequency)
    intensity = coupling_intensity_from_vibration(amplitude, acoustic.frequency, material)
    
    print(f"\nAluminum object response:")
    print(f"  Natural frequency: {material.natural_frequency():.2f} Hz")
    print(f"  Force applied: {force:.6f} N")
    print(f"  Vibration amplitude: {amplitude*1e6:.4f} µm")
    print(f"  Decoupling intensity: {intensity:.4f}")
    
    # Required SPL for target intensity
    target = 0.5
    required_spl = required_spl_for_intensity(target, acoustic.frequency, material)
    print(f"\nTo achieve intensity {target:.2f}:")
    print(f"  Required SPL: {required_spl:.1f} dB")
    
    print("\n" + "="*70)

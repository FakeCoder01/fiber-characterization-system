import numpy as np
from scipy.fft import fft, fftfreq
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter

class SignalProcessor:
    @staticmethod
    def calculate_attenuation(power_readings, distances):
        def attenuation_model(x, alpha, p0):
            return p0 * np.exp(-alpha * x)
        
        popt, pcov = curve_fit(attenuation_model, distances, power_readings)
        return {
            'attenuation_coeff': popt[0] * 1e4,  # converts to dB/km
            'initial_power': popt[1],
            'r_squared': 1 - np.sum((power_readings - attenuation_model(distances, *popt))**2) / np.sum((power_readings - np.mean(power_readings))**2)
        }

    @staticmethod
    def analyze_dispersion(signal, sampling_rate):
        n = len(signal)
        yf = fft(signal - np.mean(signal))
        xf = fftfreq(n, 1 / sampling_rate)
        
        # calculate the phase dispersion
        phase = np.unwrap(np.angle(yf))
        group_delay = -np.diff(phase) / (2 * np.pi * np.diff(xf))
        
        return {
            'frequency_spectrum': (xf[:n//2], np.abs(yf[:n//2])**2),
            'group_delay': (xf[1:n//2], savgol_filter(group_delay[:n//2-1], 11, 3)),
            'pmd': np.std(group_delay)
        }

    @staticmethod
    def noise_analysis(signal, window_size=101):
        filtered = savgol_filter(signal, window_size, 3)
        noise = signal - filtered
        return {
            'snr': 20 * np.log10(np.max(signal)/np.std(noise)),
            'noise_floor': np.mean(np.abs(noise)),
            'filtered_signal': filtered
        }
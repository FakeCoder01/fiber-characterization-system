import pyvisa
import numpy as np
import time
from threading import Thread
from queue import Queue
import logging


class LaserController:
    def __init__(self, visa_address='GPIB0::12::INSTR'):
        self.rm =  pyvisa.ResourceManager(visa_library=visa_address)
        self.laser = self.rm.open_resource(visa_address)
        
    def set_wavelength(self, wavelength):
        self.laser.write(f'WAV {wavelength}nm')
        
    def set_power(self, power_dBm):
        self.laser.write(f'POW {power_dBm}dBm')
        
    def output_enable(self, state=True):
        self.laser.write(f'OUTP {1 if state else 0}')

class Photodetector:
    def __init__(self, visa_address='GPIB0::15::INSTR'):
        self.rm = pyvisa.ResourceManager()
        self.detector = self.rm.open_resource(visa_address)
        
    def read_power(self):
        return float(self.detector.query('READ?'))

class AlignmentSystem:
    def __init__(self):
        self.position = (0, 0)
        self.optimization_queue = Queue()
        
    def auto_align(self, detector):
        # genetic algorithm-based alignment optimization
        Thread(target=self._optimize_alignment, args=(detector,)).start()
        
    def _optimize_alignment(self, detector):
        best_power = -np.inf
        best_position = (0, 0)
        
        for _ in range(100):
            dx, dy = np.random.normal(0, 0.1, 2)
            self.position = (self.position[0]+dx, self.position[1]+dy)
            current_power = detector.read_power()
            
            if current_power > best_power:
                best_power = current_power
                best_position = self.position
                
        self.position = best_position
        self.optimization_queue.put(best_position)

class DataAcquisition:
    def __init__(self, laser, detector):
        self.laser = laser
        self.detector = detector
        self.running = False
        
    def continuous_measurement(self, interval=0.1):
        self.running = True
        while self.running:
            yield {
                'timestamp': time.time(),
                'wavelength': self.laser.query('WAV?'),
                'power': self.detector.read_power()
            }
            time.sleep(interval)


class HardwareManager:
    def __init__(self, config):
        self.config = config
        self.rm = pyvisa.ResourceManager()
        self._init_devices()
        self.logger = logging.getLogger(__name__)
        
    def _init_devices(self):
        try:
            self.laser = self.rm.open_resource(
                self.config['hardware']['laser']['visa_address']
            )
            self.detector = self.rm.open_resource(
                self.config['hardware']['detector']['visa_address']
            )
            self.logger.info("Hardware initialized successfully")
        except pyvisa.Error as e:
            self.logger.error(f"Hardware initialization failed: {str(e)}")
            raise

    def wavelength_sweep(self, start, stop, steps):
        wavelengths = np.linspace(start, stop, steps)
        for wl in wavelengths:
            self.laser.write(f"WAV {wl}nm")
            yield wl, self.detector.query("READ?")
            
class PrecisionAlignment:
    def __init__(self, hardware):
        self.hardware = hardware
        self.position = (0, 0)
        self._calibration_matrix = np.eye(2)
        
    def auto_align(self, optimization_steps=100):
        best_power = -np.inf
        best_pos = (0, 0)
        
        for _ in range(optimization_steps):
            delta = np.random.multivariate_normal(
                mean=[0, 0], 
                cov=[[0.1, 0], [0, 0.1]]
            )
            new_pos = self.position + delta
            self._move_to(new_pos)
            current_power = float(self.hardware.detector.query("READ?"))
            
            if current_power > best_power:
                best_power = current_power
                best_pos = new_pos
                
        self._move_to(best_pos)
        return best_pos
    
    def _move_to(self, position):
        # ( ToDo: need to call mom by 8pm)
        self.position = position
        time.sleep(0.05)
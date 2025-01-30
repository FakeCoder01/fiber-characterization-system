from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class MeasurementResult(Base):
    __tablename__ = 'measurements'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    fiber_type = Column(String(50))
    wavelength = Column(Float)
    power = Column(Float)
    mfd = Column(Float)
    attenuation = Column(Float)
    dispersion = Column(Float)
    refractive_index_core = Column(Float)
    refractive_index_clad = Column(Float)
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'fiber_type': self.fiber_type,
            'wavelength': self.wavelength,
            'power': self.power,
            'mfd': self.mfd,
            'attenuation': self.attenuation,
            'dispersion': self.dispersion,
            'refractive_index_core': self.refractive_index_core,
            'refractive_index_clad': self.refractive_index_clad
        }

def init_db(engine='sqlite:///measurements.db'):
    engine = create_engine(engine)
    Base.metadata.create_all(engine)
    return engine
from sqlalchemy import Column, Integer, String, DateTime,ForeignKey, Boolean, Text, column
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class Technician(Base):
    __tablename__ = "technicians"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    service_areas = relationship("ServiceArea", back_populates="technician")
    specialties = relationship("Specialty", back_populates="technician")
    availability_slots = relationship("AvailabilitySlot", back_populates="technician")
    appointments = relationship("Appointment", back_populates="technician")

class ServiceArea(Base):
    __tablename__ = "service_areas"

    id = Column(Integer, primary_key=True, index=True)
    technician_id = Column(Integer, ForeignKey("technicians.id"), nullable=False)
    zip_code = Column(String, nullable=False)

    technician = relationship("Technician", back_populates="service_areas")    

class Specialty(Base):
    __tablename__ = "specialties"

    id = Column(Integer, primary_key=True, index=True)
    technician_id = Column(Integer, ForeignKey("technicians.id"), nullable=False)
    appliance_type = Column(String, nullable=False)

    technician = relationship("Technician", back_populates="specialties")    

class AvailabilitySlot(Base):
    __tablename__ = "availability_slots"

    id = Column(Integer, primary_key=True, index=True)
    technician_id = Column(Integer, ForeignKey("technicians.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_booked = Column(Boolean, default=False)

    technician = relationship("Technician", back_populates="availability_slots") 

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    technician_id = Column(Integer, ForeignKey("technicians.id"), nullable=False)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    zip_code = Column(String, nullable=False)
    customer_email = Column(String, nullable=True)
    appliance_type = Column(String, nullable=False)
    symptom_summary = Column(String, nullable=False)
    availability_slot_id = Column(Integer, ForeignKey("availability_slots.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    technician = relationship("Technician", back_populates="appointments")   

class CallSession(Base):
    __tablename__ = "call_sessions"

    id = Column(Integer, primary_key=True, index=True)
    call_sid = Column(String, nullable=False, unique=True)
    customer_phone = Column(String, nullable=True)
    appliance_type = Column(String, nullable=True)
    symptoms = Column(Text, nullable=True)
    zip_code = Column(String, nullable=True)
    pending_slot_id = Column(Integer, nullable=True)
    stage = Column(String, nullable=True, default="collect_issue")  # e.g. initial, info_gathering, slot_selection, confirmation
    troubleshooting_steps = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
      
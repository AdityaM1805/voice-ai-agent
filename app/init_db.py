from datetime import datetime, timedelta

from app.database import engine, Base, SessionLocal
from app.models import Technician, ServiceArea, Specialty, AvailabilitySlot

#Creates all database tables based on SQLAlchemy models defined in app/models.py.
def create_tables():
    Base.metadata.create_all(bind=engine)

#inserts sample data into the database for testing and development purposes.
def seed_sample_data():
    db = SessionLocal()
    try:
        existing_technicians = db.query(Technician).first()
        if existing_technicians:
            print("Sample data already exists, skipping seeding.")
            return  
        
        technicians=[
            Technician(name="Carlos Ramirez", email="carlos@shs.com", phone="555-1001"),
            Technician(name="Priya Shah", email="priya@shs.com", phone="555-1002"),
            Technician(name="Michael Chen", email="michael@shs.com", phone="555-1003"),
            Technician(name="Amanda Brooks", email="amanda@shs.com", phone="555-1004"),
            Technician(name="David Wilson", email="david@shs.com", phone="555-1005"),
        ]
        db.add_all(technicians)
        db.commit()

        for technician in technicians:
            db.refresh(technician)

        service_areas = [
            ServiceArea(technician_id=technicians[0].id, zip_code="95112"),
            ServiceArea(technician_id=technicians[0].id, zip_code="95050"),
            ServiceArea(technician_id=technicians[1].id, zip_code="94086"),
            ServiceArea(technician_id=technicians[1].id, zip_code="95112"),
            ServiceArea(technician_id=technicians[2].id, zip_code="95129"),
            ServiceArea(technician_id=technicians[2].id, zip_code="95051"),
            ServiceArea(technician_id=technicians[3].id, zip_code="94040"),
            ServiceArea(technician_id=technicians[3].id, zip_code="94086"),
            ServiceArea(technician_id=technicians[4].id, zip_code="95112"),
            ServiceArea(technician_id=technicians[4].id, zip_code="95129"),
        ]

        specialties = [
            Specialty(technician_id=technicians[0].id, appliance_type="washer"),
            Specialty(technician_id=technicians[0].id, appliance_type="dryer"),
            Specialty(technician_id=technicians[1].id, appliance_type="refrigerator"),
            Specialty(technician_id=technicians[1].id, appliance_type="dishwasher"),
            Specialty(technician_id=technicians[2].id, appliance_type="oven"),
            Specialty(technician_id=technicians[2].id, appliance_type="stove"),
            Specialty(technician_id=technicians[3].id, appliance_type="hvac"),
            Specialty(technician_id=technicians[3].id, appliance_type="refrigerator"),
            Specialty(technician_id=technicians[4].id, appliance_type="washer"),
            Specialty(technician_id=technicians[4].id, appliance_type="dishwasher"),
        ]

        db.add_all(service_areas)
        db.add_all(specialties)

        now = datetime.utcnow()

        availability_slots = []

        for technician in technicians:
            for day_offset in range(1, 4):
                start_time = now + timedelta(days=day_offset, hours=9)
                end_time = start_time + timedelta(hours=2)

                availability_slots.append(
                    AvailabilitySlot(
                        technician_id=technician.id,
                        start_time=start_time,
                        end_time=end_time,
                        is_booked=False
                    )
                )

        db.add_all(availability_slots)
        db.commit()

        print("Database tables created and sample data inserted.")

    finally:
        db.close()


if __name__ == "__main__":
    create_tables()
    seed_sample_data()    
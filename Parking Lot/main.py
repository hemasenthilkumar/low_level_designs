"""
The parking lot should have multiple levels, each level with a certain number of parking spots.
The parking lot should support different types of vehicles, such as cars, motorcycles, and trucks.
Each parking spot should be able to accommodate a specific type of vehicle.
The system should assign a parking spot to a vehicle upon entry and release it when the vehicle exits.
The system should track the availability of parking spots and provide real-time information to customers.
The system should handle multiple entry and exit points and support concurrent access.
"""

import time
import uuid
import threading
from datetime import datetime
from collections import defaultdict
from enum import Enum
from abc import ABC


class aStatus(Enum):
    FREE = 0
    OCCUPIED = 1

class pStatus(Enum):
    UNPAID = 0
    PAID = 1

class VehicleTypes(Enum):
    BIKE = 1
    CAR = 2
    TRUCK = 3

class SpotTypes(Enum):
    SMALL = 1
    COMPACT = 2
    ACCESSIBLE = 3
    LARGE = 4


class Vehicle(ABC):

    def get_license(self):
        pass

class Car(Vehicle):

    def __init__(self, license: str, is_challenged_driver: bool = False):
        self.type = VehicleTypes.CAR
        self.__license = license
        self.is_challenged_driver = is_challenged_driver

    def get_license(self):
        return self.__license

class Truck(Vehicle):

    def __init__(self, license: str):
        self.type = VehicleTypes.TRUCK
        self.__license = license

    def get_license(self):
        return self.__license

class Bike(Vehicle):

    def __init__(self, license: str, is_challenged_driver: bool = False):
        self.type = VehicleTypes.BIKE
        self.__license = license
        self.is_challenged_driver = is_challenged_driver

    def get_license(self):
        return self.__license



class ParkingSpot(ABC):

    def canFitVehicle(self, vehicle: Vehicle):
        pass

    def get_status(self):
        pass

    def set_status(self, status: aStatus):
        pass

class Small(ParkingSpot):

    def __init__(self, id: int):
        self.id = id
        self.__status = aStatus.FREE
        self.allow_types = [VehicleTypes.BIKE]
        self.type = SpotTypes.SMALL

    def canFitVehicle(self, vehicle: Vehicle):
        if vehicle.type not in self.allow_types:
            return False
        return True

    def set_status(self, status: aStatus):
        self.__status = status

    def get_status(self):
        return self.__status


class Compact(ParkingSpot):

    def __init__(self, id: int):
        self.id = id
        self.__status = aStatus.FREE
        self.allow_types = [VehicleTypes.BIKE, VehicleTypes.CAR]
        self.type = SpotTypes.COMPACT

    def canFitVehicle(self, vehicle: Vehicle):
        if vehicle.type not in self.allow_types:
            return False
        return True

    def set_status(self, status: aStatus):
        self.__status = status

    def get_status(self):
        return self.__status

class Accessible(ParkingSpot):

    def __init__(self, id: int):
        self.id = id
        self.__status = aStatus.FREE
        self.allow_types =  [VehicleTypes.BIKE, VehicleTypes.CAR]
        self.type = SpotTypes.ACCESSIBLE

    def canFitVehicle(self, vehicle: Vehicle):
        if vehicle.type not in self.allow_types:
            return False
        return True

    def set_status(self, status: aStatus):
        self.__status = status

    def get_status(self):
        return self.__status

class Large(ParkingSpot):

    def __init__(self, id: int):
        self.id = id
        self.__status = aStatus.FREE
        self.allow_types =  [VehicleTypes.BIKE, VehicleTypes.CAR, VehicleTypes.TRUCK]
        self.type = SpotTypes.LARGE

    def canFitVehicle(self, vehicle: Vehicle):
        if vehicle.type not in self.allow_types:
            return False
        return True

    def set_status(self, status: aStatus):
        self.__status = status

    def get_status(self):
        return self.__status

class ParkingTicket:

    def __init__(self, vehicle: Vehicle, spot: ParkingSpot):
        self.id = str(uuid.uuid4())
        self.vehicle = vehicle
        self.spot = spot
        self.checkin = datetime.now()
        self.__status = pStatus.UNPAID

    def get_status(self):
        return self.__status

    def set_status(self, status):
        self.__status = status

    def __str__(self):
        return '*'*10 +\
        f"Ticket ID: {self.id}\n" +\
        f"Vehicle Type: {self.vehicle.type.name}\n" +\
        f"Vehicle License Number: {self.vehicle.get_license()}\n" +\
        f"Checked In at: {self.checkin.strftime('%d%m%y %H:%M:%S')}\n" +\
        f"Ticket Status: {self.__status}\n" + '*'*10 + "\n\n"


class ParkingFloors:

    def __init__(self, floors):
        self.data = {}
        for fl in floors:
            self.data[fl.level] = fl

    def scan(self, vehicle: Vehicle):
        # return : {floor_level: [spots]}
        result = defaultdict(list)
        for level, fobj in self.data.items():
            for spot in fobj.spots:
                if spot.get_status() == aStatus.FREE:
                    if vehicle.is_challenged_driver and spot.type == SpotTypes.ACCESSIBLE :
                        result[level].append(spot)
                    else:
                        if spot.canFitVehicle(vehicle):
                            result[level].append(spot)
        return result


class Floors:

    def __init__(self, level: int):
        self.level = level
        self.spots = set()

    def assign_spot(self, spot: ParkingSpot):
        self.spots.add(spot)

    def remove_spot(self, spot: ParkingSpot):
        self.spots.remove(spot)

    def get_type_count(self):
        # in a particular floor , how many spots are there, with types
        data = defaultdict(int)
        for sp in self.spots:
            data[sp.type] += 1
        return data

class Exit:

    def __init__(self, id: int):
        self.id = id

    def calculate_fee(self):
        type = self.ticket.vehicle.type
        base_fee = 1
        per_hour = 0
        if type == VehicleTypes.CAR:
            base_fee = 50.0
            per_hour = 30.0
        elif type == VehicleTypes.BIKE:
            base_fee = 30.0
            per_hour = 10.0
        elif type == VehicleTypes.TRUCK:
            base_fee = 100.0
            per_hour = 50.0
        num_hours = ((datetime.now() - self.ticket.checkin).total_seconds())/3600
        total = base_fee + (per_hour * num_hours)
        return total

    def make_and_verify_payment(self, parking_ticket: ParkingTicket,
                            strategy: str ='Cash', card_num: str = None, upi_id: str = None):
        self.ticket = parking_ticket
        p = PaymentFactory.get_payment_obj(strategy, card_num, upi_id)
        if p.pay(self.calculate_fee()):
            self.unallocate_spot()
            self.ticket.set_status(pStatus.PAID)
        else:
            print("Payment failed, please retry!")

    def unallocate_spot(self):
        spot = self.ticket.spot
        spot.set_status(aStatus.FREE)
        print(f"{spot.type} spot {spot.id} status set to FREE!")

class Entry:

    def __init__(self, id: str, parkingfloors: ParkingFloors):
        self.id = id
        self.pf = parkingfloors

    def search_spot(self, vehicle):
        data = self.pf.scan(vehicle)
        self.spot = None
        for _, spots in data.items():
            if len(spots) > 0:
                self.spot = spots[0]
                break
        if not self.spot:
            raise Exception("Parking Full!!")
        print(f"Spot Found: {self.spot.id} for vehicle type: {vehicle.type}")

    def allocate_spot(self):
        lock = threading.Lock()
        with lock:
            self.spot.set_status(aStatus.OCCUPIED)
            print(f"{self.spot.type} spot {self.spot.id} status set to OCCUPIED!")

    def issue_ticket(self, vehicle: Vehicle):
        self.search_spot(vehicle)
        self.allocate_spot()
        ticket = ParkingTicket(vehicle, self.spot)
        print("Ticket Issued!!")
        return ticket

class Payment(ABC):

    def pay(self, amount: float):
        pass

class Card(Payment):

    def __init__(self, num: str):
        self.card_num = num

    def pay(self, amount):
        print(f"Payment started for Rs.{amount} /- via Card")
        time.sleep(1)
        print("Payment completed!")
        return True


class UPI(Payment):

    def __init__(self, id: str):
        self.upi_id = id

    def pay(self, amount):
        print(f"Payment started for Rs.{amount} /- via UPI")
        time.sleep(1)
        print("Payment completed!")
        return True

class Cash(Payment):

    def __init__(self):
        pass

    def pay(self, amount):
        print(f"Payment started for Rs.{amount} /- via Cash")
        time.sleep(1)
        print("Payment completed!")
        return True

class PaymentFactory:

    @staticmethod
    def get_payment_obj(strategy: str = 'Cash', upi_id: str = None, card_num: str = None):
        if strategy.lower() == 'cash':
            pobj = Cash()
        elif strategy.lower() == 'card':
            pobj = Card(card_num)
        elif strategy.lower() == 'upi':
            pobj = UPI(upi_id)
        else:
            raise Exception("Unknown payment method!, we accept only cash | credit | upi")
        return pobj



if __name__ == "__main__":

    car1 = Car(license="ABCD123")
    car2 = Car(license="XYZ123")
    bike1 = Bike(license = "TN12345")
    truck1 = Truck(license = "KA12345")
    p1 = Small(1)
    p2 = Compact(1)
    p3 = Compact(2)
    f1 = Floors(0)
    f1.assign_spot(p1)
    f1.assign_spot(p2)
    f2 = Floors(1)
    f2.assign_spot(p3)
    pf = ParkingFloors([f1, f2])
    res = pf.scan(car1)
    print(res[0])
    print(f1.get_type_count())
    eg1 = Entry("E1", pf)
    t1 = eg1.issue_ticket(car1)
    time.sleep(1)
    print(t1)
    t2 = eg1.issue_ticket(car2)
    print(t2)
    eg2 = Entry("E2", pf)
    t3 = eg2.issue_ticket(bike1)
    print(t3)
    ex1 = Exit('EX1')
    ex1.make_and_verify_payment(t1)
    print(t1)

"""
Design an organizational hierarchy using the Composite Pattern.

Your system should support:
    Employee → basic worker (leaf)
    Manager → can have Employees or other Managers under them (composite)
"""
from abc import ABC, abstractmethod

class OrgChart(ABC):

    @abstractmethod
    def view_details():
        raise NotImplementedError("Concrete Classes must implement this!")

# leaf
class Employee(OrgChart):

    def __init__(self, name: str):
        self.name = name

    def view_details(self, indent: int=2):
        print(f"{' '* indent} 👤{self.name}")

# container
class Manager(OrgChart):

    def __init__(self, name: str):
        self.name = name
        self.team = []

    def add(self, member: OrgChart):
        self.team.append(member)

    def view_details(self, indent=0):
        print(f"{' '*indent} 👔{self.name}")
        for emp in self.team:
            emp.view_details(indent+2)

if __name__=="__main__":

    emp1 = Employee("hema")
    emp2 = Employee("vasanth")
    emp3 = Employee("bruce")
    emp1.view_details()
    mg = Manager("John")
    mg.add(emp1)
    mg.add(emp2)
    mg.add(emp3)
    mg.view_details()
    mg2 = Manager("Sarath")
    mg2.add(mg)
    mg2.view_details()

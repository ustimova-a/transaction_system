from turtle import speed


class Aircraft:
    def __init__(self, id, weight):
        self.__id = id
        self.weight = weight
        self.speed = 0

    def takeoff(self):
        print('run')
        for _ in range(10):
            self.speed += 1
            print(self.speed)
        print('takeoff')

    def landing(self):
        print('landing')
        print('breaking')
        for _ in range(10):
            self.speed -= 1
            print(self.speed)
        print('stopped')
    
class MilitaryAircraft(Aircraft):
    def __init__(self, rockets, *args):
        super().__init__(*args)
        self.rockets = rockets

    def takeoff(self):
        print('fueled')
        super().takeoff()

    def shoot(self):
        if self.rockets > 0:
            print('bang')
            self.rockets -= 1
        else:
            print("can't shoot")


# boeing = Aircraft(737, 5000)
# print(boeing.weight)
# boeing.takeoff()
# print('flight')
# boeing.landing()
mig = MilitaryAircraft(3, 29, 2000)
mig.takeoff()
mig.shoot()
mig.landing()
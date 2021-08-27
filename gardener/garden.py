import random
import time


class Garden:
    # Start simulation at 2021-01-01 00:00:00 GMT
    INITIAL_TIME_UNIX_SECONDS = 1612557000

    # Each step is 10 minutes (60 seconds * 10)
    STEP_INTERVAL_SECONDS = 600

    # 86400 seconds per day
    STEPS_PER_DAY = 86400 / STEP_INTERVAL_SECONDS

    def __init__(self, moisture, temperature):
        self.moisture = moisture
        self.temperature = temperature
        self.time_unix_seconds = Garden.INITIAL_TIME_UNIX_SECONDS

    def get_moisture(self):
        return self.moisture

    def get_temperature(self):
        return self.temperature

    def get_time_unix_seconds(self):
        return self.time_unix_seconds

    def water_half(self):
        if self.moisture >= 0.99:
            return

        self.moisture += 0.005 * ((100 - self.temperature) / 100)

    def water_full(self):
        if self.moisture >= 0.99:
            return

        self.moisture += 0.01 * ((100 - self.temperature) / 100)

    def update(self):
        if self.moisture > 0.01:
            self.moisture -= 0.01 * (self.temperature / 100)

        is_afternoon = (
            (self.time_unix_seconds / Garden.STEP_INTERVAL_SECONDS)
            % Garden.STEPS_PER_DAY
        ) > (Garden.STEPS_PER_DAY / 2)

        if is_afternoon and self.temperature < 99.3:
            self.temperature += 0.3 * random.random()
        elif not is_afternoon and self.temperature > 0.3:
            self.temperature -= 0.3 * random.random()

        self.time_unix_seconds += Garden.STEP_INTERVAL_SECONDS

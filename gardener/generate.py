import time
import random
import csv

from garden import Garden


def maintain_garden_moisture_content(garden):
    with open("data/garden_data.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["time", "temperature", "moisture"])

        while True:
            # Observe garden
            print(
                f"Time: {garden.get_time_unix_seconds()} Temperature: {round(garden.get_temperature(),3)} Moisture: {round(garden.get_moisture(),3)}"
            )

            # Post observation
            writer.writerow(
                [
                    garden.get_time_unix_seconds(),
                    round(garden.get_temperature(), 3),
                    round(garden.get_moisture(), 3),
                ]
            )

            # Get inference
            recommended_action = random.randint(0, 6)

            # Update gargen
            if recommended_action == 0:
                garden.water_full()
                print("Watering at full flow")
            elif recommended_action == 1:
                garden.water_half()
                print("Watering at half flow")
            else:
                pass

            garden.update()
            time.sleep(0.01)


if __name__ == "__main__":
    garden = Garden(0.25, 25)
    maintain_garden_moisture_content(garden)

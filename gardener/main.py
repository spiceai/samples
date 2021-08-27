import io
import time
import random
import csv
import requests

from garden import Garden

SPICE_AI_OBSERVATIONS_URL = "http://localhost:8000/api/v0.1/pods/gardener/observations"
SPICE_AI_INFERENCE_URL = "http://localhost:8000/api/v0.1/pods/gardener/inference"


def maintain_garden_moisture_content(garden):
    while True:
        # Observe garden
        print(
            f"Time: {time.time()} Temperature: {round(garden.get_temperature(),3)} Moisture: {round(garden.get_moisture(),3)}"
        )

        with open("data/garden_data.csv", "a", newline="") as file:
            writer = csv.writer(file)
            for _ in range(10):
                # Post observation
                writer.writerow(
                    [
                        garden.get_time_unix_seconds(),
                        round(garden.get_temperature(), 3),
                        round(garden.get_moisture(), 3),
                    ]
                )

                garden.update()

        recommended_action = None
        try:
            r = requests.get(SPICE_AI_INFERENCE_URL)
            print(r.content)
        except Exception:
            print(
                f"Failed get inference from Spice AI.  Is the runtime started ('spice run')?"
            )
            return

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

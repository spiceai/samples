from os import system
import time
import csv
import requests

from garden import Garden

GARDEN_DATA_CSV_PATH = "data/garden_data.csv"
SPICE_AI_INFERENCE_URL = "http://localhost:8000/api/v0.1/pods/gardener/inference"


def maintain_garden_moisture_content(garden):
    with open(GARDEN_DATA_CSV_PATH, "a", newline="") as file:
        writer = csv.writer(file)
        while True:
            # Simulate passage of time and add observations to the data set
            print(
                f"Time: {garden.get_time_unix_seconds()} Temperature: {round(garden.get_temperature(),3)} Moisture: {round(garden.get_moisture(),3)}"
            )

            for _ in range(6):
                garden.update()
                writer.writerow(
                    [
                        garden.get_time_unix_seconds(),
                        round(garden.get_temperature(), 3),
                        round(garden.get_moisture(), 3),
                    ]
                )
                file.flush()

            recommended_action = None

            try:
                # Get a recommendation from Spice AI
                response = requests.get(SPICE_AI_INFERENCE_URL)
                response_json = response.json()
                recommended_action = response_json["action"]
            except Exception:
                print(
                    f"Failed get inference from Spice AI.  Is the runtime started ('spice run')?"
                )
                return

            # Take action based on Spice AI's recommendation
            if recommended_action == "open_valve_full":
                garden.open_valve_full()
                print("Watering at full flow")
            elif recommended_action == "open_valve_half":
                garden.open_valve_half()
                print("Watering at half flow")
            else:
                pass

            time.sleep(0.5)


def create_garden_from_csv(csv_path):
    # Seek to last entry in the csv and create a Garden from it
    with open(csv_path, "r", newline="") as file:
        reader = csv.DictReader(file)
        last_row = None
        try:
            for row in reader:
                last_row = row
        except csv.Error as e:
            system.exit(f"Could not read csv file {csv_path}: {e}")

        return Garden(
            int(last_row["time"]),
            float(last_row["moisture"]),
            float(last_row["temperature"]),
        )


if __name__ == "__main__":
    garden = create_garden_from_csv(GARDEN_DATA_CSV_PATH)
    maintain_garden_moisture_content(garden)

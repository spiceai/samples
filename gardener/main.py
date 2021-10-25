from os import system
import io
import time
import csv
import requests

from garden import Garden

GARDEN_DATA_CSV_PATH = "data/garden_data.csv"

SPICE_AI_OBSERVATIONS_URL = "http://localhost:8000/api/v0.1/pods/gardener/observations"
SPICE_AI_RECOMMENDATION_URL = (
    "http://localhost:8000/api/v0.1/pods/gardener/recommendation"
)


def maintain_garden_moisture_content(garden):
    while True:
        print(
            f"Time (s): {garden.get_time_unix_seconds()} Temperature (C): {round(garden.get_temperature(),3)} Moisture (%): {round(garden.get_moisture(),3)}"
        )

        # Post observations to Spice.ai
        #
        # Spice.ai's observations endpoint accepts CSV or JSON formatted data.
        # In this sample we will use CSV formatted data.
        # It expects headers of the form <dataspace from>.<dataspace name>.<dataspace field>
        # A "time" column must be included with all observations.
        #
        # For more information on the observations endpoint, visit https://docs.spiceai.org/reference/api/#observations
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(
            ["time", "sensors.garden.temperature", "sensors.garden.moisture"]
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

        try:
            requests.post(SPICE_AI_OBSERVATIONS_URL, data=output.getvalue())
        except Exception:
            print(
                f"Failed to post observations to Spice.ai.  Is the runtime started ('spice run')?"
            )
            return

        # Get a recommendation action from Spice.ai
        #
        # Spice.ai's recommendation endpoint returns a simple JSON response that includes a recommended "action" based
        # based on the most recent observations it has received
        #
        # For more information on the recommendations endpoint, visit https://docs.spiceai.org/reference/api/#recommendations
        recommended_action = None
        try:
            response = requests.get(SPICE_AI_RECOMMENDATION_URL)
            response_json = response.json()
            recommended_action = response_json["action"]
        except Exception:
            print(
                f"Failed to get a recommendation from Spice.ai.  Is the runtime started ('spice run')?"
            )
            return

        # Take action based on Spice.ai's recommendation
        if recommended_action == "open_valve_full":
            garden.open_valve_full()
            print("Watering at full flow", flush=True)
        elif recommended_action == "open_valve_half":
            garden.open_valve_half()
            print("Watering at half flow", flush=True)
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

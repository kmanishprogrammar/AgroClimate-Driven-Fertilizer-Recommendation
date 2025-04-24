import requests
from NPKEstimator import NPKEstimator

# Function to fetch weather data using wttr.in API
def get_weather(city, state):
    location = f"{city},{state}"
    url = f"https://wttr.in/{location}?format=j1"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch weather data.")
    data = response.json()

    # Extract today's weather details
    today_weather = data['current_condition'][0]
    temperature = float(today_weather['temp_C'])
    humidity = float(today_weather['humidity'])

    # Rainfall (precipitation in mm)
    rainfall = float(today_weather['precipMM'])

    return temperature, humidity, rainfall

def main():
    estimator = NPKEstimator()

    # Take user input from terminal
    crop_name = input("Enter Crop Name: ").strip()
    city = input("Enter City Name: ").strip()
    state = input("Enter State Name: ").strip()

    try:
        temperature, humidity, rainfall = get_weather(city, state)
        print(f"\nWeather Data for {city.title()}, {state.title()}:")
        print(f" Temperature: {temperature} °C")
        print(f" Humidity: {humidity} %")
        print(f" Rainfall: {rainfall} mm\n")

        npk_values = estimator.estimate_npk(crop_name, temperature, humidity, rainfall)

        print(f"NPK Recommendation for '{crop_name.title()}':")
        print(f" Nitrogen (N): {npk_values['Label_N']} units")
        print(f" Phosphorus (P): {npk_values['Label_P']} units")
        print(f" Potassium (K): {npk_values['Label_K']} units")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

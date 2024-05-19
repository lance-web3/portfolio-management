import requests

# Define the API endpoint URL
url = "https://api.coingecko.com/api/v3/coins/markets"

# Set the API parameters
params = {
    "vs_currency": "usd",
    "ids": "bitcoin,ethereum,litecoin"  # You can add more crypto IDs here
}

# Make the API request
response = requests.get(url, params=params)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()

    # Print the asset data
    for asset in data:
        print(f"Name: {asset['name']}")
        print(f"Symbol: {asset['symbol']}")
        print(f"Current Price: ${asset['current_price']}")
        print("---")
else:
    print("Failed to fetch data from the API.")
from config import MONITOR_PRICE, MONITOR_CURRENT_VOLUME, NTFY_HOST, NTFY_TOPIC, NTFY_USERNAME, NTFY_PASSWORD
import requests
from bs4 import BeautifulSoup

with open('drillisch-providers.txt', 'r') as f:
    providers = f.read().splitlines()

def get_offers(provider):
    response = requests.get(f"https://{provider}")
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    offers = []
    for offer_div in soup.select('.e-tarifbox'):
        price = float(offer_div.select_one('.c-price-before_decimal').text.strip()) + float(offer_div.select_one('.c-price-after_decimal').text.strip())/100
        volume = offer_div.select_one('.e-tarifbox-header-headline').text
        if 'GB' not in volume:
            continue
        volume = int(volume.replace('GB', '').strip())
        offers.append({'price': price, 'volume': volume})
    return offers

lowest_price = MONITOR_PRICE
highest_volume = MONITOR_CURRENT_VOLUME
best_provider = None

for provider in providers:
    for offer in get_offers(provider):
        price = offer['price']
        volume = offer['volume']
        if (price < lowest_price and volume >= highest_volume) or (price <= lowest_price and volume > highest_volume):
            lowest_price = price
            highest_volume = volume
            best_provider = provider

if lowest_price < MONITOR_PRICE or highest_volume > MONITOR_CURRENT_VOLUME:
    print(f"New mobile provider found: {best_provider} with price {lowest_price:.2f} € and data volume {highest_volume} GB (previous: {MONITOR_PRICE:.2f} € / {MONITOR_CURRENT_VOLUME} GB)")
    if NTFY_HOST and NTFY_TOPIC and NTFY_USERNAME and NTFY_PASSWORD:
        requests.post(
            f"{NTFY_HOST}/{NTFY_TOPIC}",
            auth=(NTFY_USERNAME, NTFY_PASSWORD),
            data=(
                f"New mobile provider found: {best_provider}\n"
                f"Price: {lowest_price:.2f} € (previous: {MONITOR_PRICE:.2f} €)\n"
                f"Data volume: {highest_volume} GB (previous: {MONITOR_CURRENT_VOLUME} GB)"
            )
        )
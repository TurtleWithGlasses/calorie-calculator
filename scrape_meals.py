import requests
from bs4 import BeautifulSoup
import psycopg2

postgresg_user = "postgres"
postgresg_pw = "mehmetsoylu"

# Insert meal data into PostgreSQL
def insert_meal_data(meals):
    conn = psycopg2.connect(
        host="localhost",
        database="calorie_tracker_db",
        user=postgresg_user,
        password=postgresg_pw
    )
    cursor = conn.cursor()
    cursor.executemany('INSERT INTO meals (name, calories) VALUES (%s, %s)', meals)
    conn.commit()
    conn.close()

# Scrape meals and calories from the given URL
def scrape_meals(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an error for bad responses
        soup = BeautifulSoup(response.content, 'html.parser')
    except requests.RequestException as e:
        print(f"Failed to retrieve {url}: {e}")
        return []

    meals = []

    meal_elements = soup.find_all('td', class_="food")
    calorie_elements = soup.find_all('td', class_="kcal")

    print(f"Number of meal elements found: {len(meal_elements)}")
    print(f"Number of calorie elements found: {len(calorie_elements)}")

    if len(meal_elements) == len(calorie_elements):
        for i, (meal, calorie) in enumerate(zip(meal_elements, calorie_elements)):
            meal_name = meal.get_text(strip=True)
            calorie_data = calorie.find("data")
            
            if calorie_data:
                calorie_value = calorie_data.get_text(strip=True)
                meals.append((meal_name, int(calorie_value)))
                print(f"Meal {i+1}: {meal_name}, Calories: {calorie_value}")
            else:
                print(f"Meal {i+1}: {meal_name}, No calorie data found")
    else:
        print(f"Mismatch between meals and calories for {url}")

    return meals

urls = [
    'https://www.kaloricetveli.org/yiyecek/alkollue-ickiler-ve-icecekler',
    'https://www.kaloricetveli.org/yiyecek/alkolsuez-icecekler',
    'https://www.kaloricetveli.org/yiyecek/baklagiller',
    'https://www.kaloricetveli.org/yiyecek/balik-ve-deniz-ueruenleri',
    'https://www.kaloricetveli.org/yiyecek/bira',
    'https://www.kaloricetveli.org/yiyecek/bitkisel-siviyaglar',
    'https://www.kaloricetveli.org/yiyecek/cerez-ve-cekirdekler',
    'https://www.kaloricetveli.org/yiyecek/corbalar',
    'https://www.kaloricetveli.org/yiyecek/dilimlenmis-peynir',
    'https://www.kaloricetveli.org/yiyecek/dip-soslar-ezmeler',
    'https://www.kaloricetveli.org/yiyecek/domuz-eti',
    'https://www.kaloricetveli.org/yiyecek/dondurma-donmus-tatlilar',
    'https://www.kaloricetveli.org/yiyecek/et-ve-et-ueruenleri',
    'https://www.kaloricetveli.org/yiyecek/fast-food',
    'https://www.kaloricetveli.org/yiyecek/geyik-ve-av-etleri',
    'https://www.kaloricetveli.org/yiyecek/kek-ve-tartlar',
    'https://www.kaloricetveli.org/yiyecek/konserve-meyveler',
    'https://www.kaloricetveli.org/yiyecek/krem-peynir',
    'https://www.kaloricetveli.org/yiyecek/kuemes-hayvanlari',
    'https://www.kaloricetveli.org/yiyecek/makarna-ve-noodle',
    'https://www.kaloricetveli.org/yiyecek/meyve-sulari',
    'https://www.kaloricetveli.org/yiyecek/meyveler',
    'https://www.kaloricetveli.org/yiyecek/otlar-ve-baharatlar',
    'https://www.kaloricetveli.org/yiyecek/pasta-malzemeleri',
    'https://www.kaloricetveli.org/yiyecek/pastalar-ekmek-ve-unlu-mamuller',
    'https://www.kaloricetveli.org/yiyecek/patates-ueruenleri',
    'https://www.kaloricetveli.org/yiyecek/peynir',
    'https://www.kaloricetveli.org/yiyecek/pizza',
    'https://www.kaloricetveli.org/yiyecek/sakatat-ve-ic-organlari',
    'https://www.kaloricetveli.org/yiyecek/sarap',
    'https://www.kaloricetveli.org/yiyecek/sebzeler',
    'https://www.kaloricetveli.org/yiyecek/sekerleme-ve-tatlilar',
    'https://www.kaloricetveli.org/yiyecek/sigir-ve-dana-eti',
    'https://www.kaloricetveli.org/yiyecek/sivi-ve-kati-yaglar',
    'https://www.kaloricetveli.org/yiyecek/soda-ve-mesrubatlar',
    'https://www.kaloricetveli.org/yiyecek/soegues-et-ve-sarkueteri-ueruenleri',
    'https://www.kaloricetveli.org/yiyecek/sosis-ve-sucuk',
    'https://www.kaloricetveli.org/yiyecek/soslar-ve-salata-soslari',
    'https://www.kaloricetveli.org/yiyecek/suet-ve-suet-ueruenleri',
    'https://www.kaloricetveli.org/yiyecek/tahillar-ve-tahilli-ueruenler',
    'https://www.kaloricetveli.org/yiyecek/tropik-ve-egzotik-meyveler',
    'https://www.kaloricetveli.org/yiyecek/yemekler-ve-oeguenler',
    'https://www.kaloricetveli.org/yiyecek/yogurt',
    'https://www.kaloricetveli.org/yiyecek/yulaf-ezmesi-muesli-ve-tahil-gevrekleri',
]

for url in urls:
    print(f"Scraping {url}...")
    meals = scrape_meals(url)
    if meals:
        insert_meal_data(meals)
        print(f"Inserted {len(meals)} meals from {url} into the database.")
    else:
        print(f"No meals scraped from {url}.")
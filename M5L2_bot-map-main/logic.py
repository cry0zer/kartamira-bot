import sqlite3
from config import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

class DB_Map():
    def __init__(self, database):
        self.database = database
    
    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]  
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1
            return 0
            
    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))
            cities = [row[0] for row in cursor.fetchall()]
            return cities

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT lat, lng FROM cities WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates

    def create_graph(self, path, cities):
        fig = plt.figure(figsize=(10, 5))
        ax = plt.axes(projection=ccrs.PlateCarree())
        
        # Фиксируем карту на весь мир, чтобы не было белого экрана
        ax.set_global()
        
        # Добавляем базовые слои карты для видимости материков
        ax.coastlines(resolution='110m', color='gray', linewidth=1)
        ax.add_feature(cfeature.LAND, facecolor='lightgray')
        ax.add_feature(cfeature.OCEAN, facecolor='azure')
        ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='gray')
        
        for city in cities:
            coordinates = self.get_coordinates(city)
            if coordinates:
                # Извлекаем широту и долготу по индексам из кортежа БД
                lat, lng = float(coordinates[0]), float(coordinates[1])
                
                # Рисуем точку и название города
                ax.plot(lng, lat, marker='o', color='red', markersize=6, transform=ccrs.Geodetic())
                ax.text(lng + 1.5, lat + 1.5, city, transform=ccrs.Geodetic(), fontsize=10, weight='bold')
                
        plt.savefig(path, bbox_inches='tight', dpi=150)
        plt.close(fig)
        
    def draw_distance(self, city1, city2):
        pass

if __name__ == "__main__":
    m = DB_Map(DATABASE)
    m.create_user_table()

import pandas as pd
import folium
from folium.plugins import HeatMap
import requests

# ---------- Координаты центров регионов ----------
REGION_COORDINATES = {
    'Адыгея': [44.6098, 40.1004],
    'Алтайский': [52.5186, 85.2040],
    'Амурская': [50.2907, 127.5272],
    'Архангельская': [64.5393, 40.5186],
    'Астраханская': [46.3479, 48.0336],
    'Башкортостан': [54.7355, 55.9587],
    'Белгородская': [50.5978, 36.5858],
    'Брянская': [53.2434, 34.3642],
    'Бурятия': [52.7182, 109.1770],
    'Владимирская': [56.1290, 40.4066],
    'Волгоградская': [48.7080, 44.5133],
    'Вологодская': [59.2181, 39.8890],
    'Воронежская': [51.6615, 39.2003],
    'Дагестан': [42.9849, 47.5047],
    'Еврейская': [48.7947, 132.9218],
    'Забайкальский': [52.0333, 113.5000],
    'Ивановская': [57.0003, 40.9739],
    'Ингушетия': [43.1151, 45.0000],
    'Иркутская': [52.2864, 104.2807],
    'Кабардино-Балкария': [43.4853, 43.6071],
    'Калининградская': [54.7104, 20.4522],
    'Калмыкия': [46.2313, 45.3272],
    'Калужская': [54.5138, 36.2612],
    'Камчатский': [53.0190, 158.5236],
    'Карелия': [61.7850, 34.3469],
    'Кемеровская': [55.3547, 86.0873],
    'Кировская': [58.6036, 49.6680],
    'Коми': [61.6688, 50.8354],
    'Костромская': [57.7677, 40.9264],
    'Краснодарский': [45.0355, 38.9753],
    'Красноярский': [56.0153, 92.8932],
    'Крым': [44.9521, 34.1024],
    'Курганская': [55.4410, 65.3411],
    'Курская': [51.7304, 36.1926],
    'КЧР ( Карачаево-Черкесия )': [43.9133, 41.9260],
    'Ленинградская': [59.9391, 30.3159],
    'Липецкая': [52.6088, 39.5992],
    'Магаданская': [59.5603, 150.7985],
    'Марий Эл': [56.6344, 47.8999],
    'Мордовия': [54.1808, 45.1861],
    'Московская': [55.7558, 37.6173],
    'Мурманская': [68.9585, 33.0827],
    'Нижегородская': [56.3269, 44.0065],
    'Новгородская': [58.5228, 31.2699],
    'Новосибирская': [55.0084, 82.9357],
    'Омская': [54.9893, 73.3682],
    'Оренбургская': [51.7872, 55.1018],
    'Орловская': [52.9671, 36.0697],
    'Пензенская': [53.2007, 45.0046],
    'Пермский': [58.0105, 56.2294],
    'Приморский': [43.1155, 131.8855],
    'Псковская': [57.8194, 28.3318],
    'Респ. Алтай': [50.7114, 86.9353],
    'Ростовская': [47.2224, 39.7189],
    'РСО ( Северная Осетия )': [43.0241, 44.6813],
    'Рязанская': [54.6294, 39.7420],
    'Самарская': [53.1951, 50.1069],
    'Саратовская': [51.5336, 46.0343],
    'Саха (Якутия)': [62.0278, 129.7315],
    'Сахалинская': [46.9591, 142.7380],
    'Свердловская': [56.8389, 60.6057],
    'Смоленская': [54.7826, 32.0453],
    'Ставропольский': [45.0433, 41.9691],
    'Тамбовская': [52.7212, 41.4523],
    'Татарстан': [55.7944, 49.1114],
    'Тверская': [56.8587, 35.9176],
    'Томская': [56.4846, 84.9482],
    'Тульская': [54.1931, 37.6173],
    'Тыва': [51.7191, 94.4380],
    'Тюменская': [57.1530, 65.5343],
    'Удмуртская': [56.8527, 53.2115],
    'Ульяновская': [54.3142, 48.4031],
    'Хабаровский': [48.4802, 135.0719],
    'Хакасия': [53.7223, 91.4435],
    'ХМАО': [61.0032, 69.0189],
    'Челябинская': [55.1644, 61.4368],
    'Чеченская': [43.3180, 45.6883],
    'Чувашия': [56.1439, 47.2489],
    'Чукотский': [66.0000, 169.0000],
    'ЯНАО': [66.5299, 66.6145],
    'Ярославская': [57.6261, 39.8845]
}

# ---------- Маппинг GeoJSON → CSV ----------
REGION_NAME_MAPPING = {
    'Адыгея': 'Адыгея',
    'Алтайский край': 'Алтайский',
    'Алтай': 'Респ. Алтай',
    'Амурская область': 'Амурская',
    'Архангельская область': 'Архангельская',
    'Астраханская область': 'Астраханская',
    'Башкортостан': 'Башкортостан',
    'Белгородская область': 'Белгородская',
    'Брянская область': 'Брянская',
    'Бурятия': 'Бурятия',
    'Владимирская область': 'Владимирская',
    'Волгоградская область': 'Волгоградская',
    'Вологодская область': 'Вологодская',
    'Воронежская область': 'Воронежская',
    'Дагестан': 'Дагестан',
    'Еврейская автономная область': 'Еврейская',
    'Забайкальский край': 'Забайкальский',
    'Ивановская область': 'Ивановская',
    'Ингушетия': 'Ингушетия',
    'Иркутская область': 'Иркутская',
    'Кабардино-Балкарская республика': 'Кабардино-Балкария',
    'Калининградская область': 'Калининградская',
    'Республика Калмыкия': 'Калмыкия',
    'Калужская область': 'Калужская',
    'Камчатский край': 'Камчатский',
    'Республика Карелия': 'Карелия',
    'Кемеровская область': 'Кемеровская',
    'Кировская область': 'Кировская',
    'Республика Коми': 'Коми',
    'Костромская область': 'Костромская',
    'Краснодарский край': 'Краснодарский',
    'Красноярский край': 'Красноярский',
    'Крым': 'Крым',
    'Курганская область': 'Курганская',
    'Курская область': 'Курская',
    'Карачаево-Черкесская республика': 'КЧР ( Карачаево-Черкесия )',
    'Ленинградская область': 'Ленинградская',
    'Липецкая область': 'Липецкая',
    'Магаданская область': 'Магаданская',
    'Марий Эл': 'Марий Эл',
    'Республика Мордовия': 'Мордовия',
    'Москва': 'Московская',
    'Московская область': 'Московская',
    'Мурманская область': 'Мурманская',
    'Нижегородская область': 'Нижегородская',
    'Новгородская область': 'Новгородская',
    'Новосибирская область': 'Новосибирская',
    'Омская область': 'Омская',
    'Оренбургская область': 'Оренбургская',
    'Орловская область': 'Орловская',
    'Пензенская область': 'Пензенская',
    'Пермский край': 'Пермский',
    'Приморский край': 'Приморский',
    'Псковская область': 'Псковская',
    'Ростовская область': 'Ростовская',
    'Северная Осетия - Алания': 'РСО ( Северная Осетия )',
    'Рязанская область': 'Рязанская',
    'Самарская область': 'Самарская',
    'Санкт-Петербург': 'Ленинградская',
    'Саратовская область': 'Саратовская',
    'Республика Саха (Якутия)': 'Саха (Якутия)',
    'Сахалинская область': 'Сахалинская',
    'Свердловская область': 'Свердловская',
    'Смоленская область': 'Смоленская',
    'Ставропольский край': 'Ставропольский',
    'Тамбовская область': 'Тамбовская',
    'Татарстан': 'Татарстан',
    'Тверская область': 'Тверская',
    'Томская область': 'Томская',
    'Тульская область': 'Тульская',
    'Тыва': 'Тыва',
    'Тюменская область': 'Тюменская',
    'Удмуртская республика': 'Удмуртская',
    'Ульяновская область': 'Ульяновская',
    'Хабаровский край': 'Хабаровский',
    'Республика Хакасия': 'Хакасия',
    'Ханты-Мансийский автономный округ - Югра': 'ХМАО',
    'Челябинская область': 'Челябинская',
    'Чеченская республика': 'Чеченская',
    'Чувашия': 'Чувашия',
    'Чукотский автономный округ': 'Чукотский',
    'Ямало-Ненецкий автономный округ': 'ЯНАО',
    'Ярославская область': 'Ярославская',
    'Ненецкий автономный округ': 'Архангельская'
}

# ---------- Цветовая палитра ----------
COLOR_PALETTE = {
    
    'very_high': '#B22222',   # Firebrick
    'high': '#DC143C',  # Crimson
    'medium_high':'#FF4500',  # Orange Red
    'medium':'#FF8C00',  # Dark Orange
    'medium_low': '#FFA500',  # Orange
    'low': '#FFD700',  # Gold
    'very_low': '#FFFF00',  # Bright Yellow
    'border': '#DDC1F3',
    'marker': '#7B1FA2'
}

def get_color_for_value(value, df):
    """
    Get color for value based on quantiles from dataframe
    """
    # Calculate quantiles from the 'Колво на 100к' column
    q95 = df['Колво на 100к'].quantile(0.95)  # 95th percentile
    q85 = df['Колво на 100к'].quantile(0.85)  # 85th percentile
    q70 = df['Колво на 100к'].quantile(0.70)  # 70th percentile
    q50 = df['Колво на 100к'].quantile(0.50)  # 50th percentile (median)
    q30 = df['Колво на 100к'].quantile(0.30)  # 30th percentile
    q15 = df['Колво на 100к'].quantile(0.15)  # 15th percentile
    
    if value >= q95:
        return COLOR_PALETTE['very_high']
    elif value >= q85:
        return COLOR_PALETTE['high']
    elif value >= q70:
        return COLOR_PALETTE['medium_high']
    elif value >= q50:
        return COLOR_PALETTE['medium']
    elif value >= q30:
        return COLOR_PALETTE['medium_low']
    elif value >= q15:
        return COLOR_PALETTE['low']
    else:
        return COLOR_PALETTE['very_low']

# ---------- Создание popup для региона ----------
def create_popup_for_region(geojson_region_name):
    csv_region_name = REGION_NAME_MAPPING.get(geojson_region_name, geojson_region_name)
    region_row = df[df['Регион'] == csv_region_name]
    if region_row.empty:
        return folium.Popup("Нет данных", max_width=250)

    row = region_row.iloc[0]
    popup_html = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; width: 300px;">
        <div style="background: linear-gradient(135deg, {COLOR_PALETTE['marker']}, #9C27B0); 
             padding: 18px; color: white; border-radius: 10px 10px 0 0;">
            <h3 style="margin: 0; font-size: 20px;">{row['Регион']}</h3>
        </div>
        <div style="padding: 18px; background: white; border-radius: 0 0 10px 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 18px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                     padding: 12px; border-radius: 8px; text-align: center;">
                    <div style="font-weight: bold; color: white; font-size: 20px;">{row['Кол-во заявок']:,}</div>
                    <div style="font-size: 11px; color: rgba(255,255,255,0.9);">Всего заявок</div>
                </div>
                <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                     padding: 12px; border-radius: 8px; text-align: center;">
                    <div style="font-weight: bold; color: white; font-size: 20px;">{row['Колво на 100к']:.2f}</div>
                    <div style="font-size: 11px; color: rgba(255,255,255,0.9);">На 100к</div>
                </div>
            </div>
            <div style="margin-bottom: 12px; padding: 10px; background: #f0f8ff; border-radius: 6px;">
                <div style="font-size: 12px; color: #666;">Население:</div>
                <div style="font-size: 16px; font-weight: bold;">{int(row['Население']):,}</div>
            </div>
            <div style="border-top: 2px solid #f0f0f0; padding-top: 12px;">
                <div style="display: flex; justify-content: space-between;"><span>Активные:</span><strong>{row['Актив']}</strong></div>
                <div style="display: flex; justify-content: space-between;"><span>Инфопоиск:</span><strong>{row['Инфопоиск']}</strong></div>
                <div style="display: flex; justify-content: space-between;"><span>Автоном:</span><strong>{row['Автоном']}</strong></div>
                <div style="display: flex; justify-content: space-between;"><span>ЛНС:</span><strong>{row['ЛНС']}</strong></div>
                <div style="display: flex; justify-content: space-between;"><span>Погибло:</span><strong style="color:red">{row['Погиб']}</strong></div>
                <div style="display: flex; justify-content: space-between;"><span>Утонуло:</span><strong style="color:blue">{row['Утонул']}</strong></div>
            </div>
        </div>
    </div>
    """
    return folium.Popup(popup_html, max_width=320)

# ---------- 2GIS Tile Layers ----------
def create_2gis_tile_layers():
    """Create 2GIS tile layers that mimic OpenStreetMap style"""
    
    # 2GIS Vector Light (similar to CartoDB positron)
    tiles_2gis_light = folium.TileLayer(
        tiles='https://tile2.maps.2gis.com/tiles?x={x}&y={y}&z={z}',
        attr='2GIS',
        name='2GIS Light',
        control=True,
        opacity=1.0
    )
    
    # 2GIS Basic (similar to standard OSM)
    tiles_2gis_basic = folium.TileLayer(
        tiles='https://tile1.maps.2gis.com/tiles?x={x}&y={y}&z={z}',
        attr='2GIS',
        name='2GIS Basic',
        control=True,
        opacity=1.0
    )
    
    return tiles_2gis_light, tiles_2gis_basic

# ---------- Основная функция построения карты ----------
def create_stylish_map(df):
    max_value = df['Колво на 100к'].max()
    min_value = df['Колво на 100к'].min()
    mean_value = df['Колво на 100к'].mean()

    print(f"📊 Диапазон значений на 100к населения:")
    print(f"   Минимум: {min_value:.2f}")
    print(f"   Максимум: {max_value:.2f}")
    print(f"   Среднее: {mean_value:.2f}")

    # Создаем карту с 2GIS в качестве базового слоя
    m = folium.Map(location=[61.5, 95], zoom_start=3, tiles=None, control_scale=True)
    
    # Добавляем 2GIS слои
    tiles_2gis_light, tiles_2gis_basic = create_2gis_tile_layers()
    tiles_2gis_light.add_to(m)
    tiles_2gis_basic.add_to(m)

    # Тепловая карта
    heat_data = [[row['latitude'], row['longitude'], row['Колво на 100к']] for _, row in df.iterrows()]
    heatmap_layer = folium.FeatureGroup(name='Тепловая карта', show=False)
    HeatMap(heat_data, min_opacity=0.4, max_opacity=0.95, radius=45, blur=30, max_zoom=13,
            gradient={0.0: '#00CED1', 0.2: '#00FF00', 0.4: '#FFFF00', 0.6: '#FFA500', 0.8: '#FF4500', 1.0: '#8B0000'}).add_to(heatmap_layer)
    heatmap_layer.add_to(m)

    # GeoJSON слой регионов
    regions_layer = folium.FeatureGroup(name='Регионы с данными', show=True)
    geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/russia.geojson"
    geojson_data = requests.get(geojson_url).json()

    # ---------- Добавляем регионы по одному с popup ----------
    for feature in geojson_data['features']:
        geo_name = feature['properties']['name']
        csv_name = REGION_NAME_MAPPING.get(geo_name, geo_name)
        row = df[df['Регион'] == csv_name]
        if row.empty:
            continue

        region_popup = create_popup_for_region(geo_name)
        color = get_color_for_value(row['Колво на 100к'].iloc[0], df)

        folium.GeoJson(
            feature,
            style_function=lambda f, color=color: {
                'fillColor': color,
                'color': COLOR_PALETTE['border'],
                'weight': 1.2,
                'fillOpacity': 0.8,
                'dashArray': '3, 3'
            },
            highlight_function=lambda f: {
                'fillColor': '#ffffff',
                'color': 'none',           # ← убираем обводку
                'weight': 0,               # ← толщина 0
                'fillOpacity': 0.4
            },
            popup=region_popup,
            tooltip=folium.GeoJsonTooltip(
                fields=['name'],
                aliases=['Регион:'],
                style=("background-color: white; color: #333; font-family: Arial; "
                       "font-size: 12px; padding: 8px; border-radius: 4px;")
            )
        ).add_to(regions_layer)

    regions_layer.add_to(m)

    # Легенда
    legend_html = f'''
    <div style="position: fixed; bottom: 50px; left: 50px; width: 320px; background: white; border: none; z-index:9999;
         font-family: 'Segoe UI', Arial; font-size: 13px; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
         <h4 style="margin: 0 0 16px 0; color: #2C3E50; font-size: 16px; font-weight: 600;">
            📊 Статистика пропавших (на 100к населения)
         </h4>
         <div style="display: grid; grid-template-columns: 25px 1fr; gap: 10px; align-items: center;">
            <div style="width: 20px; height: 20px; background: {COLOR_PALETTE['very_high']}; border-radius: 4px;"></div>
            <div>Критический (≥200)</div>
            <div style="width: 20px; height: 20px; background: {COLOR_PALETTE['high']}; border-radius: 4px;"></div>
            <div>Очень высокий (150-200)</div>
            <div style="width: 20px; height: 20px; background: {COLOR_PALETTE['medium_high']}; border-radius: 4px;"></div>
            <div>Высокий (100-150)</div>
            <div style="width: 20px; height: 20px; background: {COLOR_PALETTE['medium']}; border-radius: 4px;"></div>
            <div>Повышенный (60-100)</div>
            <div style="width: 20px; height: 20px; background: {COLOR_PALETTE['medium_low']}; border-radius: 4px;"></div>
            <div>Средний (30-60)</div>
            <div style="width: 20px; height: 20px; background: {COLOR_PALETTE['low']}; border-radius: 4px;"></div>
            <div>Низкий (15-30)</div>
            <div style="width: 20px; height: 20px; background: {COLOR_PALETTE['very_low']}; border-radius: 4px;"></div>
            <div>Минимальный (<15)</div>
         </div>
         <div style="margin-top: 16px; padding-top: 12px; border-top: 2px solid #f0f0f0;">
            <div>📌 Кликните на регион для детальной статистики</div>
            <div>🔥 Переключатель слоев в правом верхнем углу</div>
         </div>
         <div style="margin-top: 12px; padding: 10px; background: #f8f9fa; border-radius: 6px;">
            <small><strong>Диапазон:</strong> {min_value:.2f} - {max_value:.2f}<br><strong>Среднее:</strong> {mean_value:.2f}</small>
         </div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    folium.LayerControl(position='topright', collapsed=False).add_to(m)
    m.get_root().header.add_child(folium.Element('''
        <style>
            /* Убирает фокус-рамку вокруг полигона */
            .leaflet-container path:focus {
                outline: none !important;
                box-shadow: none !important;
                stroke: none !important;
            }
        </style>
    '''))
    return m

# ---------- Запуск ----------
if __name__ == "__main__":
    df = pd.read_csv('russian_regions_81.csv')
    df['Колво на 100к'] = (df['Кол-во заявок'] / df['Население']) * 100000
    df['latitude'] = df['Регион'].map(lambda x: REGION_COORDINATES.get(x, [55.7558, 37.6173])[0])
    df['longitude'] = df['Регион'].map(lambda x: REGION_COORDINATES.get(x, [55.7558, 37.6173])[1])

    stylish_map = create_stylish_map(df)
    stylish_map.save('stylish_russia_map.html')
    print("✅ Карта создана: откройте stylish_russia_map.html")
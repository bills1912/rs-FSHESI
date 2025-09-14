import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import geopandas as gpd
from datetime import datetime, timedelta
import json
import random
from typing import Dict, List, Tuple

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Monitoring Pulau Sumatera",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stSelectbox > div > div {
        background-color: #ffffff;
    }
    .header-style {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .indicator-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #2a5298;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def generate_sumatera_data():
    """Generate sample data untuk provinsi di Pulau Sumatera"""
    sumatera_provinces = [
        {"name": "Aceh", "lat": 4.695135, "lon": 96.749397, "capital": "Banda Aceh"},
        {"name": "Sumatera Utara", "lat": 2.1153547, "lon": 99.5450974, "capital": "Medan"},
        {"name": "Sumatera Barat", "lat": -0.7399397, "lon": 100.8000051, "capital": "Padang"},
        {"name": "Riau", "lat": 0.2933469, "lon": 101.7068294, "capital": "Pekanbaru"},
        {"name": "Kepulauan Riau", "lat": 3.9456514, "lon": 108.1428669, "capital": "Tanjung Pinang"},
        {"name": "Jambi", "lat": -1.4851831, "lon": 102.4380581, "capital": "Jambi"},
        {"name": "Sumatera Selatan", "lat": -3.3194374, "lon": 103.914399, "capital": "Palembang"},
        {"name": "Bangka Belitung", "lat": -2.7410513, "lon": 106.4405872, "capital": "Pangkal Pinang"},
        {"name": "Bengkulu", "lat": -3.8004871, "lon": 102.2655756, "capital": "Bengkulu"},
        {"name": "Lampung", "lat": -4.5585849, "lon": 105.4068079, "capital": "Bandar Lampung"}
    ]
    
    data = []
    for province in sumatera_provinces:
        # Data kemiskinan
        pou = round(random.uniform(3.5, 18.5), 2)
        fies_mild = round(random.uniform(18.0, 42.0), 2)
        fies_moderate = round(random.uniform(9.0, 28.0), 2)
        fies_severe = round(random.uniform(3.0, 15.0), 2)
        
        # Data gas rumah kaca (dalam unit yang sesuai)
        co_level = round(random.uniform(0.8, 2.5), 3)  # mg/m³
        no2_level = round(random.uniform(15.0, 85.0), 2)  # µg/m³
        ch4_level = round(random.uniform(1.8, 3.2), 3)  # ppm
        
        # Data ketenagakerjaan
        ntp = round(random.uniform(95.0, 115.0), 2)  # Nilai Tukar Petani
        agri_workers = round(random.uniform(25.0, 65.0), 2)  # % penduduk bekerja di pertanian
        
        data.append({
            'province': province['name'],
            'latitude': province['lat'],
            'longitude': province['lon'],
            'capital': province['capital'],
            'pou_percentage': pou,
            'fies_mild': fies_mild,
            'fies_moderate': fies_moderate,
            'fies_severe': fies_severe,
            'co_level': co_level,
            'no2_level': no2_level,
            'ch4_level': ch4_level,
            'ntp': ntp,
            'agri_workers_percentage': agri_workers,
            'population': random.randint(800000, 14000000)
        })
    
    return pd.DataFrame(data)

@st.cache_data
def generate_time_series_data(provinces: List[str], days: int = 30):
    """Generate time series data untuk trending"""
    dates = [datetime.now() - timedelta(days=x) for x in range(days, 0, -1)]
    
    time_series = []
    for date in dates:
        for province in provinces:
            time_series.append({
                'date': date,
                'province': province,
                'co_trend': round(random.uniform(0.5, 3.0), 3),
                'no2_trend': round(random.uniform(10.0, 90.0), 2),
                'ch4_trend': round(random.uniform(1.5, 3.5), 3),
                'pou_trend': round(random.uniform(2.0, 20.0), 2),
                'ntp_trend': round(random.uniform(90.0, 120.0), 2)
            })
    
    return pd.DataFrame(time_series)

def create_poverty_map(df: pd.DataFrame, indicator: str):
    """Membuat peta untuk indikator kemiskinan"""
    # Koordinat tengah Sumatera
    center_lat = df['latitude'].mean()
    center_lon = df['longitude'].mean()
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    # Color mapping berdasarkan indikator
    if indicator == 'PoU':
        values = df['pou_percentage']
        colormap = folium.LinearColormap(
            colors=['green', 'yellow', 'orange', 'red'],
            vmin=values.min(),
            vmax=values.max(),
            caption=f'{indicator} (%)'
        )
    elif indicator == 'FIES Severe':
        values = df['fies_severe']
        colormap = folium.LinearColormap(
            colors=['lightgreen', 'yellow', 'orange', 'red'],
            vmin=values.min(),
            vmax=values.max(),
            caption=f'{indicator} (%)'
        )
    
    # Menambahkan markers
    for idx, row in df.iterrows():
        if indicator == 'PoU':
            popup_text = f"""
            <div style="width: 200px;">
                <h4>{row['province']}</h4>
                <b>Ibukota:</b> {row['capital']}<br>
                <b>PoU:</b> {row['pou_percentage']}%<br>
                <b>FIES Mild:</b> {row['fies_mild']}%<br>
                <b>FIES Moderate:</b> {row['fies_moderate']}%<br>
                <b>FIES Severe:</b> {row['fies_severe']}%<br>
                <b>Populasi:</b> {row['population']:,}
            </div>
            """
            color_val = row['pou_percentage']
        else:
            popup_text = f"""
            <div style="width: 200px;">
                <h4>{row['province']}</h4>
                <b>Ibukota:</b> {row['capital']}<br>
                <b>FIES Severe:</b> {row['fies_severe']}%<br>
                <b>FIES Moderate:</b> {row['fies_moderate']}%<br>
                <b>FIES Mild:</b> {row['fies_mild']}%<br>
                <b>Populasi:</b> {row['population']:,}
            </div>
            """
            color_val = row['fies_severe']
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=10 + (color_val / values.max()) * 20,
            popup=folium.Popup(popup_text, max_width=250),
            color='black',
            weight=1,
            fillColor=colormap(color_val),
            fillOpacity=0.7,
            tooltip=f"{row['province']}: {color_val}%"
        ).add_to(m)
    
    colormap.add_to(m)
    return m

def create_greenhouse_map(df: pd.DataFrame, gas_type: str):
    """Membuat peta untuk gas rumah kaca"""
    center_lat = df['latitude'].mean()
    center_lon = df['longitude'].mean()
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    # Color mapping dan unit berdasarkan jenis gas
    if gas_type == 'CO':
        values = df['co_level']
        unit = 'mg/m³'
        colors = ['lightblue', 'yellow', 'orange', 'red']
    elif gas_type == 'NO2':
        values = df['no2_level']
        unit = 'µg/m³'
        colors = ['lightgreen', 'yellow', 'orange', 'red']
    elif gas_type == 'CH4':
        values = df['ch4_level']
        unit = 'ppm'
        colors = ['lightcyan', 'yellow', 'orange', 'darkred']
    
    colormap = folium.LinearColormap(
        colors=colors,
        vmin=values.min(),
        vmax=values.max(),
        caption=f'{gas_type} ({unit})'
    )
    
    # Menambahkan markers
    for idx, row in df.iterrows():
        popup_text = f"""
        <div style="width: 200px;">
            <h4>{row['province']}</h4>
            <b>Ibukota:</b> {row['capital']}<br>
            <b>CO:</b> {row['co_level']} mg/m³<br>
            <b>NO2:</b> {row['no2_level']} µg/m³<br>
            <b>CH4:</b> {row['ch4_level']} ppm<br>
        </div>
        """
        
        if gas_type == 'CO':
            color_val = row['co_level']
        elif gas_type == 'NO2':
            color_val = row['no2_level']
        else:
            color_val = row['ch4_level']
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=8 + (color_val / values.max()) * 15,
            popup=folium.Popup(popup_text, max_width=250),
            color='black',
            weight=1,
            fillColor=colormap(color_val),
            fillOpacity=0.8,
            tooltip=f"{row['province']}: {color_val} {unit}"
        ).add_to(m)
    
    colormap.add_to(m)
    return m

def create_employment_map(df: pd.DataFrame, indicator: str):
    """Membuat peta untuk indikator ketenagakerjaan"""
    center_lat = df['latitude'].mean()
    center_lon = df['longitude'].mean()
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    if indicator == 'NTP':
        values = df['ntp']
        unit = ''
        colors = ['red', 'orange', 'yellow', 'lightgreen', 'green']
    else:  # Agricultural Workers
        values = df['agri_workers_percentage']
        unit = '%'
        colors = ['lightblue', 'blue', 'darkblue', 'navy']
    
    colormap = folium.LinearColormap(
        colors=colors,
        vmin=values.min(),
        vmax=values.max(),
        caption=f'{indicator} {unit}'
    )
    
    # Menambahkan markers
    for idx, row in df.iterrows():
        popup_text = f"""
        <div style="width: 200px;">
            <h4>{row['province']}</h4>
            <b>Ibukota:</b> {row['capital']}<br>
            <b>NTP:</b> {row['ntp']}<br>
            <b>Pekerja Pertanian:</b> {row['agri_workers_percentage']}%<br>
            <b>Populasi:</b> {row['population']:,}
        </div>
        """
        
        if indicator == 'NTP':
            color_val = row['ntp']
        else:
            color_val = row['agri_workers_percentage']
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=8 + (color_val / values.max()) * 15,
            popup=folium.Popup(popup_text, max_width=250),
            color='black',
            weight=1,
            fillColor=colormap(color_val),
            fillOpacity=0.8,
            tooltip=f"{row['province']}: {color_val}{unit}"
        ).add_to(m)
    
    colormap.add_to(m)
    return m

def main():
    # Header
    st.markdown("""
    <div class="header-style">
        <h1>🌴 Dashboard Monitoring Indikator Pulau Sumatera</h1>
        <p>Monitoring Kemiskinan, Gas Rumah Kaca, dan Ketenagakerjaan</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    df = generate_sumatera_data()
    time_series_df = generate_time_series_data(df['province'].tolist())
    
    # Sidebar
    st.sidebar.header("🔧 Pengaturan Dashboard")
    
    # Pilihan kategori monitoring
    monitoring_type = st.sidebar.selectbox(
        "Pilih Kategori Monitoring:",
        ["📊 Overview", "🍽️ Indikator Kemiskinan", "🏭 Gas Rumah Kaca", "👨‍🌾 Ketenagakerjaan", "📈 Analisis Trend"]
    )
    
    if monitoring_type == "📊 Overview":
        st.header("📊 Ringkasan Indikator Sumatera")
        
        # Statistik overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="indicator-card">
                <h3>🍽️ Kemiskinan</h3>
                <h2>{:.1f}%</h2>
                <p>Rata-rata PoU</p>
            </div>
            """.format(df['pou_percentage'].mean()), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="indicator-card">
                <h3>🏭 Gas CO</h3>
                <h2>{:.2f}</h2>
                <p>Rata-rata mg/m³</p>
            </div>
            """.format(df['co_level'].mean()), unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="indicator-card">
                <h3>👨‍🌾 NTP</h3>
                <h2>{:.1f}</h2>
                <p>Rata-rata Nilai Tukar Petani</p>
            </div>
            """.format(df['ntp'].mean()), unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="indicator-card">
                <h3>🌾 Pertanian</h3>
                <h2>{:.1f}%</h2>
                <p>Rata-rata Pekerja Pertanian</p>
            </div>
            """.format(df['agri_workers_percentage'].mean()), unsafe_allow_html=True)
        
        # Tabel ringkasan
        st.subheader("📋 Data Provinsi Sumatera")
        
        summary_df = df[['province', 'capital', 'pou_percentage', 'co_level', 'ntp', 'agri_workers_percentage']].copy()
        summary_df.columns = ['Provinsi', 'Ibukota', 'PoU (%)', 'CO (mg/m³)', 'NTP', 'Pekerja Pertanian (%)']
        
        st.dataframe(
            summary_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Peta overview
        st.subheader("🗺️ Peta Overview Sumatera")
        overview_map = create_poverty_map(df, 'PoU')
        st_folium(overview_map, width=700, height=500)
    
    elif monitoring_type == "🍽️ Indikator Kemiskinan":
        st.header("🍽️ Monitoring Indikator Kemiskinan")
        
        # Pilihan indikator kemiskinan
        poverty_indicator = st.sidebar.selectbox(
            "Pilih Indikator:",
            ["PoU (Prevalence of Undernourishment)", "FIES Severe (Food Insecurity)"]
        )
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"🗺️ Peta {poverty_indicator}")
            if "PoU" in poverty_indicator:
                poverty_map = create_poverty_map(df, 'PoU')
            else:
                poverty_map = create_poverty_map(df, 'FIES Severe')
            st_folium(poverty_map, width=600, height=500)
        
        with col2:
            st.subheader("📊 Statistik Kemiskinan")
            
            if "PoU" in poverty_indicator:
                # Bar chart PoU
                fig_bar = px.bar(
                    df.sort_values('pou_percentage'),
                    x='pou_percentage',
                    y='province',
                    orientation='h',
                    title="PoU per Provinsi (%)",
                    color='pou_percentage',
                    color_continuous_scale='Reds'
                )
                fig_bar.update_layout(height=400)
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # Statistik deskriptif
                st.metric("Rata-rata PoU", f"{df['pou_percentage'].mean():.2f}%")
                st.metric("Tertinggi", f"{df['pou_percentage'].max():.2f}%")
                st.metric("Terendah", f"{df['pou_percentage'].min():.2f}%")
            else:
                # FIES comparison
                fies_data = df[['province', 'fies_mild', 'fies_moderate', 'fies_severe']].melt(
                    id_vars=['province'],
                    var_name='FIES_Level',
                    value_name='Percentage'
                )
                
                fig_fies = px.bar(
                    fies_data,
                    x='province',
                    y='Percentage',
                    color='FIES_Level',
                    title="Perbandingan Tingkat FIES",
                    barmode='stack'
                )
                fig_fies.update_xaxes(tickangle=45)
                fig_fies.update_layout(height=400)
                st.plotly_chart(fig_fies, use_container_width=True)
        
        # Tabel detail kemiskinan
        st.subheader("📋 Detail Data Kemiskinan")
        poverty_detail = df[['province', 'pou_percentage', 'fies_mild', 'fies_moderate', 'fies_severe']].copy()
        poverty_detail.columns = ['Provinsi', 'PoU (%)', 'FIES Mild (%)', 'FIES Moderate (%)', 'FIES Severe (%)']
        st.dataframe(poverty_detail, use_container_width=True, hide_index=True)
    
    elif monitoring_type == "🏭 Gas Rumah Kaca":
        st.header("🏭 Monitoring Gas Rumah Kaca")
        
        # Pilihan jenis gas
        gas_type = st.sidebar.selectbox(
            "Pilih Jenis Gas:",
            ["CO (Carbon Monoxide)", "NO2 (Nitrogen Dioxide)", "CH4 (Methane)"]
        )
        
        gas_short = gas_type.split()[0]  # Ambil bagian pertama (CO, NO2, CH4)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"🗺️ Peta Konsentrasi {gas_short}")
            ghg_map = create_greenhouse_map(df, gas_short)
            st_folium(ghg_map, width=600, height=500)
        
        with col2:
            st.subheader(f"📊 Statistik {gas_short}")
            
            if gas_short == 'CO':
                column = 'co_level'
                unit = 'mg/m³'
                color_scale = 'Oranges'
            elif gas_short == 'NO2':
                column = 'no2_level'
                unit = 'µg/m³'
                color_scale = 'Reds'
            else:  # CH4
                column = 'ch4_level'
                unit = 'ppm'
                color_scale = 'Blues'
            
            # Bar chart
            fig_bar = px.bar(
                df.sort_values(column),
                x=column,
                y='province',
                orientation='h',
                title=f"{gas_short} per Provinsi ({unit})",
                color=column,
                color_continuous_scale=color_scale
            )
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Statistik deskriptif
            st.metric(f"Rata-rata {gas_short}", f"{df[column].mean():.3f} {unit}")
            st.metric("Tertinggi", f"{df[column].max():.3f} {unit}")
            st.metric("Terendah", f"{df[column].min():.3f} {unit}")
        
        # Perbandingan semua gas
        st.subheader("📊 Perbandingan Gas Rumah Kaca")
        
        # Normalize data untuk perbandingan
        df_normalized = df.copy()
        df_normalized['co_norm'] = (df['co_level'] - df['co_level'].min()) / (df['co_level'].max() - df['co_level'].min()) * 100
        df_normalized['no2_norm'] = (df['no2_level'] - df['no2_level'].min()) / (df['no2_level'].max() - df['no2_level'].min()) * 100
        df_normalized['ch4_norm'] = (df['ch4_level'] - df['ch4_level'].min()) / (df['ch4_level'].max() - df['ch4_level'].min()) * 100
        
        ghg_comparison = df_normalized[['province', 'co_norm', 'no2_norm', 'ch4_norm']].melt(
            id_vars=['province'],
            var_name='Gas_Type',
            value_name='Normalized_Level'
        )
        
        fig_comparison = px.bar(
            ghg_comparison,
            x='province',
            y='Normalized_Level',
            color='Gas_Type',
            title="Perbandingan Relatif Gas Rumah Kaca (Normalized)",
            barmode='group'
        )
        fig_comparison.update_xaxes(tickangle=45)
        st.plotly_chart(fig_comparison, use_container_width=True)
        
        # Tabel detail gas rumah kaca
        st.subheader("📋 Detail Data Gas Rumah Kaca")
        ghg_detail = df[['province', 'co_level', 'no2_level', 'ch4_level']].copy()
        ghg_detail.columns = ['Provinsi', 'CO (mg/m³)', 'NO2 (µg/m³)', 'CH4 (ppm)']
        st.dataframe(ghg_detail, use_container_width=True, hide_index=True)
    
    elif monitoring_type == "👨‍🌾 Ketenagakerjaan":
        st.header("👨‍🌾 Monitoring Ketenagakerjaan")
        
        # Pilihan indikator ketenagakerjaan
        employment_indicator = st.sidebar.selectbox(
            "Pilih Indikator:",
            ["NTP (Nilai Tukar Petani)", "Persentase Pekerja Pertanian"]
        )
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"🗺️ Peta {employment_indicator}")
            if "NTP" in employment_indicator:
                emp_map = create_employment_map(df, 'NTP')
            else:
                emp_map = create_employment_map(df, 'Agricultural Workers')
            st_folium(emp_map, width=600, height=500)
        
        with col2:
            st.subheader("📊 Statistik Ketenagakerjaan")
            
            if "NTP" in employment_indicator:
                # Bar chart NTP
                fig_bar = px.bar(
                    df.sort_values('ntp'),
                    x='ntp',
                    y='province',
                    orientation='h',
                    title="NTP per Provinsi",
                    color='ntp',
                    color_continuous_scale='RdYlGn'
                )
                fig_bar.update_layout(height=400)
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # Interpretasi NTP
                st.info("NTP > 100: Kondisi petani membaik\nNTP < 100: Kondisi petani memburuk")
                
                # Statistik deskriptif
                st.metric("Rata-rata NTP", f"{df['ntp'].mean():.2f}")
                st.metric("Tertinggi", f"{df['ntp'].max():.2f}")
                st.metric("Terendah", f"{df['ntp'].min():.2f}")
            else:
                # Bar chart Agricultural Workers
                fig_bar = px.bar(
                    df.sort_values('agri_workers_percentage'),
                    x='agri_workers_percentage',
                    y='province',
                    orientation='h',
                    title="Pekerja Pertanian per Provinsi (%)",
                    color='agri_workers_percentage',
                    color_continuous_scale='Greens'
                )
                fig_bar.update_layout(height=400)
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # Statistik deskriptif
                st.metric("Rata-rata", f"{df['agri_workers_percentage'].mean():.2f}%")
                st.metric("Tertinggi", f"{df['agri_workers_percentage'].max():.2f}%")
                st.metric("Terendah", f"{df['agri_workers_percentage'].min():.2f}%")
        
        # Analisis korelasi NTP dan Pekerja Pertanian
        st.subheader("🔍 Analisis Hubungan NTP dan Pekerja Pertanian")
        
        fig_scatter = px.scatter(
            df,
            x='ntp',
            y='agri_workers_percentage',
            text='province',
            title="Hubungan NTP dan Persentase Pekerja Pertanian",
            labels={'ntp': 'Nilai Tukar Petani', 'agri_workers_percentage': 'Pekerja Pertanian (%)'}
        )
        fig_scatter.update_traces(textposition="top center")
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Tabel detail ketenagakerjaan
        st.subheader("📋 Detail Data Ketenagakerjaan")
        employment_detail = df[['province', 'ntp', 'agri_workers_percentage']].copy()
        employment_detail.columns = ['Provinsi', 'NTP', 'Pekerja Pertanian (%)']
        st.dataframe(employment_detail, use_container_width=True, hide_index=True)
    
    elif monitoring_type == "📈 Analisis Trend":
        st.header("📈 Analisis Trend Temporal")
        
        # Pilihan provinsi untuk analisis trend
        selected_provinces = st.sidebar.multiselect(
            "Pilih Provinsi:",
            df['province'].tolist(),
            default=df['province'].tolist()[:3]
        )
        
        if not selected_provinces:
            st.warning("Silakan pilih minimal satu provinsi untuk analisis trend.")
            return
        
        # Filter data berdasarkan provinsi yang dipilih
        filtered_ts = time_series_df[time_series_df['province'].isin(selected_provinces)]
        
        # Pilihan indikator untuk trend
        trend_indicator = st.sidebar.selectbox(
            "Pilih Indikator Trend:",
            ["CO Level", "NO2 Level", "CH4 Level", "PoU Trend", "NTP Trend"]
        )
        
        st.subheader(f"📊 Trend {trend_indicator} - 30 Hari Terakhir")
        
        # Membuat grafik trend
        if trend_indicator == "CO Level":
            fig_trend = px.line(
                filtered_ts,
                x='date',
                y='co_trend',
                color='province',
                title="Trend Konsentrasi CO (mg/m³)",
                labels={'co_trend': 'CO (mg/m³)', 'date': 'Tanggal'}
            )
        elif trend_indicator == "NO2 Level":
            fig_trend = px.line(
                filtered_ts,
                x='date',
                y='no2_trend',
                color='province',
                title="Trend Konsentrasi NO2 (µg/m³)",
                labels={'no2_trend': 'NO2 (µg/m³)', 'date': 'Tanggal'}
            )
        elif trend_indicator == "CH4 Level":
            fig_trend = px.line(
                filtered_ts,
                x='date',
                y='ch4_trend',
                color='province',
                title="Trend Konsentrasi CH4 (ppm)",
                labels={'ch4_trend': 'CH4 (ppm)', 'date': 'Tanggal'}
            )
        elif trend_indicator == "PoU Trend":
            fig_trend = px.line(
                filtered_ts,
                x='date',
                y='pou_trend',
                color='province',
                title="Trend PoU (%)",
                labels={'pou_trend': 'PoU (%)', 'date': 'Tanggal'}
            )
        else:  # NTP Trend
            fig_trend = px.line(
                filtered_ts,
                x='date',
                y='ntp_trend',
                color='province',
                title="Trend NTP",
                labels={'ntp_trend': 'NTP', 'date': 'Tanggal'}
            )
            # Tambahkan garis referensi pada 100 untuk NTP
            fig_trend.add_hline(y=100, line_dash="dash", line_color="red", 
                              annotation_text="NTP = 100 (Break Even)")
        
        fig_trend.update_layout(height=500)
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Statistik trend
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Statistik Trend Terkini")
            
            for province in selected_provinces:
                prov_data = filtered_ts[filtered_ts['province'] == province].iloc[-1]  # Data terbaru
                
                with st.expander(f"📍 {province}"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("CO", f"{prov_data['co_trend']:.3f} mg/m³")
                        st.metric("NO2", f"{prov_data['no2_trend']:.1f} µg/m³")
                        st.metric("CH4", f"{prov_data['ch4_trend']:.3f} ppm")
                    with col_b:
                        st.metric("PoU", f"{prov_data['pou_trend']:.2f}%")
                        st.metric("NTP", f"{prov_data['ntp_trend']:.2f}")
        
        with col2:
            st.subheader("📈 Analisis Perubahan")
            
            # Hitung perubahan dari awal ke akhir periode
            trend_changes = []
            for province in selected_provinces:
                prov_ts = filtered_ts[filtered_ts['province'] == province].sort_values('date')
                if len(prov_ts) >= 2:
                    first_day = prov_ts.iloc[0]
                    last_day = prov_ts.iloc[-1]
                    
                    if trend_indicator == "CO Level":
                        change = ((last_day['co_trend'] - first_day['co_trend']) / first_day['co_trend']) * 100
                        unit = "mg/m³"
                    elif trend_indicator == "NO2 Level":
                        change = ((last_day['no2_trend'] - first_day['no2_trend']) / first_day['no2_trend']) * 100
                        unit = "µg/m³"
                    elif trend_indicator == "CH4 Level":
                        change = ((last_day['ch4_trend'] - first_day['ch4_trend']) / first_day['ch4_trend']) * 100
                        unit = "ppm"
                    elif trend_indicator == "PoU Trend":
                        change = ((last_day['pou_trend'] - first_day['pou_trend']) / first_day['pou_trend']) * 100
                        unit = "%"
                    else:  # NTP Trend
                        change = ((last_day['ntp_trend'] - first_day['ntp_trend']) / first_day['ntp_trend']) * 100
                        unit = ""
                    
                    trend_changes.append({
                        'province': province,
                        'change_percent': change,
                        'trend': "📈 Naik" if change > 0 else "📉 Turun" if change < 0 else "➡️ Stabil"
                    })
            
            if trend_changes:
                trend_df = pd.DataFrame(trend_changes)
                for _, row in trend_df.iterrows():
                    color = "normal"
                    if row['change_percent'] > 5:
                        color = "normal"  # Bisa disesuaikan dengan warna yang diinginkan
                    elif row['change_percent'] < -5:
                        color = "inverse"
                    
                    st.metric(
                        row['province'],
                        f"{row['change_percent']:.1f}%",
                        delta=f"{row['trend']}"
                    )
        
        # Heatmap korelasi indikator
        st.subheader("🔥 Heatmap Korelasi Antar Indikator")
        
        # Aggregate data untuk korelasi
        correlation_data = []
        for province in selected_provinces:
            prov_ts = filtered_ts[filtered_ts['province'] == province]
            if len(prov_ts) > 0:
                avg_data = {
                    'province': province,
                    'CO': prov_ts['co_trend'].mean(),
                    'NO2': prov_ts['no2_trend'].mean(),
                    'CH4': prov_ts['ch4_trend'].mean(),
                    'PoU': prov_ts['pou_trend'].mean(),
                    'NTP': prov_ts['ntp_trend'].mean()
                }
                correlation_data.append(avg_data)
        
        if correlation_data:
            corr_df = pd.DataFrame(correlation_data).set_index('province')
            correlation_matrix = corr_df.corr()
            
            fig_heatmap = px.imshow(
                correlation_matrix,
                title="Korelasi Antar Indikator",
                color_continuous_scale='RdBu',
                aspect='auto'
            )
            fig_heatmap.update_layout(height=400)
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Tabel summary trend
        st.subheader("📋 Summary Data Trend Terkini")
        if correlation_data:
            summary_trend_df = pd.DataFrame(correlation_data)
            summary_trend_df.columns = ['Provinsi', 'CO (mg/m³)', 'NO2 (µg/m³)', 'CH4 (ppm)', 'PoU (%)', 'NTP']
            st.dataframe(summary_trend_df, use_container_width=True, hide_index=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>Dashboard Monitoring Indikator Pulau Sumatera | 
        Data: Simulasi untuk tujuan demonstrasi | 
        Dikembangkan dengan Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
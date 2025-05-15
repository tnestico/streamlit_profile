import streamlit as st
import requests
import polars as pl
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import io
import base64
import tempfile
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


SEASON = 2025




@st.cache_data(show_spinner=False)
def fetch_batter_data(season=SEASON):
    url = f"https://bdfed.stitch.mlbinfra.com/bdfed/stats/player?&env=prod&season={season}&sportId=1&stats=season&group=hitting&gameType=R&limit=1000000&offset=0"
    data = requests.get(url).json()["stats"]
    df = pl.DataFrame({
        "player_id": [x["playerId"] for x in data],
        "name": [x["playerFullName"] for x in data]
    }).unique().drop_nulls(subset=["player_id"]).sort("name")
    return df

@st.cache_data(show_spinner=False)
def fetch_pitcher_data(season=SEASON):
    url = f"https://bdfed.stitch.mlbinfra.com/bdfed/stats/player?&env=prod&season={season}&sportId=1&stats=season&group=pitching&gameType=R&limit=1000000&offset=0"
    data = requests.get(url).json()["stats"]
    df = pl.DataFrame({
        "player_id": [x["playerId"] for x in data],
        "name": [x["playerFullName"] for x in data]
    }).unique().drop_nulls(subset=["player_id"]).sort("name")
    return df

from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import shutil

def get_chromedriver_path():
    path = shutil.which("chromedriver")
    if path is None:
        raise FileNotFoundError("Chromedriver executable not found in PATH.")
    return path

def get_driver(proxy: str = None, socksStr: str = None) -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    # Your custom window size for mobile viewport
    options.add_argument("--window-size=400,800")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-features=NetworkService")
    options.add_argument("--disable-features=VizDisplayCompositor")
    # Mobile emulation for Pixel 2
    mobile_emulation = { "deviceName": "Pixel 2" }
    options.add_experimental_option("mobileEmulation", mobile_emulation)

    if proxy and socksStr:
        options.add_argument(f"--proxy-server={socksStr}://{proxy}")

    chromedriver_path = get_chromedriver_path()
    service = Service(executable_path=chromedriver_path)

    driver = webdriver.Chrome(service=service, options=options)
    return driver



def take_mobile_screenshot(mlb_player_id):

    
    # driver = get_driver()
    print('DRIVER')
    driver = get_driver(proxy=None, socksStr="socks5")  # or proxy=None
    
    print('DRIVER SECURED')
    url = f"https://www.mlb.com/player/{mlb_player_id}"
    driver.get(url)
    print('Page Loaded')
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".player-name, h1, .player-profile-name"))
        )
    except Exception as e:
        st.warning(f"Timeout or error loading page: {e}")

    driver.execute_script("""
        // Remove typical cookie banners
        const selectors = [
            '[class*="cookie"]',
            '[id*="cookie"]',
            'iframe[src*="consent"]',
            '[role="dialog"]',
            'div[class*="banner"]'
        ];
        for (let sel of selectors) {
            const el = document.querySelector(sel);
            if (el) el.remove();
        }

        // Remove specific buttons by class
        const btns = document.querySelectorAll(
            '.p-button__button.p-button__button--regular.p-button__button--secondary'
        );
        btns.forEach(btn => btn.remove());

        // Also try hiding any fixed footers
        const all = document.querySelectorAll('*');
        all.forEach(el => {
            const style = getComputedStyle(el);
            if (style.position === 'fixed' && style.bottom === '0px') {
                el.style.display = 'none';
            }
        });
    """)
    WebDriverWait(driver, 2).until(lambda d: True)

    png = driver.get_screenshot_as_png()
    driver.quit()
    print('Done')
    try:
        os.rmdir(user_data_dir)
    except:
        pass

    image = Image.open(io.BytesIO(png))
    cropped = image.crop((0, 300, image.width, 1430))
    driver.quit()
    return cropped

st.title("MLB Player Mobile Screenshot")

tabs = st.tabs(["Batters", "Pitchers"])

with tabs[0]:
    batter_df = fetch_batter_data()
    batter_name_to_id = dict(zip(batter_df["name"], batter_df["player_id"]))
    selected_batter = st.selectbox("Select a Batter:", list(batter_name_to_id.keys()))
    if st.button("Generate Batter Screenshot"):
        with st.spinner("Taking screenshot..."):
            print('MADE IT HERE')
            img = take_mobile_screenshot(batter_name_to_id[selected_batter])
            st.image(img, use_column_width=True)

with tabs[1]:
    pitcher_df = fetch_pitcher_data()
    pitcher_name_to_id = dict(zip(pitcher_df["name"], pitcher_df["player_id"]))
    selected_pitcher = st.selectbox("Select a Pitcher:", list(pitcher_name_to_id.keys()))
    if st.button("Generate Pitcher Screenshot"):
        with st.spinner("Taking screenshot..."):
            img = take_mobile_screenshot(pitcher_name_to_id[selected_pitcher])
            st.image(img, use_column_width=True)

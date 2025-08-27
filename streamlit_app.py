# streamlit_app.py
import streamlit as st
import xarray as xr
import datetime
import plotly.express as px
from streamlit_folium import st_folium
import folium
import numpy as np

# NOAA OISST API
BASE_URL = "https://psl.noaa.gov/thredds/dodsC/Datasets/noaa.oisst.v2.highres/sst.day.mean.{year}.nc"

st.set_page_config(page_title="바다 온도 & 환경오염 사례", layout="wide")
st.title("🌊 바다 온도와 환경오염 사례 탐색기")

# --- 날짜 선택 ---
default_date = datetime.date.today() - datetime.timedelta(days=2)
selected_date = st.sidebar.date_input(
    "날짜를 선택하세요",
    value=default_date,
    min_value=datetime.date(1981, 9, 1),
    max_value=default_date
)

# --- 데이터 불러오기 함수 ---
@st.cache_data
def load_data(date):
    """
    선택한 날짜의 전세계 해수면 온도(SST) 데이터를 로드
    """
    year = date.year
    url = BASE_URL.format(year=year)
    date_str = date.strftime("%Y-%m-%d")

    try:
        ds = xr.open_dataset(url)
        da = ds["sst"].sel(time=date_str).squeeze()
        return da
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return None

# --- 현재 SST 데이터 로드 ---
with st.spinner(f"{selected_date} 데이터 불러오는 중..."):
    sst_now = load_data(selected_date)
    if sst_now is None:
        st.stop()

# --- 세계 해수면 온도 지도 시각화 (Plotly) ---
st.subheader(f"📌 {selected_date} 세계 해수면 온도 지도")
fig = px.imshow(
    sst_now,
    origin="lower",
    labels={"color": "°C"},
    color_continuous_scale="RdBu_r",
    title=f"Sea Surface Temperature {selected_date}"
)
fig.update_layout(
    dragmode="zoom",
    coloraxis_colorbar=dict(title="온도 (°C)")
)
st.plotly_chart(fig, use_container_width=True)

# --- 클릭 가능한 지도 (Folium) ---
st.subheader("🗺️ 바다 위치 선택 (클릭해서 좌표 얻기)")
m = folium.Map(location=[20, 140], zoom_start=2)
map_data = st_folium(m, width=700, height=450)

lat, lon = None, None
if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]
    st.success(f"선택한 좌표: 위도 {lat:.2f}, 경도 {lon:.2f}")

# --- 환경오염 사례 데이터 (부가설명 포함) ---
pollution_cases = {
    "태평양": [
        ("태평양 거대 쓰레기 지대", "https://www.nationalgeographic.com/environment/article/great-pacific-garbage-patch",
         "북태평양 환류 내부에 위치하며, 플라스틱 폐기물과 어망이 모여 거대한 섬을 이루고 있습니다. 해양 생물의 질식과 섭취로 인한 생태계 교란의 주범이 됩니다."),
        ("일본 후쿠시마 원전 오염수 방출 논란", "https://www.bbc.com/news/world-asia-66503073",
         "2011년 동일본 대지진으로 손상된 원전의 오염수를 정화하여 태평양에 방류하면서 안전성에 대한 논란이 지속되고 있습니다. 방사능 물질이 해양 생태계에 미칠 잠재적 영향에 대한 우려가 제기됩니다."),
        ("북태평양 어류 미세플라스틱 검출 증가", "https://www.nature.com/articles/s41598-020-64465-9",
         "플라스틱 쓰레기가 미세플라스틱으로 분해되어 먹이사슬에 침투하고 있습니다. 이는 해양 생물뿐만 아니라 어류를 섭취하는 인간의 건강까지 위협합니다."),
        ("적도 부근 산호초 백화현상", "https://www.noaa.gov/education/resource-collections/ocean-coasts/coral-reef-bleaching",
         "수온 상승으로 인해 산호가 공생하는 조류를 내보내며 하얗게 변하는 현상입니다. 산호초 생태계는 수많은 해양 생물의 서식지이므로, 이 현상은 해양 생물 다양성을 크게 훼손합니다."),
        ("알래스카 엑슨발데즈 기름 유출", "https://www.history.com/topics/1980s/exxon-valdez-oil-spill",
         "1989년 알래스카에서 발생한 대규모 원유 유출 사고입니다. 이는 해양 동물 수십만 마리를 죽게 하고 해안가 생태계를 파괴하여 장기적인 환경 오염 문제를 야기했습니다.")
    ],
    "인도양": [
        ("모리셔스 기름 유출 사고(2020)", "https://www.unep.org/news-and-stories/story/mauritius-oil-spill",
         "2020년 일본 화물선 '와카시오호'의 좌초로 연료유가 대량 유출되었습니다. 이 사고는 모리셔스의 아름다운 산호초와 해양 생태계에 치명적인 피해를 입혔습니다."),
        ("인도양 산호초 대규모 백화", "https://www.nature.com/articles/s41558-019-0595-7",
         "기후변화로 인한 수온 상승으로 인도양의 산호초들이 대규모로 백화되고 있습니다. 이는 산호초에 의존하는 수많은 해양 생물들에게 심각한 위협이 됩니다."),
        ("소말리아 해안 불법 폐기물 투기", "https://www.theguardian.com/environment/2005/jul/18/waste.pollution",
         "내전으로 인해 정부 부재 상태인 소말리아 해안에 서구 기업들이 독성 폐기물을 불법적으로 버리는 사례가 많았습니다. 이로 인해 해안 생태계가 심각하게 오염되고 있습니다."),
        ("플라스틱 쓰레기 축적", "https://www.sciencedirect.com/science/article/pii/S0025326X18306812",
         "인도양은 인구 밀도가 높은 지역의 영향을 받아 플라스틱 오염이 심각한 수준입니다. 해류를 따라 모인 쓰레기는 해양 생물에게 직접적인 위협이 됩니다."),
        ("해양 생태계 어종 감소", "https://www.fao.org/state-of-fisheries-aquaculture",
         "불법, 비보고, 비규제 어업(IUU Fishing)이 인도양에서 빈번하게 일어나고 있습니다. 이는 어족 자원을 급격히 감소시켜 생태계의 균형을 무너뜨리고 있습니다.")
    ],
    "대서양": [
        ("대서양 거대 쓰레기 지대", "https://www.nationalgeographic.com/environment/article/north-atlantic-garbage-patch",
         "북대서양 환류를 따라 형성된 또 다른 거대 쓰레기 지대입니다. 유럽과 북미에서 흘러나온 폐기물들이 모여 미세플라스틱 오염을 가속화하고 있습니다."),
        ("멕시코만 딥워터 호라이즌 기름 유출", "https://www.britannica.com/event/Deepwater-Horizon-oil-spill-of-2010",
         "2010년 멕시코만에서 발생한 역사상 최악의 해양 기름 유출 사고입니다. 막대한 양의 원유가 바다로 흘러나와 해양 생물을 죽이고 장기적인 오염을 야기했습니다."),
        ("북대서양 어류 개체수 감소", "https://www.pewtrusts.org/en/research-and-analysis/articles/2016/11/02/atlantic-fish-stocks-need-better-management",
         "과도한 어업 활동과 해양 오염으로 인해 대서양의 어종 자원이 급격히 줄어들고 있습니다. 이는 수산업에 큰 타격을 주고 해양 생태계의 먹이사슬을 교란합니다."),
        ("북해의 산업 오염", "https://www.greenpeace.org/international/press-release/4255/north-sea-pollution-crisis-calls-for-urgent-action/",
         "북해는 유럽의 주요 산업 지역에 인접해 있어 산업 폐기물과 화학 물질로 인한 오염이 심각합니다. 해양 생물의 건강과 인간의 식량 안전에 위협을 가하고 있습니다."),
        ("지중해 연안 미세플라스틱 오염", "https://www.ocean.org/insights-and-solutions/solutions/plastic-pollution-mediterranean-sea",
         "지중해는 해양 쓰레기, 특히 미세플라스틱 오염이 세계에서 가장 심각한 바다 중 하나입니다. 관광 산업과 항만 활동이 활발한 만큼 해양 오염도 심각합니다.")
    ],
    "남극해": [
        ("남극 대륙의 오존층 파괴", "https://www.nasa.gov/feature/goddard/2018/nasa-study-shows-first-direct-evidence-of-ozone-hole-recovery-due-to-cfc-bans",
         "남극 상공의 오존층이 파괴되면서 해양에 도달하는 자외선이 증가했습니다. 이는 해양 플랑크톤의 광합성을 방해하여 해양 생태계의 기초 생산력을 저하시킵니다."),
        ("빙하 해빙과 해수면 상승", "https://climate.nasa.gov/vital-signs/ice-sheets/",
         "지구 온난화로 남극의 빙하가 빠르게 녹으면서 전 세계 해수면이 상승하고 있습니다. 이는 해안 도시와 생태계에 직접적인 위협을 가하고 있습니다."),
        ("크릴 새우 개체수 감소", "https://www.nationalgeographic.com/animals/article/krill-antarctic-warming",
         "기온 상승으로 크릴 새우의 주요 서식지인 해빙이 줄어들고 있습니다. 크릴 새우는 남극 해양 생태계 먹이사슬의 핵심이므로, 그 감소는 펭귄과 고래 등 상위 포식자들에게 치명적입니다."),
        ("남극해 플라스틱 오염", "https://www.bas.ac.uk/media/antarctic-plastics/",
         "남극해는 다른 바다에 비해 오염이 적지만, 연구 기지와 관광 활동 등으로 인해 플라스틱 쓰레기가 발견되고 있습니다. 극지방의 혹독한 환경은 오염 물질의 분해를 더욱 어렵게 합니다."),
        ("해양 생물 종 분포 변화", "https://www.nature.com/articles/s41559-021-01607-x",
         "기온 변화에 따라 남극 해양 생물들의 서식지가 북쪽으로 이동하고 있습니다. 이는 생태계의 균형을 깨뜨리고 종 간의 새로운 경쟁을 유발합니다.")
    ],
    "북극해": [
        ("북극의 급격한 해빙 가속화", "https://climate.nasa.gov/vital-signs/arctic-sea-ice/",
         "지구 온난화로 북극의 해빙이 빠르게 녹아 북극곰과 같은 해빙에 의존하는 동물들의 서식지를 파괴하고 있습니다. 이는 또한 지구 온난화를 더욱 가속화하는 악순환을 만듭니다."),
        ("북극 항로 개발로 인한 오염", "https://www.unep.org/news-and-stories/story/risks-and-rewards-new-arctic-shipping-routes",
         "빙하가 녹아 북극 항로가 열리면서 선박 운항이 증가하고 있습니다. 이는 기름 유출 사고 위험을 높이고 소음 공해, 해양 생태계 교란 등을 초래합니다."),
        ("영구동토층 해빙으로 인한 메탄 방출", "https://www.nrdc.org/stories/permafrost-thaw",
         "북극의 영구동토층이 녹으면서 내부에 갇혀 있던 막대한 양의 메탄가스가 대기 중으로 방출되고 있습니다. 메탄은 이산화탄소보다 강력한 온실가스여서 기후변화를 더욱 심화시킵니다."),
        ("북극 오염 물질 축적", "https://www.arctic-council.org/exploring-the-arctic/environment/contaminants/",
         "전 세계의 오염 물질이 해류와 대기 순환을 통해 북극해로 운반되어 축적됩니다. 이러한 오염은 북극 생물들의 체내에 쌓여 먹이사슬을 통해 확산됩니다."),
        ("북극 생물 서식지 변화", "https://www.wwf.ca/arctic/species/",
         "수온과 환경 변화에 따라 북극 해양 생물들이 새로운 환경에 적응하거나 서식지를 잃고 있습니다. 이는 생물 다양성을 감소시키고 생태계의 불균형을 초래합니다.")
    ]
}

def find_region(lat, lon):
    """클릭한 좌표가 속한 5대양을 반환"""
    if -20 <= lat <= 60 and 120 <= lon <= 240:
        return "태평양"
    elif -40 <= lat <= 30 and 40 <= lon <= 120:
        return "인도양"
    elif 10 <= lat <= 60 and -80 <= lon <= 10:
        return "대서양"
    elif -90 <= lat <= -60:
        return "남극해"
    elif 60 <= lat <= 90:
        return "북극해"
    else:
        return None

# --- 결과 출력 ---
if lat and lon:
    region = find_region(lat, lon)
    if region and region in pollution_cases:
        st.markdown(f"### 🌍 선택한 지역: **{region}** 환경오염 사례")
        for i, (case, link, desc) in enumerate(pollution_cases[region][:5], 1):
            with st.expander(f"**{i}. {case}**"):
                st.write(desc)
                st.markdown(f"🔗 [출처 보러가기]({link})")
    else:
        st.warning("이 지역에 대한 사례 데이터가 준비되지 않았습니다. 다른 지역을 선택해 주세요.")

    # --- 10년 전과 현재 해수면 온도 비교 ---
    past_date = selected_date.replace(year=selected_date.year - 10)
    with st.spinner(f"{past_date} 데이터 불러오는 중..."):
        try:
            now_temp_val = sst_now.sel(lat=lat, lon=lon, method="nearest").values
            sst_past = load_data(past_date)
            past_temp_val = sst_past.sel(lat=lat, lon=lon, method="nearest").values

            if np.isnan(now_temp_val) or np.isnan(past_temp_val):
                st.warning("선택한 위치는 육지입니다. 바다를 클릭해 주세요.")
            else:
                now_temp = float(now_temp_val)
                past_temp = float(past_temp_val)
                diff = now_temp - past_temp

                st.markdown("---")
                st.markdown("### 🌡️ 10년 전과 현재의 해수면 온도 비교")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(label=f"**10년 전** ({past_date.year}년)", value=f"{past_temp:.2f} °C")
                with col2:
                    st.metric(label=f"**현재** ({selected_date.year}년)", value=f"{now_temp:.2f} °C")
                with col3:
                    st.metric(label="**온도 변화**", value=f"{diff:+.2f} °C", delta_color="inverse")
            
        except Exception as e:
            st.error(f"10년 전 데이터 불러오기 실패: {e}")

    # --- 마지막 경각심 메시지 ---
    st.markdown("---")
    st.markdown("### ✨ 우리의 바다, 함께 지켜나가요")

    try:
        current_year = datetime.date.today().year
        avg_temps = []
        
        for year_offset in range(5):
            date_to_check = datetime.date(current_year - year_offset, 1, 1)
            data = load_data(date_to_check)
            if data is not None:
                avg_temp = float(data.mean().values)
                avg_temps.append(avg_temp)

        five_year_avg = np.mean(avg_temps) if avg_temps else None

        st.markdown("""
        혹시 알고 계셨나요? 
        안타깝게도 해양 오염은 아주 오래전부터 계속되어 왔어요. 단순한 일회성 문제가 아니라, 수십 년에 걸쳐 우리 바다를 병들게 하고 있습니다.

        지난 5년간의 **세계 해수면 온도는 평균 {:.2f}°C**를 기록했는데요. 지구 온난화의 심각성을 보여주듯, 이 수치는 꾸준히 상승하고 있어요. 우리의 눈에 보이지 않는 바다 깊은 곳에서는 플라스틱 쓰레기와 화학물질이 쌓이고, 생태계는 점점 무너지고 있답니다.

        이 앱에서 보신 것처럼, 바다는 우리가 생각하는 것보다 훨씬 더 심각한 위기에 처해 있습니다. 바다 생물들의 삶의 터전을 보호하고, 우리의 미래를 지키기 위해 이제는 더 이상 미룰 수 없는 때입니다. 우리의 작은 노력 하나하나가 모이면, 우리 바다를 다시 되살릴 수 있을 거예요. 함께 행동해 봐요! 🌊
        """.format(five_year_avg))

    except Exception as e:
        st.error(f"평균 해수면 온도 데이터를 불러오는 중 오류가 발생했습니다: {e}")
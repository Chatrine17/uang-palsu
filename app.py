import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------------
# Konfigurasi halaman
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard UPUR - KPw BI Pematang Siantar",
    page_icon="💵",
    layout="wide",
)

PRIMARY = "#c0392b"
SECONDARY = "#2c3e50"
ACCENT = "#2980b9"


@st.cache_data
def load_data():
    yearly = pd.read_csv("data/yearly_totals.csv")
    emisi = pd.read_csv("data/palsu_by_tahun_emisi.csv")
    emisi["TahunEmisi"] = emisi["TahunEmisi"].astype(str)
    return yearly, emisi


yearly, emisi = load_data()

# ----------------------------------------------------------------------------
# Sidebar - filter
# ----------------------------------------------------------------------------
st.sidebar.title("💵 UPUR Dashboard")
st.sidebar.caption("KPw Bank Indonesia Kota Pematang Siantar")

year_min, year_max = int(yearly["Year"].min()), int(yearly["Year"].max())
year_range = st.sidebar.slider(
    "Rentang Tahun",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max),
)

yearly_f = yearly[(yearly["Year"] >= year_range[0]) & (yearly["Year"] <= year_range[1])]
emisi_f = emisi[(emisi["Year"] >= year_range[0]) & (emisi["Year"] <= year_range[1])]

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Tentang data**\n\n"
    "Data UPUR (Uang Palsu & Uang Rusak) hasil temuan KPw BI Kota Pematang Siantar, "
    "periode 2018-2025. Kategori meliputi *Asli*, *Asli - Rusak*, *Palsu*, dan "
    "*Palsu - Menunggu Klasifikasi*. Breakdown tahun emisi tersedia mulai 2020."
)

# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------
st.title("Dashboard Temuan UPUR")
st.markdown("##### KPw Bank Indonesia Kota Pematang Siantar — 2018–2025")
st.markdown("---")

# ----------------------------------------------------------------------------
# KPI Cards
# ----------------------------------------------------------------------------
total_temuan = int(yearly_f["Grand_Total"].sum())
total_palsu = int(yearly_f["Palsu"].sum())
total_asli_rusak = int(yearly_f["Asli_Rusak"].sum())
tahun_tertinggi = int(yearly_f.loc[yearly_f["Grand_Total"].idxmax(), "Year"]) if len(yearly_f) else "-"

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Temuan", f"{total_temuan:,}".replace(",", "."))
c2.metric("Total Uang Palsu", f"{total_palsu:,}".replace(",", "."))
c3.metric("Total Asli - Rusak", f"{total_asli_rusak:,}".replace(",", "."))
c4.metric("Tahun Temuan Tertinggi", tahun_tertinggi)

st.markdown("---")

# ----------------------------------------------------------------------------
# Tabs: Overview & Drill-down
# ----------------------------------------------------------------------------
tab1, tab2 = st.tabs(["📊 Overview", "🔍 Drill-down per Tahun Emisi"])

with tab1:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Tren Total Temuan per Tahun")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=yearly_f["Year"], y=yearly_f["Grand_Total"],
            mode="lines+markers", name="Total Temuan",
            line=dict(color=PRIMARY, width=3), marker=dict(size=8),
        ))
        fig.update_layout(
            xaxis_title="Tahun", yaxis_title="Jumlah Lembar/Keping",
            hovermode="x unified", height=420,
            xaxis=dict(dtick=1),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Komposisi Kategori")
        comp = yearly_f[["Asli", "Asli_Rusak", "Palsu", "Palsu_Menunggu_Klasifikasi"]].sum()
        comp = comp[comp > 0]
        fig_pie = px.pie(
            values=comp.values, names=comp.index, hole=0.45,
            color_discrete_sequence=[ACCENT, "#27ae60", PRIMARY, "#f39c12"],
        )
        fig_pie.update_layout(height=420)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("Perbandingan Kategori per Tahun")
    melt = yearly_f.melt(
        id_vars="Year",
        value_vars=["Asli", "Asli_Rusak", "Palsu", "Palsu_Menunggu_Klasifikasi"],
        var_name="Kategori", value_name="Jumlah",
    )
    melt = melt[melt["Jumlah"] > 0]
    fig_bar = px.bar(
        melt, x="Year", y="Jumlah", color="Kategori", barmode="stack",
        color_discrete_map={
            "Asli": ACCENT, "Asli_Rusak": "#27ae60",
            "Palsu": PRIMARY, "Palsu_Menunggu_Klasifikasi": "#f39c12",
        },
    )
    fig_bar.update_layout(xaxis=dict(dtick=1), height=420)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("Tabel Ringkasan Tahunan")
    st.dataframe(yearly_f.set_index("Year"), use_container_width=True)

with tab2:
    st.subheader("Komposisi Uang Palsu berdasarkan Tahun Emisi")
    st.caption("Breakdown tahun emisi (desain uang) baru tersedia untuk data mulai 2020.")

    if emisi_f.empty:
        st.info("Tidak ada data tahun emisi pada rentang tahun yang dipilih.")
    else:
        fig_stack = px.bar(
            emisi_f, x="Year", y="Count", color="TahunEmisi",
            barmode="stack",
            labels={"Count": "Jumlah Lembar/Keping", "Year": "Tahun Temuan", "TahunEmisi": "Tahun Emisi"},
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_stack.update_layout(xaxis=dict(dtick=1), height=450)
        st.plotly_chart(fig_stack, use_container_width=True)

        colA, colB = st.columns(2)
        with colA:
            st.subheader("Total per Tahun Emisi (Akumulasi)")
            agg = emisi_f.groupby("TahunEmisi", as_index=False)["Count"].sum().sort_values("Count", ascending=False)
            fig_h = px.bar(
                agg, x="Count", y="TahunEmisi", orientation="h",
                color="Count", color_continuous_scale="Reds",
                labels={"Count": "Jumlah Lembar/Keping", "TahunEmisi": "Tahun Emisi"},
            )
            fig_h.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_h, use_container_width=True)

        with colB:
            st.subheader("Tabel Detail")
            st.dataframe(
                emisi_f.sort_values(["Year", "Count"], ascending=[True, False]).set_index("Year"),
                use_container_width=True, height=400,
            )

st.markdown("---")
st.caption("Dibuat untuk keperluan magang — KPw Bank Indonesia Kota Pematang Siantar.")

"""
Dashboard Analisis Temuan Uang Palsu
KPw Bank Indonesia Kota Pematang Siantar

Cara menjalankan:
    pip install streamlit plotly pandas openpyxl
    streamlit run app_uangpalsu.py

Pastikan file 'data_up.xlsx' berada di folder yang sama, atau sesuaikan DATA_PATH.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ──────────────────────────────────────────────────────────────────────────────
# Konfigurasi halaman
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Uang Palsu – KPw BI Pematang Siantar",
    page_icon="💵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# Warna & tema
# ──────────────────────────────────────────────────────────────────────────────
C_PRIMARY   = "#c0392b"   # merah BI
C_DARK      = "#2c3e50"   # hitam-navy
C_BLUE      = "#2980b9"   # biru aksen
C_GOLD      = "#f39c12"   # emas / warning
C_GREEN     = "#27ae60"   # hijau (Asli)
C_GRAY      = "#7f8c8d"

KLARIFIKASI_COLORS = {
    "Palsu":                       C_PRIMARY,
    "Palsu - Menunggu Klasifikasi": C_GOLD,
    "Asli":                        C_GREEN,
    "Asli - Rusak":                C_BLUE,
}

# ──────────────────────────────────────────────────────────────────────────────
# CSS kustom
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Card metrik */
.metric-card {
    background: #f8f9fa;
    border-left: 5px solid #c0392b;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 8px;
}
.metric-label {
    font-size: 0.78rem;
    font-weight: 600;
    color: #7f8c8d;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.metric-value {
    font-size: 1.9rem;
    font-weight: 700;
    color: #2c3e50;
    line-height: 1;
}
.metric-sub {
    font-size: 0.75rem;
    color: #95a5a6;
    margin-top: 4px;
}

/* Section title */
.section-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #2c3e50;
    border-bottom: 2px solid #c0392b;
    padding-bottom: 6px;
    margin-bottom: 16px;
}

/* Badge nomor seri */
.badge-seri {
    display: inline-block;
    background: #fdedec;
    color: #c0392b;
    font-size: 0.82rem;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 12px;
    font-family: monospace;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# Load data
# ──────────────────────────────────────────────────────────────────────────────
DATA_PATH = "data_up.xlsx"

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    df["TAHUN"]       = df["TAHUN"].astype(int)
    df["TAHUN EMISI"] = df["TAHUN EMISI"].astype(int)
    df["PECAHAN"]     = df["PECAHAN"].astype(int)
    df["JUMLAH LEMBAR"] = df["JUMLAH LEMBAR"].fillna(0).astype(int)
    df["NILAI NOMINAL"] = df["PECAHAN"] * df["JUMLAH LEMBAR"]
    df["HASIL KLARIFIKASI"] = df["HASIL KLARIFIKASI"].fillna("Tidak Diketahui")
    df["STATUS"]            = df["STATUS"].fillna("-")
    df["NOMOR SERI 1"]      = df["NOMOR SERI 1"].astype(str).str.strip()
    return df

try:
    df_raw = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(
        f"❌ File **{DATA_PATH}** tidak ditemukan. "
        "Pastikan file Excel berada di folder yang sama dengan `app.py`."
    )
    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# Sidebar — Filter
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/"
        "Logo_Bank_Indonesia.svg/200px-Logo_Bank_Indonesia.svg.png",
        width=140,
    )
    st.markdown("## 🔎 Filter Data")

    all_tahun  = sorted(df_raw["TAHUN"].unique())
    all_satker = sorted(df_raw["SATKER"].unique())
    all_pecahan = sorted(df_raw["PECAHAN"].unique())

    sel_tahun = st.multiselect(
        "Tahun",
        options=all_tahun,
        default=all_tahun,
        help="Pilih satu atau beberapa tahun",
    )
    sel_satker = st.multiselect(
        "SATKER",
        options=all_satker,
        default=all_satker,
    )
    sel_pecahan = st.multiselect(
        "Pecahan (Rp)",
        options=all_pecahan,
        default=all_pecahan,
        format_func=lambda x: f"Rp {x:,}".replace(",", "."),
    )

    st.markdown("---")
    st.markdown(
        "<small>Data UPUR (Uang Palsu & Uang Rusak)<br>"
        "**KPw BI Kota Pematang Siantar**<br>"
        "Periode 2018–2025</small>",
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────────────────────────────────────
# Filter data
# ──────────────────────────────────────────────────────────────────────────────
if not sel_tahun or not sel_satker or not sel_pecahan:
    st.warning("⚠️ Pilih minimal satu opsi untuk setiap filter.")
    st.stop()

df = df_raw[
    df_raw["TAHUN"].isin(sel_tahun) &
    df_raw["SATKER"].isin(sel_satker) &
    df_raw["PECAHAN"].isin(sel_pecahan)
].copy()

# ──────────────────────────────────────────────────────────────────────────────
# Header halaman
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='color:#c0392b; margin-bottom:0'>💵 Dashboard Analisis Temuan Uang Palsu</h1>"
    "<p style='color:#7f8c8d; margin-top:4px'>KPw Bank Indonesia Kota Pematang Siantar &nbsp;|&nbsp; "
    "Data menampilkan hasil filter yang dipilih</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ──────────────────────────────────────────────────────────────────────────────
# KPI Cards
# ──────────────────────────────────────────────────────────────────────────────
total_laporan    = len(df)
total_lembar     = int(df["JUMLAH LEMBAR"].sum())
total_nilai      = int(df["NILAI NOMINAL"].sum())
total_satker     = df["SATKER"].nunique()
total_seri_unik  = df["NOMOR SERI 1"].nunique()

def card(label, value, sub=""):
    return (
        f'<div class="metric-card">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        f'<div class="metric-sub">{sub}</div>'
        f'</div>'
    )

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(card("Total Laporan", f"{total_laporan:,}".replace(",", "."), "baris data"), unsafe_allow_html=True)
with c2:
    st.markdown(card("Total Lembar Uang", f"{total_lembar:,}".replace(",", "."), "lembar/keping"), unsafe_allow_html=True)
with c3:
    nilai_str = f"Rp {total_nilai:,}".replace(",", ".")
    st.markdown(card("Total Nilai Nominal", nilai_str, "pecahan × jumlah lembar"), unsafe_allow_html=True)
with c4:
    st.markdown(card("SATKER Terlibat", str(total_satker), "satuan kerja"), unsafe_allow_html=True)
with c5:
    st.markdown(card("Nomor Seri Unik", f"{total_seri_unik:,}".replace(",", "."), "dari total data"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# Tabs utama
# ──────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📊  Overview & Tren",
    "🔍  Analisis Nomor Seri",
    "📋  Data Mentah",
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — Overview & Tren
# ════════════════════════════════════════════════════════════════════════════
with tab1:

    # ── Baris 1: Line chart tren + Pie klarifikasi ──
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown('<div class="section-title">📈 Tren Temuan per Tahun</div>', unsafe_allow_html=True)

        tren = (
            df.groupby("TAHUN")
            .agg(Total_Laporan=("JUMLAH LEMBAR", "count"), Total_Lembar=("JUMLAH LEMBAR", "sum"))
            .reset_index()
        )

        fig_tren = go.Figure()
        fig_tren.add_trace(go.Scatter(
            x=tren["TAHUN"], y=tren["Total_Lembar"],
            name="Total Lembar", mode="lines+markers",
            line=dict(color=C_PRIMARY, width=3),
            marker=dict(size=9, color=C_PRIMARY, line=dict(color="white", width=2)),
            hovertemplate="<b>%{x}</b><br>Lembar: %{y}<extra></extra>",
        ))
        fig_tren.add_trace(go.Scatter(
            x=tren["TAHUN"], y=tren["Total_Laporan"],
            name="Jumlah Laporan", mode="lines+markers",
            line=dict(color=C_BLUE, width=2, dash="dot"),
            marker=dict(size=7, color=C_BLUE),
            hovertemplate="<b>%{x}</b><br>Laporan: %{y}<extra></extra>",
        ))
        fig_tren.update_layout(
            height=360, hovermode="x unified",
            xaxis=dict(dtick=1, title="Tahun"),
            yaxis=dict(title="Jumlah"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(t=10, b=40, l=40, r=20),
        )
        st.plotly_chart(fig_tren, use_container_width=True)

    with col_right:
        st.markdown('<div class="section-title">🥧 Proporsi Hasil Klarifikasi</div>', unsafe_allow_html=True)

        klarifikasi = (
            df.groupby("HASIL KLARIFIKASI")["JUMLAH LEMBAR"]
            .sum()
            .reset_index(name="Total Lembar")
        )

        fig_pie = px.pie(
            klarifikasi, values="Total Lembar", names="HASIL KLARIFIKASI",
            hole=0.48,
            color="HASIL KLARIFIKASI",
            color_discrete_map=KLARIFIKASI_COLORS,
        )
        fig_pie.update_traces(
            textposition="outside",
            textinfo="percent+label",
            pull=[0.04] * len(klarifikasi),
        )
        fig_pie.update_layout(
            height=360, showlegend=False,
            margin=dict(t=10, b=10, l=20, r=20),
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ── Baris 2: Bar chart pecahan + Stacked bar tahun emisi ──
    col2a, col2b = st.columns(2)

    with col2a:
        st.markdown('<div class="section-title">💰 Distribusi Pecahan Nominal</div>', unsafe_allow_html=True)

        pecahan_df = (
            df.groupby("PECAHAN")["JUMLAH LEMBAR"]
            .sum()
            .reset_index(name="Total Lembar")
            .sort_values("Total Lembar", ascending=False)
        )
        pecahan_df["Label"] = pecahan_df["PECAHAN"].apply(lambda x: f"Rp {x:,}".replace(",", "."))

        fig_bar = px.bar(
            pecahan_df, x="Label", y="Total Lembar",
            color="Total Lembar", color_continuous_scale="Reds",
            labels={"Label": "Pecahan", "Total Lembar": "Jumlah Lembar"},
            text="Total Lembar",
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_coloraxes(showscale=False)
        fig_bar.update_layout(
            height=350, margin=dict(t=10, b=50, l=40, r=20),
            xaxis_title="Pecahan", yaxis_title="Jumlah Lembar",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2b:
        st.markdown('<div class="section-title">🗓️ Uang Palsu berdasarkan Tahun Emisi</div>', unsafe_allow_html=True)

        palsu_df = df[df["HASIL KLARIFIKASI"].str.contains("Palsu", na=False)].copy()
        emisi_df = (
            palsu_df.groupby(["TAHUN", "TAHUN EMISI"])["JUMLAH LEMBAR"]
            .sum()
            .reset_index(name="Total Lembar")
        )
        emisi_df["TAHUN EMISI"] = emisi_df["TAHUN EMISI"].astype(str)

        fig_emisi = px.bar(
            emisi_df, x="TAHUN", y="Total Lembar", color="TAHUN EMISI",
            barmode="stack",
            color_discrete_sequence=px.colors.qualitative.Set2,
            labels={"Total Lembar": "Jumlah Lembar", "TAHUN": "Tahun Temuan", "TAHUN EMISI": "Tahun Emisi"},
        )
        fig_emisi.update_layout(
            height=350, margin=dict(t=10, b=50, l=40, r=20),
            xaxis=dict(dtick=1),
            legend=dict(title="Tahun Emisi", orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig_emisi, use_container_width=True)

    # ── Baris 3: Heatmap Tahun × Pecahan ──
    st.markdown('<div class="section-title">🗺️ Heatmap Temuan — Tahun × Pecahan</div>', unsafe_allow_html=True)

    heat_df = (
        df.groupby(["TAHUN", "PECAHAN"])["JUMLAH LEMBAR"]
        .sum()
        .reset_index(name="Total")
    )
    heat_pivot = heat_df.pivot(index="PECAHAN", columns="TAHUN", values="Total").fillna(0)
    heat_pivot.index = [f"Rp {p:,}".replace(",", ".") for p in heat_pivot.index]

    fig_heat = px.imshow(
        heat_pivot,
        color_continuous_scale="Reds",
        labels=dict(x="Tahun", y="Pecahan", color="Jumlah Lembar"),
        text_auto=True,
        aspect="auto",
    )
    fig_heat.update_layout(height=280, margin=dict(t=10, b=40, l=100, r=20))
    st.plotly_chart(fig_heat, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — Analisis Nomor Seri
# ════════════════════════════════════════════════════════════════════════════
with tab2:

    # ── Top 10 Nomor Seri (keseluruhan) ──
    st.markdown('<div class="section-title">🏆 Top 10 Nomor Seri Paling Banyak Muncul (Keseluruhan)</div>', unsafe_allow_html=True)

    top10_seri = (
        df.groupby("NOMOR SERI 1")
        .agg(
            Jumlah_Laporan=("NOMOR SERI 1", "count"),
            Total_Lembar=("JUMLAH LEMBAR", "sum"),
        )
        .reset_index()
        .sort_values("Total_Lembar", ascending=False)
        .head(10)
    )

    col_chart, col_table = st.columns([3, 2])

    with col_chart:
        fig_top10 = px.bar(
            top10_seri.sort_values("Total_Lembar"),
            x="Total_Lembar", y="NOMOR SERI 1", orientation="h",
            color="Total_Lembar",
            color_continuous_scale="Reds",
            labels={"Total_Lembar": "Total Lembar", "NOMOR SERI 1": "Nomor Seri"},
            text="Total_Lembar",
        )
        fig_top10.update_traces(textposition="outside")
        fig_top10.update_coloraxes(showscale=False)
        fig_top10.update_layout(
            height=380,
            margin=dict(t=10, b=20, l=10, r=40),
            yaxis=dict(tickfont=dict(family="monospace", size=11)),
        )
        st.plotly_chart(fig_top10, use_container_width=True)

    with col_table:
        st.dataframe(
            top10_seri.reset_index(drop=True)
            .rename(columns={
                "NOMOR SERI 1": "Nomor Seri",
                "Jumlah_Laporan": "Jumlah Laporan",
                "Total_Lembar": "Total Lembar",
            }),
            use_container_width=True,
            height=380,
            hide_index=True,
        )

    st.markdown("---")

    # ── Nomor Seri "Juara" per Tahun ──
    st.markdown(
        '<div class="section-title">🥇 Nomor Seri Terbanyak per Tahun (Juara Tahunan)</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Nomor seri yang paling banyak muncul berdasarkan total JUMLAH LEMBAR di setiap tahun. "
        "Berguna untuk melacak apakah ada satu lembar uang yang terus beredar lintas tahun."
    )

    # Groupby TAHUN + NOMOR SERI → ambil yang rank 1 per tahun
    seri_per_tahun = (
        df.groupby(["TAHUN", "NOMOR SERI 1"])
        .agg(
            Total_Lembar=("JUMLAH LEMBAR", "sum"),
            Jumlah_Laporan=("NOMOR SERI 1", "count"),
        )
        .reset_index()
    )

    seri_per_tahun["Rank"] = seri_per_tahun.groupby("TAHUN")["Total_Lembar"].rank(
        method="first", ascending=False
    ).astype(int)

    juara_tahun = (
        seri_per_tahun[seri_per_tahun["Rank"] == 1]
        .sort_values("TAHUN")
        .reset_index(drop=True)
    )

    # Tampilkan sebagai tabel interaktif bergaya card
    col_a, col_b = st.columns([2, 3])

    with col_a:
        display_juara = juara_tahun[["TAHUN", "NOMOR SERI 1", "Total_Lembar", "Jumlah_Laporan"]].rename(
            columns={
                "TAHUN": "Tahun",
                "NOMOR SERI 1": "Nomor Seri Juara",
                "Total_Lembar": "Total Lembar",
                "Jumlah_Laporan": "Muncul (Laporan)",
            }
        )
        st.dataframe(
            display_juara,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Tahun": st.column_config.NumberColumn(format="%d"),
                "Total Lembar": st.column_config.ProgressColumn(
                    min_value=0,
                    max_value=int(juara_tahun["Total_Lembar"].max()) + 1,
                    format="%d",
                ),
            },
        )

    with col_b:
        # Bar chart: nomor seri juara per tahun
        fig_juara = px.bar(
            juara_tahun,
            x="TAHUN", y="Total_Lembar",
            color="Total_Lembar",
            color_continuous_scale="Reds",
            text="NOMOR SERI 1",
            labels={"TAHUN": "Tahun", "Total_Lembar": "Total Lembar", "NOMOR SERI 1": "Nomor Seri"},
            hover_data={"NOMOR SERI 1": True, "Jumlah_Laporan": True},
        )
        fig_juara.update_traces(textposition="outside", textfont=dict(family="monospace", size=11))
        fig_juara.update_coloraxes(showscale=False)
        fig_juara.update_layout(
            height=380,
            margin=dict(t=30, b=40, l=40, r=20),
            xaxis=dict(dtick=1),
        )
        st.plotly_chart(fig_juara, use_container_width=True)

    st.markdown("---")

    # ── Drill-down: Riwayat satu nomor seri tertentu ──
    st.markdown('<div class="section-title">🔬 Drill-down: Riwayat Nomor Seri Tertentu</div>', unsafe_allow_html=True)

    all_seri = sorted(df["NOMOR SERI 1"].unique())
    # Default: nomor seri juara keseluruhan
    default_seri = top10_seri.iloc[0]["NOMOR SERI 1"] if len(top10_seri) else all_seri[0]
    idx_default  = all_seri.index(default_seri) if default_seri in all_seri else 0

    selected_seri = st.selectbox("Cari / pilih Nomor Seri:", options=all_seri, index=idx_default)

    detail = df[df["NOMOR SERI 1"] == selected_seri]

    d1, d2, d3 = st.columns(3)
    d1.metric("Total Laporan Ditemukan", len(detail))
    d2.metric("Total Lembar", int(detail["JUMLAH LEMBAR"].sum()))
    d3.metric(
        "Rentang Tahun",
        f"{detail['TAHUN'].min()} – {detail['TAHUN'].max()}" if len(detail) > 0 else "-"
    )

    st.dataframe(
        detail[["TAHUN", "PECAHAN", "JUMLAH LEMBAR", "TAHUN EMISI", "SATKER", "HASIL KLARIFIKASI", "STATUS"]]
        .sort_values("TAHUN")
        .reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
    )


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — Data Mentah
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown(
        f'<div class="section-title">📋 Data Lengkap &nbsp;'
        f'<span style="font-weight:400;font-size:0.85rem;color:{C_GRAY}">({len(df):,} baris)</span></div>'.replace(",", "."),
        unsafe_allow_html=True,
    )

    search_text = st.text_input("🔍 Cari nomor seri / satker:", "")
    if search_text:
        mask = (
            df["NOMOR SERI 1"].str.contains(search_text, case=False, na=False) |
            df["SATKER"].str.contains(search_text, case=False, na=False)
        )
        df_show = df[mask]
        st.caption(f"Ditemukan {len(df_show)} baris yang cocok.")
    else:
        df_show = df

    st.dataframe(
        df_show[[
            "TAHUN", "NOMOR SERI 1", "JUMLAH LEMBAR", "TAHUN EMISI",
            "PECAHAN", "SATKER", "HASIL KLARIFIKASI", "STATUS", "NILAI NOMINAL",
        ]].sort_values(["TAHUN", "NOMOR SERI 1"]).reset_index(drop=True),
        use_container_width=True,
        height=520,
        hide_index=True,
        column_config={
            "PECAHAN": st.column_config.NumberColumn(format="Rp %d"),
            "NILAI NOMINAL": st.column_config.NumberColumn(format="Rp %d"),
        },
    )

    # Tombol download CSV
    csv_bytes = df_show.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️  Download data sebagai CSV",
        data=csv_bytes,
        file_name="data_uang_palsu_filtered.csv",
        mime="text/csv",
    )

# ──────────────────────────────────────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<div style='text-align:center; color:{C_GRAY}; font-size:0.8rem'>"
    "Dashboard Analisis Temuan UPUR &nbsp;·&nbsp; "
    "KPw Bank Indonesia Kota Pematang Siantar &nbsp;·&nbsp; "
    "Dibuat dengan Streamlit & Plotly"
    "</div>",
    unsafe_allow_html=True,
)

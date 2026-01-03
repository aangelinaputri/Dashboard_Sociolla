import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =====================
# PAGE CONFIG
# =====================
st.set_page_config(
    page_title="Sociolla Brand Dashboard",
    layout="wide"
)

# =====================
# GLOBAL STYLE (CSS)
# =====================
st.markdown("""
<style>
body {
    background-color: #fffafc;
}
.block-container {
    padding-top: 2rem;
}
h1, h2, h3 {
    color: #7a2048;
}
.metric-container {
    background-color: #ffe4ec;
    border-radius: 16px;
    padding: 20px;
}
.chart-card {
    background-color: white;
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.05);
    margin-bottom: 30px;
}
</style>
""", unsafe_allow_html=True)

# =====================
# LOAD DATA
# =====================
@st.cache_data
def load_data():
    return pd.read_csv("data_clean.csv")

data = load_data()

# =====================
# HEADER
# =====================
st.title("💄 Sociolla Brand Performance Dashboard")
st.caption("Analisis brand berdasarkan rekomendasi, rating, dan perilaku repurchase pengguna")

# =====================
# SIDEBAR
# =====================
st.sidebar.header("🎛️ Filter Analisis")
min_repurchase = st.sidebar.slider(
    "Minimal total repurchase",
    min_value=0,
    max_value=int(
        (data['repurchase_yes_num_imputed_median'] +
         data['repurchase_no_num_imputed_median']).max()
    ),
    value=30
)
min_produk = st.sidebar.slider(
    "Minimal jumlah produk per brand",
    min_value=1,
    max_value=int(
        data.groupby('brand').size().max()
    ),
    value=2
)
min_rating = st.sidebar.slider(
    "Minimal rata-rata rating brand",
    min_value=1.0,
    max_value=5.0,
    value=1.0,
    step=0.1
)

# =====================
# DATA PREPARATION
# =====================
brand_rep_all = data.groupby('brand').agg({
    'repurchase_yes_num_imputed_median': 'sum',
    'repurchase_no_num_imputed_median': 'sum',
    'rating_imputed_median': 'mean',
    'number_of_recommendations_imputed_median': 'sum'
}).reset_index()

brand_count = (
    data.groupby('brand')
    .size()
    .reset_index(name='total_produk')
)

brand_rep_all = brand_rep_all.merge(brand_count, on='brand')

brand_rep_all['total_repurchase'] = (
    brand_rep_all['repurchase_yes_num_imputed_median'] +
    brand_rep_all['repurchase_no_num_imputed_median']
)

brand_rep_all['repurchase_rate'] = (
    brand_rep_all['repurchase_yes_num_imputed_median'] /
    brand_rep_all['total_repurchase']
)

brand_rep_all['repurchase_index'] = (
    brand_rep_all['repurchase_yes_num_imputed_median'] -
    brand_rep_all['repurchase_no_num_imputed_median']
) / brand_rep_all['total_repurchase']

brand_rep_filtered = brand_rep_all[
    (brand_rep_all['total_repurchase'] >= min_repurchase) &
    (brand_rep_all['total_produk'] >= min_produk) &
    (brand_rep_all['rating_imputed_median'] >= min_rating)
]


# =====================
# METRICS
# =====================
m1, m2, m3 = st.columns(3)

with m1:
    st.metric("💋 Total Brand", brand_rep_filtered.shape[0])

with m2:
    st.metric(
        "⭐ Rata-rata Rating",
        round(brand_rep_filtered['rating_imputed_median'].mean(), 2)
    )

with m3:
    st.metric(
        "🔁 Rata-rata Repurchase Rate",
        round(brand_rep_filtered['repurchase_rate'].mean(), 2)
    )

# =====================
# CHART STYLE
# =====================
sns.set_style("whitegrid")
palette_pink = sns.color_palette("pink", 15)

# =====================
# CHART 1
# =====================
st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.subheader("🔝 Brand dengan Rekomendasi Terbanyak")

top_rec = brand_rep_filtered.sort_values(
    'number_of_recommendations_imputed_median',
    ascending=False
).head(15)

fig, ax = plt.subplots(figsize=(14, 6))
sns.barplot(
    data=top_rec,
    x='brand',
    y='number_of_recommendations_imputed_median',
    palette=palette_pink,
    ax=ax
)
ax.set_xlabel("")
ax.set_ylabel("Jumlah Rekomendasi")
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.tight_layout()
st.pyplot(fig)
st.markdown("</div>", unsafe_allow_html=True)

# =====================
# CHART 2
# =====================
st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.subheader("⭐ Brand dengan Rating Tertinggi")

top_rating = brand_rep_filtered.sort_values(
    'rating_imputed_median',
    ascending=False
).head(15)

fig, ax = plt.subplots(figsize=(14, 6))
sns.barplot(
    data=top_rating,
    x='brand',
    y='rating_imputed_median',
    palette="Reds",
    ax=ax
)
ax.set_xlabel("")
ax.set_ylabel("Total Rating")
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.tight_layout()
st.pyplot(fig)
st.markdown("</div>", unsafe_allow_html=True)

# =====================
# CHART 3
# =====================
st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.subheader("🔁 Brand dengan Repurchase Rate Tertinggi")

top_rate = brand_rep_filtered.sort_values(
    'repurchase_rate',
    ascending=False
).head(15)

fig, ax = plt.subplots(figsize=(14, 6))
sns.barplot(
    data=top_rate,
    x='brand',
    y='repurchase_rate',
    palette="Blues",
    ax=ax
)
ax.set_xlabel("")
ax.set_ylabel("Repurchase Rate")
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.tight_layout()
st.pyplot(fig)
st.markdown("</div>", unsafe_allow_html=True)

# =====================
# CHART 4
# =====================
st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.subheader("⚠️ Brand dengan Repurchase Index Terendah")

low_index = brand_rep_filtered.sort_values(
    'repurchase_index'
).head(15)

fig, ax = plt.subplots(figsize=(14, 6))
sns.barplot(
    data=low_index,
    x='brand',
    y='repurchase_index',
    palette="coolwarm",
    ax=ax
)
ax.set_xlabel("")
ax.set_ylabel("Repurchase Index")
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.tight_layout()
st.pyplot(fig)
st.markdown("</div>", unsafe_allow_html=True)

"""
UIDAI Data Hackathon 2026 - Digital India Readiness Analysis
Generates all visualizations and exports results
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from math import pi
import warnings
import os

warnings.filterwarnings('ignore')

# Configuration
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.titleweight'] = 'bold'

print("="*70)
print("🏛️ UIDAI Data Hackathon 2026 - Digital India Readiness Analysis")
print("="*70)

# ============================================================
# 1. LOAD ALL DATASETS
# ============================================================
print("\n📁 Loading datasets...")

df_pds_metrics = pd.read_csv('data/RS_Session_254_AU_1356.csv')
df_ration_cards = pd.read_csv('data/RS_Session_246_AU2800.csv')
df_msme = pd.read_csv('data/RS_Session_254_AU_1540.1.ii_.csv')
df_mgnregs = pd.read_csv('data/RS_Session_260_AU_1546_C.csv')
df_aadhaar_gen = pd.read_csv('data/rs_session-241_au2785_1.1.csv')
df_deleted_cards = pd.read_csv('data/rs_session243_au721_1.1.csv')
df_transgender = pd.read_csv('data/rs_session_239_AU1492_1.1.csv')
df_seeding_alt = pd.read_csv('data/session_244_AU85_1.1_1.csv')

print(f"   ✅ PDS Metrics: {len(df_pds_metrics)} rows")
print(f"   ✅ Ration Cards: {len(df_ration_cards)} rows")
print(f"   ✅ MSME: {len(df_msme)} rows")
print(f"   ✅ MGNREGS: {len(df_mgnregs)} rows")
print(f"   ✅ Aadhaar Generation: {len(df_aadhaar_gen)} rows")

# ============================================================
# 2. DATA CLEANING & STANDARDIZATION
# ============================================================
print("\n🧹 Cleaning and standardizing data...")

def standardize_state_name(name):
    """Standardize state/UT names for merging"""
    if pd.isna(name) or str(name).strip() in ['Total', 'Grand Total']:
        return None
    
    name = str(name).strip()
    
    replacements = {
        'A & N Islands': 'Andaman and Nicobar Islands',
        'Andaman & Nicobar': 'Andaman and Nicobar Islands',
        'Andaman & Nicobar Island': 'Andaman and Nicobar Islands',
        'Dadra & Nagar Haveli': 'Dadra and Nagar Haveli',
        'Dadra & Nagar Haveli and Daman Diu': 'DNH and DD',
        'Dadra and Nagar Haveli and Daman and Diu': 'DNH and DD',
        'Daman & Diu': 'Daman and Diu',
        'Jammu & Kashmir': 'Jammu and Kashmir',
    }
    
    for old, new in replacements.items():
        if old.lower() == name.lower():
            return new
    
    return name

# Clean PDS Metrics
df_pds_clean = df_pds_metrics.copy()
df_pds_clean.columns = ['Sl_No', 'State', 'Ration_Card_Seeding', 'Beneficiary_Seeding', 'FPS_Automation']
df_pds_clean['State'] = df_pds_clean['State'].apply(standardize_state_name)
df_pds_clean = df_pds_clean[df_pds_clean['State'].notna()]
df_pds_clean['FPS_Automation'] = pd.to_numeric(df_pds_clean['FPS_Automation'], errors='coerce')

# Clean Aadhaar Generation
df_aadhaar_clean = df_aadhaar_gen.copy()
df_aadhaar_clean.columns = ['Sl_No', 'State', 'Population_2011', 'Aadhaar_Generated', 'Aadhaar_Percentage']
df_aadhaar_clean['State'] = df_aadhaar_clean['State'].apply(standardize_state_name)
df_aadhaar_clean = df_aadhaar_clean[df_aadhaar_clean['State'].notna()]

# Clean MGNREGS
df_mgnregs_clean = df_mgnregs.copy()
df_mgnregs_clean.columns = ['Sl_No', 'State', 'Active_Workers_Lakh', 'ABPS_Eligible_Lakh']
df_mgnregs_clean['State'] = df_mgnregs_clean['State'].apply(standardize_state_name)
df_mgnregs_clean = df_mgnregs_clean[df_mgnregs_clean['State'].notna()]
df_mgnregs_clean['Active_Workers_Lakh'] = pd.to_numeric(df_mgnregs_clean['Active_Workers_Lakh'], errors='coerce')
df_mgnregs_clean['ABPS_Eligible_Lakh'] = pd.to_numeric(df_mgnregs_clean['ABPS_Eligible_Lakh'], errors='coerce')
df_mgnregs_clean['ABPS_Coverage'] = (df_mgnregs_clean['ABPS_Eligible_Lakh'] / df_mgnregs_clean['Active_Workers_Lakh'] * 100).round(2)

# Clean MSME
df_msme_clean = df_msme.copy()
df_msme_clean = df_msme_clean.rename(columns={'State/UT': 'State'})
df_msme_clean['State'] = df_msme_clean['State'].apply(standardize_state_name)
df_msme_clean = df_msme_clean[df_msme_clean['State'].notna()]

print(f"   ✅ Cleaned datasets ready")

# ============================================================
# 3. CREATE MASTER DATASET
# ============================================================
print("\n🔗 Creating master dataset...")

master_df = df_aadhaar_clean[['State', 'Population_2011', 'Aadhaar_Generated', 'Aadhaar_Percentage']].copy()

master_df = master_df.merge(
    df_pds_clean[['State', 'Ration_Card_Seeding', 'Beneficiary_Seeding', 'FPS_Automation']], 
    on='State', how='left'
)

master_df = master_df.merge(
    df_mgnregs_clean[['State', 'Active_Workers_Lakh', 'ABPS_Eligible_Lakh', 'ABPS_Coverage']], 
    on='State', how='left'
)

master_df = master_df.merge(
    df_msme_clean[['State', 'Total']], 
    on='State', how='left'
)
master_df = master_df.rename(columns={'Total': 'Total_MSMEs'})

print(f"   ✅ Master dataset: {len(master_df)} states")

# ============================================================
# 4. CALCULATE DIGITAL READINESS INDEX
# ============================================================
print("\n📊 Calculating Digital Readiness Index...")

def normalize_score(series, higher_is_better=True):
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series([50] * len(series), index=series.index)
    if higher_is_better:
        return ((series - min_val) / (max_val - min_val) * 100).round(2)
    else:
        return ((max_val - series) / (max_val - min_val) * 100).round(2)

# Calculate scores
master_df['Aadhaar_Coverage_Capped'] = master_df['Aadhaar_Percentage'].clip(upper=100)
master_df['Score_Aadhaar_Coverage'] = normalize_score(master_df['Aadhaar_Coverage_Capped'])

master_df['PDS_Avg'] = master_df[['Ration_Card_Seeding', 'Beneficiary_Seeding', 'FPS_Automation']].mean(axis=1, skipna=True)
master_df['Score_PDS_Readiness'] = normalize_score(master_df['PDS_Avg'])

master_df['Score_MGNREGS_ABPS'] = normalize_score(master_df['ABPS_Coverage'].fillna(0))

master_df['MSME_Density'] = (master_df['Total_MSMEs'] / master_df['Population_2011'] * 10000).round(2)
master_df['Score_MSME_Density'] = normalize_score(master_df['MSME_Density'].fillna(0))

# Calculate composite index
WEIGHTS = {
    'Score_Aadhaar_Coverage': 0.20,
    'Score_PDS_Readiness': 0.35,
    'Score_MGNREGS_ABPS': 0.30,
    'Score_MSME_Density': 0.15
}

# Fill NaN scores with 0 before calculation
master_df['Score_Aadhaar_Coverage'] = master_df['Score_Aadhaar_Coverage'].fillna(0)
master_df['Score_PDS_Readiness'] = master_df['Score_PDS_Readiness'].fillna(0)
master_df['Score_MGNREGS_ABPS'] = master_df['Score_MGNREGS_ABPS'].fillna(0)
master_df['Score_MSME_Density'] = master_df['Score_MSME_Density'].fillna(0)

master_df['Digital_Readiness_Index'] = (
    master_df['Score_Aadhaar_Coverage'] * WEIGHTS['Score_Aadhaar_Coverage'] +
    master_df['Score_PDS_Readiness'] * WEIGHTS['Score_PDS_Readiness'] +
    master_df['Score_MGNREGS_ABPS'] * WEIGHTS['Score_MGNREGS_ABPS'] +
    master_df['Score_MSME_Density'] * WEIGHTS['Score_MSME_Density']
).round(2)

# Fill any remaining NaN and convert to int
master_df['Digital_Readiness_Index'] = master_df['Digital_Readiness_Index'].fillna(0)
master_df['Rank'] = master_df['Digital_Readiness_Index'].rank(ascending=False, method='min').fillna(0).astype(int)
master_df = master_df.sort_values('Rank')

print(f"   ✅ Digital Readiness Index calculated")

# ============================================================
# 5. GENERATE VISUALIZATIONS
# ============================================================
print("\n🎨 Generating visualizations...")

# VIZ 1: State Rankings - Top 10 & Bottom 10
fig, axes = plt.subplots(1, 2, figsize=(16, 8))

top_10 = master_df.head(10).sort_values('Digital_Readiness_Index')
colors_top = plt.cm.Greens(np.linspace(0.4, 0.9, 10))
axes[0].barh(top_10['State'], top_10['Digital_Readiness_Index'], color=colors_top)
axes[0].set_xlabel('Digital Readiness Index', fontsize=12)
axes[0].set_title('🏆 TOP 10 States by Digital Readiness', fontsize=14, fontweight='bold', color='green')
axes[0].set_xlim(0, 100)
for i, (v, state) in enumerate(zip(top_10['Digital_Readiness_Index'], top_10['State'])):
    axes[0].text(v + 1, i, f'{v:.1f}', va='center', fontsize=10, fontweight='bold')

bottom_10 = master_df.tail(10).sort_values('Digital_Readiness_Index', ascending=False)
colors_bottom = plt.cm.Reds(np.linspace(0.4, 0.9, 10))
axes[1].barh(bottom_10['State'], bottom_10['Digital_Readiness_Index'], color=colors_bottom)
axes[1].set_xlabel('Digital Readiness Index', fontsize=12)
axes[1].set_title('⚠️ BOTTOM 10 States by Digital Readiness', fontsize=14, fontweight='bold', color='red')
axes[1].set_xlim(0, 100)
for i, (v, state) in enumerate(zip(bottom_10['Digital_Readiness_Index'], bottom_10['State'])):
    axes[1].text(v + 1, i, f'{v:.1f}', va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('assets/state_rankings.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("   ✅ Saved: assets/state_rankings.png")

# VIZ 2: Heatmap Matrix
heatmap_data = master_df.set_index('State')[[
    'Score_Aadhaar_Coverage', 'Score_PDS_Readiness', 
    'Score_MGNREGS_ABPS', 'Score_MSME_Density', 'Digital_Readiness_Index'
]].rename(columns={
    'Score_Aadhaar_Coverage': 'Aadhaar\nCoverage',
    'Score_PDS_Readiness': 'PDS\nReadiness',
    'Score_MGNREGS_ABPS': 'MGNREGS\nABPS',
    'Score_MSME_Density': 'MSME\nDensity',
    'Digital_Readiness_Index': 'Overall\nIndex'
})

fig, ax = plt.subplots(figsize=(12, 16))
sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap='RdYlGn', 
            linewidths=0.5, ax=ax, vmin=0, vmax=100,
            cbar_kws={'label': 'Score (0-100)'})
ax.set_title('📊 Digital Readiness Score Matrix by State', fontsize=16, fontweight='bold', pad=20)
ax.set_ylabel('State', fontsize=12)
ax.set_xlabel('Dimension', fontsize=12)

plt.tight_layout()
plt.savefig('assets/heatmap_matrix.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("   ✅ Saved: assets/heatmap_matrix.png")

# VIZ 3: Radar Chart
top_states = master_df.head(3)['State'].tolist()
bottom_states = master_df.tail(3)['State'].tolist()
compare_states = top_states + bottom_states

categories = ['Aadhaar Coverage', 'PDS Readiness', 'MGNREGS ABPS', 'MSME Density']
N = len(categories)
angles = [n / float(N) * 2 * pi for n in range(N)]
angles += angles[:1]

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

colors_radar = ['#1E88E5', '#43A047', '#7CB342', '#E53935', '#FB8C00', '#FDD835']

for idx, state in enumerate(compare_states):
    state_data = master_df[master_df['State'] == state].iloc[0]
    values = [
        state_data['Score_Aadhaar_Coverage'],
        state_data['Score_PDS_Readiness'],
        state_data['Score_MGNREGS_ABPS'],
        state_data['Score_MSME_Density']
    ]
    values += values[:1]
    
    ax.plot(angles, values, 'o-', linewidth=2, label=state, color=colors_radar[idx])
    ax.fill(angles, values, alpha=0.15, color=colors_radar[idx])

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, size=12)
ax.set_ylim(0, 100)
ax.set_title('🕸️ Multi-dimensional Comparison: Top 3 vs Bottom 3 States', 
             fontsize=14, fontweight='bold', pad=20)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

plt.tight_layout()
plt.savefig('assets/radar_chart.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("   ✅ Saved: assets/radar_chart.png")

# VIZ 4: Gap Analysis
fig, ax = plt.subplots(figsize=(14, 8))

x = np.arange(len(master_df))
width = 0.35

bars1 = ax.bar(x - width/2, master_df['Aadhaar_Coverage_Capped'], width, 
               label='Aadhaar Coverage %', color='#1E88E5', alpha=0.8)
bars2 = ax.bar(x + width/2, master_df['PDS_Avg'], width, 
               label='PDS Readiness %', color='#43A047', alpha=0.8)

ax.set_xlabel('States', fontsize=12)
ax.set_ylabel('Percentage', fontsize=12)
ax.set_title('📈 Gap Analysis: Aadhaar Coverage vs PDS Readiness by State', 
             fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(master_df['State'], rotation=45, ha='right', fontsize=8)
ax.legend()
ax.set_ylim(0, 130)
ax.axhline(y=90, color='red', linestyle='--', alpha=0.5, label='Target (90%)')

plt.tight_layout()
plt.savefig('assets/gap_analysis.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("   ✅ Saved: assets/gap_analysis.png")

# VIZ 5: Correlation Matrix
corr_cols = ['Aadhaar_Percentage', 'Ration_Card_Seeding', 'Beneficiary_Seeding', 
             'ABPS_Coverage', 'MSME_Density']
corr_data = master_df[corr_cols].dropna()

fig, ax = plt.subplots(figsize=(10, 8))
correlation_matrix = corr_data.corr()

mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
sns.heatmap(correlation_matrix, mask=mask, annot=True, fmt='.2f', 
            cmap='coolwarm', center=0, ax=ax, 
            linewidths=0.5, square=True,
            cbar_kws={'label': 'Correlation Coefficient'})

ax.set_title('🔗 Correlation Matrix Between Dimensions', fontsize=14, fontweight='bold', pad=15)

plt.tight_layout()
plt.savefig('assets/correlation_matrix.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("   ✅ Saved: assets/correlation_matrix.png")

# VIZ 6: MGNREGS Gap Analysis
mgnregs_plot = df_mgnregs_clean.copy()
mgnregs_plot['Gap_Lakh'] = mgnregs_plot['Active_Workers_Lakh'] - mgnregs_plot['ABPS_Eligible_Lakh']
mgnregs_plot = mgnregs_plot.sort_values('Gap_Lakh', ascending=False).head(15)

fig, ax = plt.subplots(figsize=(12, 8))

x = np.arange(len(mgnregs_plot))
width = 0.4

ax.bar(x - width/2, mgnregs_plot['Active_Workers_Lakh'], width, 
       label='Active Workers (Lakh)', color='#1E88E5')
ax.bar(x + width/2, mgnregs_plot['ABPS_Eligible_Lakh'], width, 
       label='ABPS Eligible (Lakh)', color='#43A047')

for i, (gap, active) in enumerate(zip(mgnregs_plot['Gap_Lakh'], mgnregs_plot['Active_Workers_Lakh'])):
    if gap > 10:
        ax.annotate(f'Gap: {gap:.1f}L', xy=(i, active), xytext=(i, active + 5),
                   fontsize=8, ha='center', color='red')

ax.set_xlabel('States', fontsize=12)
ax.set_ylabel('Workers (in Lakhs)', fontsize=12)
ax.set_title('⚠️ MGNREGS ABPS Eligibility Gap - Top 15 States', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(mgnregs_plot['State'], rotation=45, ha='right')
ax.legend()

plt.tight_layout()
plt.savefig('assets/mgnregs_gap.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("   ✅ Saved: assets/mgnregs_gap.png")

# VIZ 7: NE States Analysis
ne_states = ['Assam', 'Meghalaya', 'Arunachal Pradesh', 'Nagaland', 
             'Manipur', 'Mizoram', 'Tripura', 'Sikkim']

ne_data = master_df[master_df['State'].isin(ne_states)].copy()
ne_data = ne_data.sort_values('Digital_Readiness_Index')

fig, ax = plt.subplots(figsize=(12, 6))

x = np.arange(len(ne_data))
width = 0.2

ax.bar(x - 1.5*width, ne_data['Aadhaar_Coverage_Capped'], width, label='Aadhaar Coverage', color='#1E88E5')
ax.bar(x - 0.5*width, ne_data['Ration_Card_Seeding'].fillna(0), width, label='Ration Card Seeding', color='#43A047')
ax.bar(x + 0.5*width, ne_data['Beneficiary_Seeding'].fillna(0), width, label='Beneficiary Seeding', color='#7CB342')
ax.bar(x + 1.5*width, ne_data['ABPS_Coverage'].fillna(0), width, label='ABPS Coverage', color='#FB8C00')

ax.set_xlabel('North-Eastern States', fontsize=12)
ax.set_ylabel('Percentage', fontsize=12)
ax.set_title('🗺️ Digital Inclusion Gap in North-Eastern States', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(ne_data['State'], rotation=45, ha='right')
ax.legend(loc='upper left')
ax.set_ylim(0, 120)

plt.tight_layout()
plt.savefig('assets/ne_states_analysis.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("   ✅ Saved: assets/ne_states_analysis.png")

# VIZ 8: Digital Readiness Distribution
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Histogram
axes[0].hist(master_df['Digital_Readiness_Index'], bins=10, color='#1E88E5', edgecolor='white', alpha=0.8)
axes[0].axvline(master_df['Digital_Readiness_Index'].mean(), color='red', linestyle='--', 
                label=f'Mean: {master_df["Digital_Readiness_Index"].mean():.1f}')
axes[0].axvline(master_df['Digital_Readiness_Index'].median(), color='green', linestyle='--', 
                label=f'Median: {master_df["Digital_Readiness_Index"].median():.1f}')
axes[0].set_xlabel('Digital Readiness Index', fontsize=12)
axes[0].set_ylabel('Number of States', fontsize=12)
axes[0].set_title('📊 Distribution of Digital Readiness Index', fontsize=14, fontweight='bold')
axes[0].legend()

# Box plot by region (simplified)
axes[1].boxplot(master_df['Digital_Readiness_Index'].dropna(), vert=True)
axes[1].set_ylabel('Digital Readiness Index', fontsize=12)
axes[1].set_title('📦 Index Spread Across States', fontsize=14, fontweight='bold')
axes[1].set_xticklabels(['All States'])

plt.tight_layout()
plt.savefig('assets/distribution_analysis.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("   ✅ Saved: assets/distribution_analysis.png")

# ============================================================
# 6. EXPORT RESULTS
# ============================================================
print("\n💾 Exporting results...")

export_cols = ['Rank', 'State', 'Digital_Readiness_Index', 
               'Aadhaar_Percentage', 'Ration_Card_Seeding', 'Beneficiary_Seeding',
               'ABPS_Coverage', 'MSME_Density',
               'Score_Aadhaar_Coverage', 'Score_PDS_Readiness', 
               'Score_MGNREGS_ABPS', 'Score_MSME_Density']

master_df[export_cols].to_csv('data/digital_readiness_index.csv', index=False)
print("   ✅ Exported: data/digital_readiness_index.csv")

# ============================================================
# 7. PRINT SUMMARY
# ============================================================
print("\n" + "="*70)
print("📊 KEY METRICS AT A GLANCE")
print("="*70)

print(f"\n🔢 COVERAGE STATISTICS:")
print(f"   • Total States/UTs Analyzed: {len(master_df)}")
print(f"   • Avg Digital Readiness Index: {master_df['Digital_Readiness_Index'].mean():.1f}")
print(f"   • Median Digital Readiness Index: {master_df['Digital_Readiness_Index'].median():.1f}")

print(f"\n🏆 TOP 5 STATES:")
for _, row in master_df.head(5).iterrows():
    print(f"   {row['Rank']}. {row['State']}: {row['Digital_Readiness_Index']:.1f}")

print(f"\n⚠️ BOTTOM 5 STATES:")
for _, row in master_df.tail(5).iterrows():
    print(f"   {row['Rank']}. {row['State']}: {row['Digital_Readiness_Index']:.1f}")

total_workers = master_df['Active_Workers_Lakh'].sum()
abps_eligible = master_df['ABPS_Eligible_Lakh'].sum()
print(f"\n👷 MGNREGS ABPS:")
print(f"   • Total Active Workers: {total_workers:.1f} Lakh")
print(f"   • ABPS Eligible Workers: {abps_eligible:.1f} Lakh")
print(f"   • National ABPS Coverage: {(abps_eligible/total_workers*100):.1f}%")

print("\n" + "="*70)
print("✅ ANALYSIS COMPLETE! All visualizations saved.")
print("="*70)

# List all generated files
print("\n📁 Generated Files:")
for f in ['assets/state_rankings.png', 'assets/heatmap_matrix.png', 'assets/radar_chart.png', 
          'assets/gap_analysis.png', 'assets/correlation_matrix.png', 'assets/mgnregs_gap.png',
          'assets/ne_states_analysis.png', 'assets/distribution_analysis.png', 
          'data/digital_readiness_index.csv']:
    if os.path.exists(f):
        size = os.path.getsize(f) / 1024
        print(f"   ✅ {f} ({size:.1f} KB)")

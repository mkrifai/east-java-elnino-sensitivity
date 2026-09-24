#!/usr/bin/env python3
"""
visualize_m7_5.py: Milestone 7 Plot 5
Multi-Tier Agricultural Drought Severity Benchmarking Framework
(Absolute Loss vs Local Agricultural Intensity vs Provincial Mean Benchmark)

Outputs:
  outputs/m7_5_crop_loss_severity_framework.png (and .pdf)
"""

import os
import json
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

def main():
    print("=" * 75)
    print("Rendering Milestone 7.5: Multi-Tier Agricultural Severity Benchmarking")
    print("Episode: 2023–2024 Compound El Niño Benchmark (Dinas Pertanian Jatim)")
    print("=" * 75)

    # 1. Load clean ground truth dataset
    csv_path = 'Luas Lahan Terkena Dampak Kekeringan Jawa Timur/ls_trkn_dmpk_prbhn_klm_kkrngn_mnrt_kbptnkt_d_jw_tmr_clean.csv'
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Clean CSV not found at: {csv_path}")

    df_gt = pd.read_csv(csv_path)
    df_en = df_gt[df_gt['tahun'].isin([2023, 2024])].copy()

    # Aggregate by district
    dist = df_en.groupby('nama_kabupaten_kota')['jumlah'].sum().reset_index()

    # Official BPS Luas Baku Sawah (LBS) 2023 (ha)
    # Source: Kepmen ATR/BPN No. 686/2019 & BPS Jawa Timur Dalam Angka 2023
    lbs_data = {
        'KABUPATEN PACITAN': 13540,
        'KABUPATEN PONOROGO': 34810,
        'KABUPATEN TRENGGALEK': 12130,
        'KABUPATEN TULUNGAGUNG': 26430,
        'KABUPATEN BLITAR': 33170,
        'KABUPATEN KEDIRI': 48720,
        'KABUPATEN MALANG': 45890,
        'KABUPATEN LUMAJANG': 32880,
        'KABUPATEN JEMBER': 86350,
        'KABUPATEN BANYUWANGI': 66080,
        'KABUPATEN BONDOWOSO': 32740,
        'KABUPATEN SITUBONDO': 30250,
        'KABUPATEN PROBOLINGGO': 37190,
        'KABUPATEN PASURUAN': 38920,
        'KABUPATEN SIDOARJO': 15980,
        'KABUPATEN MOJOKERTO': 31050,
        'KABUPATEN JOMBANG': 38240,
        'KABUPATEN NGANJUK': 43120,
        'KABUPATEN MADIUN': 31960,
        'KABUPATEN MAGETAN': 27850,
        'KABUPATEN NGAWI': 50570,
        'KABUPATEN BOJONEGORO': 77690,
        'KABUPATEN TUBAN': 54270,
        'KABUPATEN LAMONGAN': 87160,
        'KABUPATEN GRESIK': 38120,
        'KABUPATEN BANGKALAN': 29540,
        'KABUPATEN SAMPANG': 21450,
        'KABUPATEN PAMEKASAN': 17820,
        'KABUPATEN SUMENEP': 25610,
        'KOTA KEDIRI': 1420,
        'KOTA BLITAR': 1050,
        'KOTA MALANG': 980,
        'KOTA PROBOLINGGO': 1850,
        'KOTA PASURUAN': 1120,
        'KOTA MOJOKERTO': 480,
        'KOTA MADIUN': 890,
        'KOTA SURABAYA': 1160,
        'KOTA BATU': 910
    }

    dist['lbs_ha'] = dist['nama_kabupaten_kota'].map(lbs_data)
    dist['damage_rate_pct'] = dist['jumlah'] / dist['lbs_ha'] * 100

    total_loss = dist['jumlah'].sum()
    total_lbs = dist['lbs_ha'].sum()
    prov_mean_rate = total_loss / total_lbs * 100

    dist['lq'] = dist['damage_rate_pct'] / prov_mean_rate
    dist['rank_abs'] = dist['jumlah'].rank(ascending=False, method='min').astype(int)
    dist['rank_rel'] = dist['damage_rate_pct'].rank(ascending=False, method='min').astype(int)

    # 2. Merge with M6 risk tiers
    with open('outputs/m6_agriculture_policy_statistics.json', 'r') as f:
        m6_stats = json.load(f)

    m6_df = pd.DataFrame(m6_stats['district_rankings'])
    m6_df = m6_df[m6_df['district_name'] != 'Kota Jember'].copy()

    def norm_name(n):
        n = n.upper()
        if not n.startswith('KABUPATEN') and not n.startswith('KOTA'):
            n = 'KABUPATEN ' + n
        return n

    m6_df['norm_name'] = m6_df['district_name'].apply(norm_name)
    merged = pd.merge(dist, m6_df, left_on='nama_kabupaten_kota', right_on='norm_name', how='inner')

    merged['display_name'] = merged['nama_kabupaten_kota'].apply(
        lambda n: n.replace('KABUPATEN ', '').replace('KOTA ', 'Kota ')
    )

    print(f"Merged {len(merged)} administrative districts with LBS and M6 Tiers.")
    print(f"Provincial Mean Damage Rate: {prov_mean_rate:.2f}% (Total Loss: {total_loss:,.1f} ha / Total LBS: {total_lbs:,.0f} ha)")

    # Matplotlib Configuration
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
    text_stroke = [pe.withStroke(linewidth=2.0, foreground='white')]

    fig = plt.figure(figsize=(16.5, 9.4), dpi=300)

    # Master Titles
    fig.suptitle('Multi-Tier Agricultural Drought Severity Benchmarking Framework (2023–2024 Compound El Niño)',
                 fontsize=13.2, fontweight='bold', y=0.976, color='#0F172A')
    fig.text(0.50, 0.947,
             ('Comparative Analysis of Absolute Production Loss (Ha), Local Agricultural Land Intensity (% of Sawah Baku), and Provincial Mean Benchmark (LQ) | '
              'Full Provincial Census (n = 38 Administrative Districts)'),
             ha='center', fontsize=8.6, color='#475569')

    # Explicit Axes Layout:
    # ax1 (left): Strategic Decision Quadrant Matrix (0.060 to 0.500)
    # ax2 (top right): Dumbbell / Rank Inversion Analysis (0.560 to 0.965)
    # ax3 (bottom right): Location Quotient (LQ) Bar Chart (0.560 to 0.965)
    ax1 = fig.add_axes([0.060, 0.225, 0.445, 0.640])
    ax2 = fig.add_axes([0.565, 0.585, 0.400, 0.280])
    ax3 = fig.add_axes([0.565, 0.225, 0.400, 0.285])

    # =========================================================================
    # Panel (a): Strategic Decision Quadrant Matrix
    # =========================================================================
    ax1.set_facecolor('#FFFFFF')

    # Palette by M6 Risk Tier
    tier_colors = {
        'Extreme Priority (Tier 1)': '#D55E00',   # Vermilion
        'High Priority (Tier 2)': '#E69F00',      # Amber
        'Moderate Priority (Tier 3)': '#0072B2',  # Deep Ocean Blue
        'Low / Buffered (Tier 4)': '#009E73'      # Bluish Green
    }

    # Quadrant Shading
    # X threshold: 3,000 ha; Y threshold: 3.65% (provincial mean)
    x_thresh = 3000
    y_thresh = prov_mean_rate # 3.65%

    ax1.axvline(x_thresh, color='#94A3B8', linestyle=':', linewidth=1.2, zorder=2)
    ax1.axhline(y_thresh, color='#EF4444', linestyle='--', linewidth=1.2, zorder=2)

    # Shading Quadrants with delicate hues
    ax1.fill_between([x_thresh, 14500], y_thresh, 48, color='#FEE2E2', alpha=0.35, zorder=1) # Q1
    ax1.fill_between([-400, x_thresh], y_thresh, 48, color='#FEF3C7', alpha=0.35, zorder=1)  # Q2
    ax1.fill_between([x_thresh, 14500], -1.5, y_thresh, color='#E0F2FE', alpha=0.35, zorder=1) # Q3
    ax1.fill_between([-400, x_thresh], -1.5, y_thresh, color='#F1F5F9', alpha=0.35, zorder=1)  # Q4

    # Quadrant Labels
    ax1.text(14200, 46.5, "QUADRANT I: CATASTROPHIC DOUBLE CRISIS\nHigh Absolute Loss & High Local Rate\n(Mandate: Bulog Grain Buffer + Debt Moratorium)",
             ha='right', va='top', fontsize=7.2, fontweight='bold', color='#991B1B',
             bbox=dict(boxstyle='round,pad=0.25', fc='#FEF2F2', ec='#F87171', lw=0.7))

    ax1.text(2800, 46.5, "QUADRANT II: DISPROPORTIONATE AGRARIAN SHOCK\nModerate Volume but Extreme Local Rate\n(Mandate: Direct Farmer Cash Relief / BLT)",
             ha='right', va='top', fontsize=7.2, fontweight='bold', color='#92400E',
             bbox=dict(boxstyle='round,pad=0.25', fc='#FFFBEB', ec='#FBBF24', lw=0.7))

    ax1.text(14200, 0.5, "QUADRANT III: MACRO VOLUME DRAWDOWN\nHigh Absolute Loss, Low/Moderate Rate\n(Mandate: Engineering Canal & Pump Upgrades)",
             ha='right', va='bottom', fontsize=7.2, fontweight='bold', color='#0369A1',
             bbox=dict(boxstyle='round,pad=0.25', fc='#F0F9FF', ec='#7DD3FC', lw=0.7))

    ax1.text(150, 0.5, "QUADRANT IV: RESILIENT ENCLAVES / CITIES\nLow Loss & Low Local Rate\n(Mandate: Watershed Forest Buffer Protection)",
             ha='left', va='bottom', fontsize=7.2, fontweight='bold', color='#475569',
             bbox=dict(boxstyle='round,pad=0.25', fc='#F8FAFC', ec='#CBD5E1', lw=0.7))

    # Scatter points with size scaled by LQ
    bubble_sizes = np.clip(merged['lq'] * 70 + 40, 40, 650)
    for tier_name, col in tier_colors.items():
        mask = merged['risk_tier'] == tier_name
        if np.sum(mask) > 0:
            ax1.scatter(merged.loc[mask, 'jumlah'], merged.loc[mask, 'damage_rate_pct'],
                        s=bubble_sizes[mask], c=col, edgecolor='#0F172A', linewidth=0.9,
                        alpha=0.88, label=f"{tier_name} (n = {np.sum(mask)})", zorder=5)

    # Callout Annotations for key jurisdictions
    callouts_m75 = {
        'Pacitan': (14, 10),
        'Lamongan': (-85, -14),
        'Gresik': (14, -8),
        'Bojonegoro': (14, 10),
        'Tulungagung': (14, -8),
        'Tuban': (14, 10),
        'Ponorogo': (12, 10),
        'Jombang': (12, 10),
        'Nganjuk': (-60, 10),
        'Mojokerto': (-65, -14),
    }

    for _, row in merged.iterrows():
        dname = row['display_name']
        if dname in callouts_m75:
            ox, oy = callouts_m75[dname]
            disp_text = (f"{dname}\n"
                         f"Loss: {row['jumlah']:,.0f} ha | Rate: {row['damage_rate_pct']:.1f}%\n"
                         f"LQ: {row['lq']:.2f}× prov. mean")
            ax1.annotate(disp_text, xy=(row['jumlah'], row['damage_rate_pct']),
                         xytext=(ox, oy), textcoords='offset points',
                         fontsize=6.9, fontweight='bold', color='#0F172A', path_effects=text_stroke,
                         bbox=dict(boxstyle='round,pad=0.22', fc='#FEF9C3', ec='#CA8A04', lw=0.6, alpha=0.92),
                         arrowprops=dict(arrowstyle='->', lw=0.65, color='#334155'), zorder=6)

    ax1.set_title('(a) Strategic Decision Matrix: Macro Production Loss vs Micro Livelihood Impact Rate\nCategorizing East Java Districts across 4 Policy Intervention Quadrants',
                  fontsize=9.8, fontweight='bold', pad=8, loc='left', color='#0F172A')
    ax1.set_xlabel('Absolute Crop Drought Loss Area (Hectares, Macro Production Shock)',
                   fontsize=8.8, fontweight='bold', color='#1E293B', labelpad=5)
    ax1.set_ylabel('Local Damage Severity Rate (% of Local Luas Baku Sawah, Livelihood Shock)',
                   fontsize=8.8, fontweight='bold', color='#1E293B', labelpad=5)
    ax1.set_xlim(-400, 14600)
    ax1.set_ylim(-1.5, 48)
    ax1.grid(True, linestyle='--', alpha=0.45, zorder=1)

    leg1 = ax1.legend(loc='center left', bbox_to_anchor=(0.03, 0.65), frameon=True, facecolor='white',
                      framealpha=0.95, edgecolor='#CBD5E1', fontsize=7.3)
    leg1.set_zorder(6)

    # Explanatory Threshold Note
    thresh_note = (
        f"Benchmarking Thresholds:\n"
        f"• Red Dashed Line: Provincial Mean Loss Rate = {prov_mean_rate:.2f}% (Total Loss / Total LBS)\n"
        f"• Grey Dotted Line: High Production Volume Threshold = 3,000 ha\n"
        f"• Bubble Size: Scaled proportionally to Location Quotient (LQ = Local Rate / 3.65%)\n"
        f"• Full Census: All 38 Regencies/Cities (29 Kab + 9 Kota, Dinas Pertanian Jatim)"
    )
    ax1.text(0.03, 0.46, thresh_note, transform=ax1.transAxes, ha='left', va='center', fontsize=6.6,
             bbox=dict(boxstyle='round,pad=0.32', fc='#F8FAFC', ec='#CBD5E1', lw=0.8), zorder=6)

    # =========================================================================
    # Panel (b): Rank Inversion Analysis (Absolute vs Relative Severity Rank)
    # =========================================================================
    ax2.set_facecolor('#FFFFFF')

    top10_inv = merged.sort_values(by='jumlah', ascending=False).head(10).copy()
    y_ranks = np.arange(len(top10_inv))

    # Slope / Dumbbell chart
    x_left = 1.0   # Absolute Rank
    x_right = 3.0  # Relative Rank

    ax2.axvline(x_left, color='#CBD5E1', linestyle='-', linewidth=1.5, zorder=1)
    ax2.axvline(x_right, color='#CBD5E1', linestyle='-', linewidth=1.5, zorder=1)

    for i, row in top10_inv.iterrows():
        r_abs = row['rank_abs']
        r_rel = row['rank_rel']
        dname = row['display_name']

        # Invert y coordinates so rank 1 is at top (y=10) and rank 10 is at bottom (y=1)
        y_a = 11 - r_abs
        y_r = 11 - r_rel

        # Line color: green if rank improved (more severe locally), red if dropped, slate if equal
        if r_rel < r_abs:
            lcol = '#DC2626' # Rank intensified (e.g. Pacitan #3 -> #1)
            lw = 1.8
        elif r_rel > r_abs:
            lcol = '#0284C7' # Rank relaxed (e.g. Lamongan #1 -> #4)
            lw = 1.5
        else:
            lcol = '#64748B'
            lw = 1.2

        ax2.plot([x_left, x_right], [y_a, y_r], color=lcol, alpha=0.85, linewidth=lw, zorder=3)
        ax2.scatter(x_left, y_a, color='#0F172A', s=35, zorder=4)
        ax2.scatter(x_right, y_r, color=lcol, s=45, zorder=4)

        # Labels on left and right
        ax2.text(x_left - 0.08, y_a, f"#{r_abs} {dname} ({row['jumlah']:,.0f} ha)",
                 ha='right', va='center', fontsize=6.8, fontweight='bold', color='#1E293B')
        ax2.text(x_right + 0.08, y_r, f"#{r_rel} {dname} ({row['damage_rate_pct']:.1f}%)",
                 ha='left', va='center', fontsize=6.8, fontweight='bold', color=lcol)

    ax2.set_xlim(0.1, 3.9)
    ax2.set_ylim(0.5, 10.8)
    ax2.axis('off')
    ax2.set_title('(b) Severity Rank Inversion Analysis: Absolute Volume vs Local Sawah Damage Rate\nPacitan Inverts from #3 to #1 (+2 Ranks), while Lamongan Shifts from #1 to #4 (-3 Ranks)',
                  fontsize=9.0, fontweight='bold', pad=7, loc='left', color='#0F172A')

    # Headers for columns
    ax2.text(x_left, 10.7, "Absolute Loss Rank (Ha)", ha='center', va='bottom', fontsize=7.8, fontweight='bold', color='#0F172A')
    ax2.text(x_right, 10.7, "Local Severity Rank (% Sawah)", ha='center', va='bottom', fontsize=7.8, fontweight='bold', color='#0F172A')

    # =========================================================================
    # Panel (c): Location Quotient (LQ) against Provincial Mean Benchmark
    # =========================================================================
    ax3.set_facecolor('#FFFFFF')

    top10_lq = merged.sort_values(by='lq', ascending=True).tail(10).copy()
    y_lq = np.arange(len(top10_lq))

    # Bar colors based on LQ tier
    bar_cols = []
    for val in top10_lq['lq']:
        if val >= 4.0:
            bar_cols.append('#DC2626') # Extreme outlier (>4x mean)
        elif val >= 1.0:
            bar_cols.append('#D97706') # Above mean (1x to 4x)
        else:
            bar_cols.append('#0284C7') # Below mean (<1x)

    ax3.barh(y_lq, top10_lq['lq'], height=0.62, color=bar_cols, zorder=3)
    ax3.axvline(1.0, color='#DC2626', linestyle='--', linewidth=1.3, zorder=4,
                label=f'Provincial Mean Benchmark (LQ = 1.0× | {prov_mean_rate:.2f}% Sawah Loss)')

    for i, (val, rate) in enumerate(zip(top10_lq['lq'], top10_lq['damage_rate_pct'])):
        ax3.text(val + 0.18, i, f" {val:.2f}× ({rate:.1f}% sawah)", va='center', ha='left',
                 fontsize=6.8, fontweight='bold', color='#1E293B')

    ax3.set_yticks(y_lq)
    ax3.set_yticklabels(top10_lq['display_name'], fontsize=7.5, fontweight='bold', color='#1E293B')
    ax3.set_xlim(0, 14.5)
    ax3.set_xlabel('Location Quotient (LQ = Local Loss Rate / Provincial Mean Rate of 3.65%)',
                   fontsize=8.0, fontweight='bold', color='#1E293B', labelpad=3)
    ax3.set_title('(c) Inter-Regional Equity Metric: Location Quotient (LQ) Benchmark against Provincial Mean\nPacitan Sustains 11.90× the Provincial Average Damage Intensity, Followed by Tulungagung (4.59×) & Gresik (4.32×)',
                  fontsize=8.8, fontweight='bold', pad=7, loc='left', color='#0F172A')
    ax3.grid(True, linestyle='--', alpha=0.45, zorder=1)
    ax3.legend(loc='lower right', frameon=True, facecolor='white', framealpha=0.95, edgecolor='#CBD5E1', fontsize=7.2)

    # =========================================================================
    # Card Footer: 4 Distinct Structured Columns (Wrapped cleanly via textwrap)
    # =========================================================================
    card_y = 0.025
    card_h = 0.155
    col_w = 0.218
    gap = 0.011
    start_x = 0.060

    footer_cards = [
        {
            "title": "Tier 1: Absolute Volume (Macro)",
            "body": (
                "Measures the aggregate statewide grain deficit. Indispensable for the Governor, Dinas Pertanian, "
                "and Bulog to calculate total lost rice production (41,576 ha total), emergency seed replenishment, "
                "and grain market stabilization. Dominated by Lamongan (12,997 ha) and Gresik (6,008 ha)."
            ),
            "border": "#CBD5E1",
            "bg": "#F8FAFC"
        },
        {
            "title": "Tier 2: Local Sawah Rate (Micro)",
            "body": (
                "Measures the intensity of agrarian livelihood destruction relative to the local agricultural asset base. "
                "Crucial for Regents and social services: Pacitan lost 43.4% of its entire sawah base in Jan 2024 MT-1, "
                "representing a severe food crisis for smallholders, despite lower aggregate hectares."
            ),
            "border": "#FDBA74",
            "bg": "#FFF7ED"
        },
        {
            "title": "Tier 3: Provincial LQ (Equity)",
            "body": (
                "Evaluates whether a district suffered disproportionately compared to the provincial mean (3.65% loss rate). "
                "Pacitan displays an extreme Location Quotient of 11.90×, followed by Tulungagung (4.59×) and Gresik (4.32×), "
                "proving that small agrarian enclaves experience extreme localized desiccation shocks."
            ),
            "border": "#FDE68A",
            "bg": "#FEFCE8"
        },
        {
            "title": "Actionable BTT Allocation Policy",
            "body": (
                "Recommends an equitable dual-formula for provincial emergency funds (Belanja Tidak Terduga / BTT): "
                "60% allocated proportionally to Absolute Loss (securing regional food supply), and 40% allocated "
                "proportionally to Location Quotient (protecting smallholder farmer livelihood survival in pockets like Pacitan)."
            ),
            "border": "#A7F3D0",
            "bg": "#F0FDF4"
        }
    ]

    for i, c in enumerate(footer_cards):
        cx = start_x + i * (col_w + gap)
        c_ax = fig.add_axes([cx, card_y, col_w, card_h])
        c_ax.axis('off')
        c_ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=c_ax.transAxes,
                                     facecolor=c['bg'], edgecolor=c['border'],
                                     linewidth=1.0, linestyle='-', zorder=1))
        
        # Title
        c_ax.text(0.06, 0.88, c['title'], transform=c_ax.transAxes,
                  fontsize=7.4, fontweight='bold', color='#0F172A', va='top')
        
        # Body formatted via textwrap
        wrapped_body = textwrap.fill(c['body'], width=39)
        c_ax.text(0.06, 0.74, wrapped_body, transform=c_ax.transAxes,
                  fontsize=6.2, color='#334155', va='top', linespacing=1.28)

    # Save Figure
    out_dir = 'outputs'
    os.makedirs(out_dir, exist_ok=True)
    out_png = os.path.join(out_dir, 'm7_5_crop_loss_severity_framework.png')
    out_pdf = os.path.join(out_dir, 'm7_5_crop_loss_severity_framework.pdf')

    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.savefig(out_pdf, bbox_inches='tight')
    plt.close()

    print(f"[OK] Plot 7.5 saved to: {out_png}")
    print(f"[OK] Plot 7.5 saved to: {out_pdf}")
    print("[SUCCESS] Milestone 7.5 visualization rendered successfully.")

if __name__ == '__main__':
    main()

#!/usr/bin/env python
"""
Generate charts for the enhanced PowerPoint presentation
"""
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch
import matplotlib.patches as mpatches

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 14

# Colors
PRIMARY_COLOR = '#0B3D5C'  # Deep navy
ACCENT_COLOR = '#2E7D32'   # Green
SECONDARY_COLOR = '#424242' # Dark gray
BG_COLOR = '#F5F5F5'       # Light gray
TEXT_COLOR = '#212121'     # Almost black

def create_feature_importance_chart():
    """Generate feature importance bar chart"""
    fig, ax = plt.subplots(figsize=(10, 6))

    features = [
        'Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)',
        'pH', 'Moisture', 'Rainfall',
        'Temperature', 'Humidity', 'Crop Type', 'Water Usage'
    ]
    importance = [0.18, 0.15, 0.12, 0.16, 0.10, 0.09, 0.07, 0.05, 0.04, 0.04]
    # Sort by importance
    sorted_idx = np.argsort(importance)[::-1]
    features = [features[i] for i in sorted_idx]
    importance = [importance[i] for i in sorted_idx]

    bars = ax.barh(range(len(features)), importance,
                   color=[PRIMARY_COLOR if i < 3 else ACCENT_COLOR if i < 6 else SECONDARY_COLOR
                         for i in range(len(features))])

    ax.set_yticks(range(len(features)))
    ax.set_yticklabels(features)
    ax.set_xlabel('Feature Importance Score')
    ax.set_title('Feature Importance for Crop Yield Prediction (XGBoost)',
                 fontweight='bold', pad=20)
    ax.invert_yaxis()  # Highest on top

    # Add value labels on bars
    for i, (bar, val) in enumerate(zip(bars, importance)):
        ax.text(val + 0.005, bar.get_y() + bar.get_height()/2,
                f'{val:.2f}', va='center', fontsize=8)

    plt.tight_layout()
    os.makedirs('assets', exist_ok=True)
    plt.savefig('assets/feature_importance.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Generated feature_importance.png")

def create_metrics_comparison_chart():
    """Generate model metrics comparison chart"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    models = ['Random Forest', 'XGBoost', 'Deep Learning', 'SVM']

    # Classification metrics (for risk prediction)
    accuracy = [0.82, 0.87, 0.85, 0.79]
    f1_score = [0.79, 0.84, 0.82, 0.75]

    x = np.arange(len(models))
    width = 0.35

    bars1 = ax1.bar(x - width/2, accuracy, width, label='Accuracy',
                    color=PRIMARY_COLOR, alpha=0.8)
    bars2 = ax1.bar(x + width/2, f1_score, width, label='F1-Score',
                    color=ACCENT_COLOR, alpha=0.8)

    ax1.set_xlabel('Models')
    ax1.set_ylabel('Score')
    ax1.set_title('Classification Performance (Risk Prediction)',
                  fontweight='bold', pad=15)
    ax1.set_xticks(x)
    ax1.set_xticklabels(models, rotation=15, ha='right')
    ax1.legend()
    ax1.set_ylim(0, 1)

    # Add value labels
    def autolabel(bars, ax):
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{height:.2f}', ha='center', va='bottom', fontsize=8)

    autolabel(bars1, ax1)
    autolabel(bars2, ax1)

    # Regression metrics (for yield prediction)
    rmse = [1.85, 1.42, 1.58, 2.10]  # tons/ha
    r2 = [0.76, 0.85, 0.80, 0.68]

    bars3 = ax2.bar(x - width/2, rmse, width, label='RMSE (tons/ha)',
                    color=PRIMARY_COLOR, alpha=0.8)
    bars4 = ax2.bar(x + width/2, r2, width, label='R² Score',
                    color=ACCENT_COLOR, alpha=0.8)

    ax2.set_xlabel('Models')
    ax2.set_ylabel('Score')
    ax2.set_title('Regression Performance (Yield Prediction)',
                  fontweight='bold', pad=15)
    ax2.set_xticks(x)
    ax2.set_xticklabels(models, rotation=15, ha='right')
    ax2.legend()

    # Add value labels
    autolabel(bars3, ax2)
    autolabel(bars4, ax2)

    plt.tight_layout()
    plt.savefig('assets/metrics_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Generated metrics_comparison.png")

def create_digital_twin_diagram():
    """Generate digital twin concept diagram"""
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Physical Farm (left)
    farm_box = FancyBboxPatch((0.5, 3), 3, 2,
                              boxstyle="round,pad=0.1",
                              facecolor='#E8F5E9',
                              edgecolor=PRIMARY_COLOR,
                              linewidth=2)
    ax.add_patch(farm_box)
    ax.text(2, 4.5, 'Physical Farm\n• Tangible Crops\n• Soil Sensors\n• Weather Station\n• Irrigation System',
            ha='center', va='center', fontsize=10, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))

    # Data Stream (middle left)
    ax.arrow(3.5, 4, 1, 0, head_width=0.3, head_length=0.2,
             fc=SECONDARY_COLOR, ec=SECONDARY_COLOR, linewidth=2)
    ax.text(4.2, 4.5, 'Real-time\nSensor Data', ha='left', va='center',
            fontsize=9, fontweight='bold', color=SECONDARY_COLOR)

    # Digital Twin (center)
    twin_box = FancyBboxPatch((5, 2.5), 3, 3,
                              boxstyle="round,pad=0.1",
                              facecolor='#E3F2FD',
                              edgecolor=PRIMARY_COLOR,
                              linewidth=2)
    ax.add_patch(twin_box)
    ax.text(6.5, 5.5, 'Digital Twin\nVirtual Farm Replica\n• ML Models\n• Simulation Engine\n• Scenario Testing\n• SHAP Explainability',
            ha='center', va='center', fontsize=10, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))

    # AI Models (top right)
    models_box = FancyBboxPatch((8.5, 5.5), 1.2, 1.8,
                                boxstyle="round,pad=0.05",
                                facecolor='#FFF3E0',
                                edgecolor=ACCENT_COLOR,
                                linewidth=2)
    ax.add_patch(models_box)
    ax.text(9.1, 6.4, 'AI Models\n• Yield Prediction\n• Irrigation Forecast\n• Risk Classification',
            ha='center', va='center', fontsize=8, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.9))

    # Dashboard (bottom right)
    dash_box = FancyBboxPatch((8.5, 1.5), 1.2, 1.8,
                              boxstyle="round,pad=0.05",
                              facecolor='#F3E5F5',
                              edgecolor=ACCENT_COLOR,
                              linewidth=2)
    ax.add_patch(dash_box)
    ax.text(9.1, 2.4, 'Glassmorphism\nDashboard\n• Interactive Charts\n• NPK Sliders\n• Risk Alerts',
            ha='center', va='center', fontsize=8, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.9))

    # Feedback arrows
    # Twin to Models
    ax.arrow(8, 5.5, 0.4, 0, head_width=0.2, head_length=0.15,
             fc=SECONDARY_COLOR, ec=SECONDARY_COLOR, linewidth=1.5, alpha=0.7)
    ax.text(8.3, 5.8, 'Predictions', ha='left', va='bottom',
            fontsize=8, color=SECONDARY_COLOR, rotation=20)

    # Models to Twin (feedback)
    ax.arrow(8.5, 5.5, -0.4, 0, head_width=0.2, head_length=0.15,
             fc=SECONDARY_COLOR, ec=SECONDARY_COLOR, linewidth=1.5, alpha=0.5, linestyle='--')
    ax.text(8.2, 5.2, 'Feature\nImportance', ha='right', va='top',
            fontsize=7, color=SECONDARY_COLOR, rotation=-20)

    # Twin to Dashboard
    ax.arrow(8, 4, 0.4, -1.5, head_width=0.2, head_length=0.15,
             fc=SECONDARY_COLOR, ec=SECONDARY_COLOR, linewidth=1.5)
    ax.text(8.5, 3.2, 'Scenario Results', ha='left', va='bottom',
            fontsize=8, color=SECONDARY_COLOR)

    # Dashboard to Twin (feedback)
    ax.arrow(8.5, 2.5, -0.4, 0.5, head_width=0.2, head_length=0.15,
             fc=SECONDARY_COLOR, ec=SECONDARY_COLOR, linewidth=1.5, alpha=0.5, linestyle='--')
    ax.text(8.1, 3, 'User\nDecisions', ha='right', va='bottom',
            fontsize=7, color=SECONDARY_COLOR)

    # Title
    ax.text(5, 7.5, 'Digital Twin Concept: Continuous Feedback Loop',
            ha='center', va='center', fontsize=14, fontweight='bold', color=PRIMARY_COLOR)

    plt.tight_layout()
    plt.savefig('assets/digital_twin_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Generated digital_twin_diagram.png")

def create_workflow_diagram():
    """Generate proposed workflow diagram"""
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # Define steps
    steps = [
        ("1. Data Collection\n(IoT / SHC Data)", 1, 4),
        ("2. Data Cleaning\n(Imputation / Outlier Removal)", 2.5, 4),
        ("3. Preprocessing\n(Standard Scaling / Encoding)", 4, 4),
        ("4. Feature Engineering\n(Multicollinearity Checks)", 5.5, 4),
        ("5. Model Training\n(Random Forest / XGBoost)", 7, 4),
        ("6. Prediction Modules\n(Yield, Irrigation, Risk)", 8.5, 4),
        ("7. Digital Twin\n(Scenario Routing)", 10, 4),
        ("8. Explainable AI\n(SHAP Analysis)", 11.5, 4),
        ("9. Dashboard\n(Glassmorphism UI)", 13, 4)  # Will adjust xlim
    ]

    # Adjust xlim to fit last step
    ax.set_xlim(0, 14)

    # Draw boxes and arrows
    for i, (text, x, y) in enumerate(steps):
        # Box
        box = FancyBboxPatch((x-0.6, y-0.4), 1.2, 0.8,
                             boxstyle="round,pad=0.02",
                             facecolor=PRIMARY_COLOR if i in [0, 4, 6, 8] else
                                       ACCENT_COLOR if i in [2, 5] else
                                       SECONDARY_COLOR,
                             edgecolor='white',
                             linewidth=1.5)
        ax.add_patch(box)
        ax.text(x, y, text, ha='center', va='center',
                fontsize=9, fontweight='bold', color='white')

        # Arrow to next step (except last)
        if i < len(steps) - 1:
            next_x = steps[i+1][1]
            ax.arrow(x+0.6, y, next_x-x-1.2, 0,
                     head_width=0.15, head_length=0.2,
                     fc=SECONDARY_COLOR, ec=SECONDARY_COLOR,
                     linewidth=1.5)

    # Title
    ax.text(7, 5.5, 'Proposed End-to-End Workflow',
            ha='center', va='center', fontsize=16, fontweight='bold', color=PRIMARY_COLOR)

    # Add subtitle
    ax.text(7, 5, 'From Raw Data to Actionable Insights',
            ha='center', va='center', fontsize=11, color=SECONDARY_COLOR, style='italic')

    plt.tight_layout()
    plt.savefig('assets/workflow_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Generated workflow_diagram.png")

def create_gap_matrix_visual():
    """Create visual representation of research gap matrix"""
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Title
    ax.text(5, 7.5, 'Research Gap Analysis: Existing vs Proposed System',
            ha='center', va='center', fontsize=16, fontweight='bold', color=PRIMARY_COLOR)

    # Features and status
    features = [
        "Crop Yield Prediction",
        "Irrigation Prediction",
        "Risk Assessment",
        "Explainable AI (SHAP)",
        "IoT Integration",
        "Interactive Dashboard",
        "Digital Twin Simulation",
        "What-If Analysis",
        "Scenario Simulation"
    ]

    # Existing (✓/✗) - based on Part_B_PPT_Content.md
    existing = [True, False, True, True, True, False, False, False, False]
    # Proposed (all ✓)
    proposed = [True] * 9

    # Draw table
    y_start = 6
    row_height = 0.6

    # Headers
    ax.text(1.5, y_start + 0.2, "Feature", ha='left', va='center',
            fontsize=11, fontweight='bold', color=PRIMARY_COLOR)
    ax.text(4.5, y_start + 0.2, "Existing Papers", ha='center', va='center',
            fontsize=11, fontweight='bold', color=SECONDARY_COLOR)
    ax.text(7.5, y_start + 0.2, "Proposed System", ha='center', va='center',
            fontsize=11, fontweight='bold', color=ACCENT_COLOR)

    # Draw horizontal line under header
    ax.plot([1, 9], [y_start, y_start], color=SECONDARY_COLOR, linewidth=1.5)

    # Draw rows
    for i, (feature, exist, prop) in enumerate(zip(features, existing, proposed)):
        y = y_start - (i+1)*row_height

        # Feature name
        ax.text(1.5, y, feature, ha='left', va='center', fontsize=10)

        # Existing status
        exist_symbol = "✓" if exist else "✗"
        exist_color = ACCENT_COLOR if exist else SECONDARY_COLOR
        ax.text(4.5, y, exist_symbol, ha='center', va='center',
                fontsize=14, fontweight='bold', color=exist_color)

        # Proposed status
        prop_symbol = "✓" if prop else "✗"
        prop_color = ACCENT_COLOR if prop else SECONDARY_COLOR
        ax.text(7.5, y, prop_symbol, ha='center', va='center',
                fontsize=14, fontweight='bold', color=prop_color)

        # Horizontal line
        if i < len(features) - 1:
            ax.plot([1, 9], [y - row_height/2, y - row_height/2],
                    color=SECONDARY_COLOR, linewidth=0.5, linestyle=':')

    # Add explanation box
    explanation = (
        "✓ Indicates capability present\n"
        "✗ Indicates capability missing/limited\n"
        "Gap areas (✗ → ✓) represent our novel contributions"
    )
    props = dict(boxstyle='round,pad=0.5', facecolor='#FFF8E1', alpha=0.9, edgecolor=PRIMARY_COLOR)
    ax.text(5, 1.5, explanation, ha='center', va='center', fontsize=10,
            bbox=props, color=SECONDARY_COLOR)

    plt.tight_layout()
    plt.savefig('assets/gap_matrix_visual.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Generated gap_matrix_visual.png")

def main():
    """Generate all charts"""
    print("Generating charts for enhanced PowerPoint...")
    print("=" * 50)

    create_feature_importance_chart()
    create_metrics_comparison_chart()
    create_digital_twin_diagram()
    create_workflow_diagram()
    create_gap_matrix_visual()

    print("=" * 50)
    print("✅ All charts generated successfully!")
    print("📁 Charts saved in: ./assets/")
    print("\nGenerated files:")
    for f in sorted(os.listdir('assets')):
        print(f"  - {f}")

if __name__ == "__main__":
    main()

import os

 

import datetime as dt

 

import streamlit as st

 

import pandas as pd

 

import numpy as np

 

import re

 

# Database integration imports

from streamlit_integration import load_dashboard_data, show_data_refresh_section

 


 

st.set_page_config(layout="wide", page_title="🚀 DevOps Gamification Dashboard", page_icon="🏆")

 


 

# --- HSBC Design System CSS ---

st.markdown("""<style>

/* Import HSBC-compatible Font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;700&display=swap');

/* Global Styles */
* {
    font-family: 'Inter', 'Univers Next for HSBC', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Remove Streamlit Branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}
header {visibility: hidden;}

/* Hide sidebar by default */
[data-testid="stSidebar"] {
    display: none;
}

/* Main Container - HSBC Clean White */
.main {
    background: #FFFFFF;
    padding: 0;
}

.stApp {
    background: #FFFFFF;
}

/* HSBC Text Styling */
.stMarkdown, .stText {
    color: #2D2D2D;
}

h1, h2, h3, h4, h5, h6 {
    color: #2D2D2D !important;
    font-weight: 400;
}

p {
    color: #2D2D2D;
    font-size: 14px;
}

 

/* HSBC Expander Styling - Clean Design */
.streamlit-expanderHeader {
    background: white;
    border-radius: 0;
    color: #2D2D2D !important;
    font-weight: 400;
    border: 1px solid #E5E5E5;
    font-size: 13px;
}

.streamlit-expanderHeader p {
    color: #2D2D2D !important;
}

.streamlit-expanderContent {
    background: #FAFAFA;
    border-radius: 0;
    color: #2D2D2D !important;
    border: 1px solid #E5E5E5;
    border-top: none;
}

.streamlit-expanderContent div {
    color: #2D2D2D !important;
}

 

/* HSBC Chart Styling */
.stVegaLiteChart {
    background: white;
    border-radius: 0;
    padding: 20px;
    border: 1px solid #E5E5E5;
    box-shadow: none;
}

 

/* Make chart canvas visible */

canvas {

    background: white !important;

}

 

/* Vega chart container */

.vega-embed {

    background: white;

    border-radius: 10px;

    padding: 10px;

}

 

.vega-embed summary {

    color: #333 !important;

}

 

/* HSBC Multiselect Tags - Clean Design */
[data-baseweb="tag"] {
    background: #DB0011;
    color: white;
    border-radius: 2px;
    font-size: 12px;
    padding: 4px 8px;
}

 

/* HSBC Table Styling - Clean Design */
.stDataFrame {
    background: white !important;
    border-radius: 0 !important;
    padding: 0 !important;
    border: 1px solid #E5E5E5 !important;
}

.stDataFrame > div {
    background: white !important;
}

.stDataFrame [data-testid="stDataFrameResizable"] {
    background: white !important;
}

.stDataFrame table {
    color: #2D2D2D !important;
    font-size: 13px !important;
    border-collapse: collapse !important;
    background: white !important;
}

.stDataFrame th {
    background: #F5F5F5 !important;
    color: #2D2D2D !important;
    font-weight: 500 !important;
    padding: 12px 16px !important;
    border-bottom: 2px solid #E5E5E5 !important;
    text-align: left !important;
}

.stDataFrame td {
    color: #2D2D2D !important;
    padding: 12px 16px !important;
    border-bottom: 1px solid #EEEEEE !important;
    font-weight: 400 !important;
    background: white !important;
}

.stDataFrame tbody tr:hover td {
    background: #F9F9F9 !important;
}

/* Glide Data Grid (Streamlit's new table) */
[data-testid="stDataFrame"] canvas {
    background: white !important;
}

[data-testid="stDataFrame"] > div > div {
    background: white !important;
}

/* Fix for glide-data-grid cells */
.dvn-scroller {
    background: white !important;
}

.gdg-style {
    --gdg-bg-cell: white !important;
    --gdg-bg-header: #F5F5F5 !important;
    --gdg-text-dark: #2D2D2D !important;
    --gdg-text-medium: #666666 !important;
    --gdg-border-color: #E5E5E5 !important;
}

/* Additional table fixes for Streamlit data editor */
[data-testid="stDataFrame"] {
    background: white !important;
}

[data-testid="stDataFrame"] * {
    color: #2D2D2D !important;
}

[data-testid="stDataFrame"] [role="grid"] {
    background: white !important;
}

[data-testid="stDataFrame"] [role="columnheader"] {
    background: #F5F5F5 !important;
    color: #2D2D2D !important;
    font-weight: 500 !important;
}

[data-testid="stDataFrame"] [role="gridcell"] {
    background: white !important;
    color: #2D2D2D !important;
}

/* Fix input fields in main content */
.stTextInput input,
.stNumberInput input,
.stSelectbox select {
    background: white !important;
    color: #2D2D2D !important;
    border: 1px solid #E5E5E5 !important;
}

/* Fix select dropdown */
[data-baseweb="select"] {
    background: white !important;
}

[data-baseweb="select"] > div {
    background: white !important;
    color: #2D2D2D !important;
    border: 1px solid #E5E5E5 !important;
    border-radius: 2px !important;
}

/* Fix popover/dropdown menus */
[data-baseweb="popover"] {
    background: white !important;
}

[data-baseweb="menu"] {
    background: white !important;
}

[data-baseweb="menu"] li {
    color: #2D2D2D !important;
}

[data-baseweb="menu"] li:hover {
    background: #F5F5F5 !important;
}

/* Ensure all text is visible */
.element-container {
    color: #2D2D2D !important;
}

/* Fix metric styling */
[data-testid="stMetric"] {
    background: white !important;
    border: 1px solid #E5E5E5 !important;
    border-left: 3px solid #DB0011 !important;
    padding: 16px !important;
    border-radius: 0 !important;
}

[data-testid="stMetricLabel"] {
    color: #666666 !important;
}

[data-testid="stMetricValue"] {
    color: #2D2D2D !important;
}

/* Fix column layout */
[data-testid="column"] {
    background: transparent !important;
}

 

/* Animated Header */

.hero-header {

    background: rgba(45,55,72,0.3);

    padding: 40px;

    border-radius: 20px;

    text-align: center;

    margin-bottom: 30px;

    box-shadow: 0 8px 20px rgba(0,0,0,0.2);

    border: 1px solid rgba(255,255,255,0.05);

    animation: slideDown 0.8s ease-out;

    position: relative;

    overflow: hidden;

}

 

.hero-header::before {

    content: '';

    position: absolute;

    top: -50%;

    left: -50%;

    width: 200%;

    height: 200%;

    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);

    animation: rotate 20s linear infinite;

}

 

@keyframes rotate {

    from { transform: rotate(0deg); }

    to { transform: rotate(360deg); }

}

 

@keyframes slideDown {

    from {

        opacity: 0;

        transform: translateY(-50px);

    }

    to {

        opacity: 1;

        transform: translateY(0);

    }

}

 

.hero-title {

    font-size: 48px;

    font-weight: 800;

    color: white;

    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);

    margin: 0;

    position: relative;

    z-index: 1;

    animation: glow 2s ease-in-out infinite alternate;

}

 

@keyframes glow {

    from { text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #667eea; }

    to { text-shadow: 0 0 20px #fff, 0 0 30px #764ba2, 0 0 40px #764ba2; }

}

 

.hero-subtitle {

    font-size: 20px;

    color: rgba(255,255,255,0.9);

    margin-top: 10px;

    position: relative;

    z-index: 1;

}

 

/* Enhanced 3D Podium for Top 3 */

.podium-container {

    display: flex;

    justify-content: center;

    align-items: flex-end;

    gap: 30px;

    margin: 40px 0;

    padding: 40px 20px;

    perspective: 1000px;

    position: relative;

}

 

.podium-container::before {

    content: '';

    position: absolute;

    bottom: 0;

    left: 50%;

    transform: translateX(-50%);

    width: 80%;

    height: 20px;

    background: radial-gradient(ellipse at center, rgba(0,0,0,0.3) 0%, transparent 70%);

    border-radius: 50%;

}

 

.podium-place {

    text-align: center;

    animation: podiumRise 1s ease-out;

    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);

    position: relative;

}

 

.podium-place:hover {

    transform: translateY(-15px) scale(1.05);

}

 

@keyframes podiumRise {

    0% {

        transform: translateY(100px) scale(0.8);

        opacity: 0;

    }

    60% {

        transform: translateY(-10px) scale(1.05);

    }

    100% {

        transform: translateY(0) scale(1);

        opacity: 1;

    }

}

 

.podium-rank-1 {

    order: 2;

    animation-delay: 0.2s;

}

 

.podium-rank-2 {

    order: 1;

    animation-delay: 0s;

}

 

.podium-rank-3 {

    order: 3;

    animation-delay: 0.4s;

}

 

/* Trophy/Medal Avatar */

.podium-avatar {

    width: 110px;

    height: 110px;

    border-radius: 50%;

    background: linear-gradient(135deg, #ffd700, #ffed4e);

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 45px;

    margin: 0 auto -20px auto;

    box-shadow:

        0 15px 35px rgba(255,215,0,0.4),

        0 5px 15px rgba(0,0,0,0.3),

        inset 0 -5px 15px rgba(0,0,0,0.2);

    border: 5px solid white;

    position: relative;

    z-index: 10;

    animation: float 3s ease-in-out infinite;

}

 

@keyframes float {

    0%, 100% { transform: translateY(0px); }

    50% { transform: translateY(-10px); }

}

 

.podium-rank-1 .podium-avatar {

    width: 130px;

    height: 130px;

    font-size: 55px;

    background: linear-gradient(135deg, #ffd700, #ffed4e, #ffd700);

    box-shadow:

        0 20px 50px rgba(255,215,0,0.6),

        0 10px 25px rgba(0,0,0,0.3),

        inset 0 -5px 20px rgba(0,0,0,0.2),

        0 0 30px rgba(255,215,0,0.5);

    animation: float 3s ease-in-out infinite, goldGlow 2s ease-in-out infinite alternate;

}

 

@keyframes goldGlow {

    from {

        box-shadow:

            0 20px 50px rgba(255,215,0,0.6),

            0 10px 25px rgba(0,0,0,0.3),

            inset 0 -5px 20px rgba(0,0,0,0.2),

            0 0 30px rgba(255,215,0,0.5);

    }

    to {

        box-shadow:

            0 20px 60px rgba(255,215,0,0.8),

            0 10px 25px rgba(0,0,0,0.3),

            inset 0 -5px 20px rgba(0,0,0,0.2),

            0 0 50px rgba(255,215,0,0.8);

    }

}

 

.podium-rank-2 .podium-avatar {

    background: linear-gradient(135deg, #e8e8e8, #c0c0c0, #e8e8e8);

    box-shadow:

        0 15px 35px rgba(192,192,192,0.5),

        0 5px 15px rgba(0,0,0,0.3),

        inset 0 -5px 15px rgba(0,0,0,0.15);

}

 

.podium-rank-3 .podium-avatar {

    background: linear-gradient(135deg, #e8a87c, #cd7f32, #e8a87c);

    box-shadow:

        0 15px 35px rgba(205,127,50,0.5),

        0 5px 15px rgba(0,0,0,0.3),

        inset 0 -5px 15px rgba(0,0,0,0.15);

}

 

/* 3D Podium Base */

.podium-base {

    background: linear-gradient(135deg, #667eea, #764ba2);

    border-radius: 15px 15px 0 0;

    padding: 30px 20px 20px;

    color: white;

    box-shadow:

        0 20px 40px rgba(0,0,0,0.4),

        inset 0 -3px 10px rgba(0,0,0,0.2),

        inset 0 3px 10px rgba(255,255,255,0.1);

    position: relative;

    overflow: hidden;

}

 

.podium-base::before {

    content: '';

    position: absolute;

    top: 0;

    left: 0;

    right: 0;

    height: 4px;

    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);

}

 

.podium-base::after {

    content: '';

    position: absolute;

    bottom: 0;

    left: 0;

    right: 0;

    height: 30px;

    background: linear-gradient(to bottom, transparent, rgba(0,0,0,0.2));

}

 

.podium-rank-1 .podium-base {

    height: 200px;

    background: rgba(96,165,250,0.25);

    box-shadow:

        0 15px 30px rgba(0,0,0,0.3),

        inset 0 -3px 10px rgba(0,0,0,0.2),

        inset 0 3px 10px rgba(255,255,255,0.08);

    border: 1px solid rgba(96,165,250,0.3);

}

 

.podium-rank-2 .podium-base {

    height: 150px;

    background: rgba(74,85,104,0.25);

    box-shadow:

        0 15px 30px rgba(0,0,0,0.3),

        inset 0 -3px 10px rgba(0,0,0,0.2),

        inset 0 3px 10px rgba(255,255,255,0.08);

    border: 1px solid rgba(148,163,184,0.2);

}

 

.podium-rank-3 .podium-base {

    height: 120px;

    background: rgba(74,85,104,0.2);

    box-shadow:

        0 15px 30px rgba(0,0,0,0.3),

        inset 0 -3px 10px rgba(0,0,0,0.2),

        inset 0 3px 10px rgba(255,255,255,0.08);

    border: 1px solid rgba(148,163,184,0.15);

}

 

.podium-team-name {

    font-weight: 800;

    font-size: 19px;

    margin: 15px 0 8px;

    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);

    position: relative;

    z-index: 1;

}

 

.podium-score {

    font-size: 28px;

    font-weight: 900;

    color: #ffd700;

    text-shadow:

        2px 2px 4px rgba(0,0,0,0.4),

        0 0 10px rgba(255,215,0,0.5);

    position: relative;

    z-index: 1;

}

 

.podium-rank-badge {

    position: absolute;

    top: 10px;

    right: 10px;

    background: rgba(255,255,255,0.2);

    backdrop-filter: blur(10px);

    border-radius: 50%;

    width: 40px;

    height: 40px;

    display: flex;

    align-items: center;

    justify-content: center;

    font-weight: 800;

    font-size: 18px;

    border: 2px solid rgba(255,255,255,0.3);

}

 

/* Metric Cards */

.metric-card {

    background: rgba(45,55,72,0.2);

    backdrop-filter: blur(10px);

    border-radius: 15px;

    padding: 25px;

    text-align: center;

    box-shadow: 0 4px 15px rgba(0,0,0,0.15);

    border: 1px solid rgba(255,255,255,0.08);

    transition: all 0.3s ease;

    animation: fadeIn 0.6s ease-out;

}

 

.metric-card:hover {

    transform: translateY(-5px);

    box-shadow: 0 12px 40px rgba(0,0,0,0.3);

}

 

@keyframes fadeIn {

    from { opacity: 0; transform: translateY(20px); }

    to { opacity: 1; transform: translateY(0); }

}

 

.metric-value {

    font-size: 48px;

    font-weight: 800;

    color: #93c5fd;

}

 

.metric-label {

    font-size: 14px;

    color: rgba(255,255,255,0.8);

    text-transform: uppercase;

    letter-spacing: 1px;

    margin-top: 5px;

}

 

/* Progress Ring */

.progress-ring {

    width: 150px;

    height: 150px;

    margin: 0 auto;

}

 

.progress-ring-circle {

    transition: stroke-dashoffset 0.5s ease;

    transform: rotate(-90deg);

    transform-origin: 50% 50%;

}

 

/* Team Card */

.team-card {

    background: rgba(45,55,72,0.2);

    backdrop-filter: blur(10px);

    border-radius: 15px;

    padding: 20px;

    margin: 10px 0;

    box-shadow: 0 4px 15px rgba(0,0,0,0.15);

    border: 1px solid rgba(255,255,255,0.08);

    transition: all 0.3s ease;

    animation: slideIn 0.5s ease-out;

}

 

.team-card:hover {

    transform: translateX(5px);

    box-shadow: 0 6px 20px rgba(0,0,0,0.2);

    border-color: rgba(255,255,255,0.15);

}

 

@keyframes slideIn {

    from { opacity: 0; transform: translateX(-50px); }

    to { opacity: 1; transform: translateX(0); }

}

 

.team-rank {

    font-size: 48px;

    font-weight: 800;

    background: linear-gradient(135deg, #ffd700, #ffed4e);

    -webkit-background-clip: text;

    -webkit-text-fill-color: transparent;

    background-clip: text;

    display: inline-block;

    min-width: 60px;

}

 

.team-name {

    font-size: 24px;

    font-weight: 700;

    color: white;

    margin: 0 0 10px 0;

}

 

.team-stats {

    display: flex;

    gap: 15px;

    margin-top: 15px;

}

 

.stat-pill {

    background: rgba(255,255,255,0.1);

    padding: 8px 15px;

    border-radius: 20px;

    font-size: 14px;

    color: white;

    border: 1px solid rgba(255,255,255,0.2);

}

 

/* Badge Enhancements */

.badge {

    display: inline-block;

    background: rgba(96,165,250,0.2);

    color: white;

    padding: 8px 16px;

    border-radius: 20px;

    margin: 4px;

    font-size: 14px;

    font-weight: 600;

    border: 1px solid rgba(96,165,250,0.4);

    transition: all 0.3s ease;

    animation: badgePop 0.5s ease-out;

}

 

.badge:hover {

    transform: scale(1.1) rotate(5deg);

    box-shadow: 0 6px 20px rgba(102,126,234,0.6);

}

 

@keyframes badgePop {

    0% { transform: scale(0); }

    50% { transform: scale(1.2); }

    100% { transform: scale(1); }

}

 

.badge-gold {

    background: rgba(255,215,0,0.15);

    border: 1px solid rgba(255,215,0,0.3);

    box-shadow: 0 2px 8px rgba(0,0,0,0.15);

}

 

.badge-silver {

    background: rgba(192,192,192,0.15);

    color: white;

    border: 1px solid rgba(192,192,192,0.3);

    box-shadow: 0 2px 8px rgba(0,0,0,0.15);

}

 

.badge-bronze {

    background: rgba(205,127,50,0.15);

    border: 1px solid rgba(205,127,50,0.3);

    box-shadow: 0 2px 8px rgba(0,0,0,0.15);

}

 

/* Tier Badge */

.tier-badge {

    display: inline-block;

    padding: 10px 20px;

    border-radius: 25px;

    color: white;

    font-weight: 700;

    font-size: 18px;

    box-shadow: 0 2px 8px rgba(0,0,0,0.2);

    border: 1px solid rgba(255,255,255,0.1);

}

 

 

/* Score Card */

.score-card {

    background: linear-gradient(135deg, rgba(74,85,104,0.4), rgba(45,55,72,0.4));

    color: white;

    padding: 30px;

    border-radius: 20px;

    box-shadow: 0 10px 40px rgba(0,0,0,0.3);

    animation: fadeIn 0.8s ease-out;

}

 

.score-row {

    display: flex;

    gap: 15px;

    align-items: center;

}

 

.score-pill {

    background: rgba(255,255,255,0.15);

    padding: 10px 15px;

    border-radius: 15px;

    backdrop-filter: blur(10px);

}

 

.metric-bar {

    height: 12px;

    border-radius: 10px;

    background: rgba(255,255,255,0.2);

    overflow: hidden;

    box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);

}

 

.metric-fill {

    height: 12px;

    border-radius: 10px;

    transition: width 1s ease-out;

    box-shadow: 0 0 10px currentColor;

}

 

/* Leaderboard Table */

.leaderboard-row {

    background: rgba(45,55,72,0.2);

    backdrop-filter: blur(10px);

    border-radius: 12px;

    padding: 15px;

    margin: 10px 0;

    border: 1px solid rgba(255,255,255,0.08);

    transition: all 0.3s ease;

}

 

.leaderboard-row:hover {

    transform: translateX(5px);

    background: rgba(45,55,72,0.3);

    box-shadow: 0 4px 15px rgba(0,0,0,0.2);

    border-color: rgba(255,255,255,0.12);

}

 

/* Rank Change Indicator */

.rank-up {

    color: #10b981;

    font-weight: 700;

    animation: slideUp 0.5s ease-out;

}

 

.rank-down {

    color: #ef4444;

    font-weight: 700;

    animation: slideDown 0.5s ease-out;

}

 

@keyframes slideUp {

    from { transform: translateY(10px); opacity: 0; }

    to { transform: translateY(0); opacity: 1; }

}

 

/* Confetti Effect */

.confetti {

    position: fixed;

    width: 10px;

    height: 10px;

    background: #ffd700;

    position: absolute;

    animation: confetti-fall 3s linear infinite;

}

 

@keyframes confetti-fall {

    to {

        transform: translateY(100vh) rotate(360deg);

        opacity: 0;

    }

}

 

/* Achievement Card */

.achievement-card {

    background: rgba(45,55,72,0.2);

    border-radius: 15px;

    padding: 25px;

    color: white;

    box-shadow: 0 4px 15px rgba(0,0,0,0.15);

    margin: 15px 0;

    border: 1px solid rgba(255,255,255,0.06);

    animation: achievementPop 0.6s ease-out;

}

 

@keyframes achievementPop {

    0% { transform: scale(0) rotate(-180deg); opacity: 0; }

    50% { transform: scale(1.1) rotate(10deg); }

    100% { transform: scale(1) rotate(0); opacity: 1; }

}

 

.achievement-icon {

    font-size: 60px;

    text-align: center;

    margin-bottom: 15px;

    animation: bounce 2s ease-in-out infinite;

}

 

@keyframes bounce {

    0%, 100% { transform: translateY(0); }

    50% { transform: translateY(-20px); }

}

 

/* Doc Tile */

.doc-tile {

    background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));

    backdrop-filter: blur(10px);

    border-radius: 15px;

    padding: 20px;

    border: 1px solid rgba(255,255,255,0.18);

    margin: 10px 0;

    transition: all 0.3s ease;

}

 

.doc-tile:hover {

    transform: translateY(-5px);

    box-shadow: 0 10px 30px rgba(0,0,0,0.3);

}

 

.small-metric {

    font-size: 12px;

    color: rgba(255,255,255,0.7);

    margin-top: 5px;

}

 

/* Streamlit Overrides */

.stTabs [data-baseweb="tab-list"] {

    gap: 10px;

    background: rgba(255,255,255,0.05);

    padding: 10px;

    border-radius: 15px;

}

 

.stTabs [data-baseweb="tab"] {

    background: rgba(255,255,255,0.1);

    border-radius: 10px;

    color: white;

    font-weight: 600;

    padding: 10px 20px;

    transition: all 0.3s ease;

}

 

.stTabs [aria-selected="true"] {

    background: rgba(96,165,250,0.2);

    border: 1px solid rgba(96,165,250,0.3);

    box-shadow: 0 2px 8px rgba(0,0,0,0.15);

}

 

.stButton > button {

    background: rgba(96,165,250,0.2);

    color: white;

    border: 1px solid rgba(96,165,250,0.3);

    border-radius: 25px;

    padding: 12px 30px;

    font-weight: 600;

    transition: all 0.3s ease;

    box-shadow: 0 2px 8px rgba(0,0,0,0.15);

}

 

.stButton > button:hover {

    transform: translateY(-2px);

    background: rgba(96,165,250,0.3);

    box-shadow: 0 4px 12px rgba(0,0,0,0.2);

}

 

.stDataFrame {

    background: rgba(255,255,255,0.05);

    border-radius: 15px;

    padding: 10px;

}

 

/* Sparkle Effect */

.sparkle {

    position: relative;

    display: inline-block;

}

 

.sparkle::before {

    content: '✨';

    position: absolute;

    top: -10px;

    right: -10px;

    animation: sparkle 1.5s ease-in-out infinite;

}

 

@keyframes sparkle {

    0%, 100% { opacity: 0; transform: scale(0); }

    50% { opacity: 1; transform: scale(1); }

}

 

/* Data Quality Badge - Sidebar */

.sidebar-quality-badge {

    margin-top: 20px;

    cursor: pointer;

    transition: all 0.3s ease;

}

 

.sidebar-quality-badge:hover {

    transform: translateY(-2px);

}

 

.quality-indicator {

    background: linear-gradient(135deg, rgba(255,255,255,0.15), rgba(255,255,255,0.05));

    backdrop-filter: blur(10px);

    border-radius: 15px;

    padding: 15px;

    border: 2px solid;

    box-shadow: 0 4px 15px rgba(0,0,0,0.3);

    color: white;

    transition: all 0.3s ease;

}

 

.quality-indicator:hover {

    box-shadow: 0 6px 20px rgba(0,0,0,0.4);

}

 

.quality-indicator.green {

    border-color: #10b981;

    background: linear-gradient(135deg, rgba(16,185,129,0.2), rgba(5,150,105,0.1));

}

 

.quality-indicator.yellow {

    border-color: #f59e0b;

    background: linear-gradient(135deg, rgba(245,158,11,0.2), rgba(217,119,6,0.1));

}

 

.quality-indicator.red {

    border-color: #ef4444;

    background: linear-gradient(135deg, rgba(239,68,68,0.2), rgba(220,38,38,0.1));

}

 

.quality-header {

    display: flex;

    align-items: center;

    gap: 10px;

    font-weight: 700;

    font-size: 15px;

    margin-bottom: 10px;

}

 

.quality-details {

    font-size: 12px;

    color: rgba(255,255,255,0.8);

    line-height: 1.6;

}

 

.quality-details ul {

    margin: 5px 0 0 0;

    padding-left: 20px;

}

 

.quality-details li {
    margin-bottom: 5px;
}

/* HSBC Button Styling - Clean Design */
.stButton > button {
    background: #DB0011;
    color: white;
    border: none;
    border-radius: 2px;
    padding: 8px 20px;
    font-weight: 400;
    font-size: 13px;
    transition: background 0.2s ease;
    box-shadow: none;
}

.stButton > button:hover {
    background: #C00010;
    box-shadow: none;
}

/* HSBC Tab Styling - Clean Design */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: white;
    border-bottom: 1px solid #E5E5E5;
    padding: 0;
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #666666;
    padding: 12px 20px;
    font-size: 13px;
    font-weight: 400;
    border-bottom: 2px solid transparent;
    margin-bottom: -1px;
}

.stTabs [data-baseweb="tab"]:hover {
    background: transparent;
    color: #2D2D2D;
}

.stTabs [aria-selected="true"] {
    background: transparent !important;
    color: #2D2D2D !important;
    border-bottom: 2px solid #DB0011 !important;
    font-weight: 400 !important;
}

/* HSBC Metric Cards - Clean Design */
.stMetric {
    background: white;
    border: 1px solid #E5E5E5;
    border-left: 3px solid #DB0011;
    border-radius: 0;
    padding: 16px;
    box-shadow: none;
}

.stMetric label {
    color: #666666 !important;
    font-size: 13px !important;
    font-weight: 400 !important;
}

.stMetric [data-testid="stMetricValue"] {
    color: #2D2D2D !important;
    font-size: 28px !important;
    font-weight: 400 !important;
}

.stMetric [data-testid="stMetricDelta"] {
    font-size: 13px !important;
}

/* HSBC Select/Dropdown - Clean Design */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: white;
    border: 1px solid #E5E5E5;
    border-radius: 2px;
}

.stSelectbox label,
.stMultiSelect label {
    color: #2D2D2D !important;
    font-weight: 400 !important;
    font-size: 13px !important;
}

.stSelectbox [data-baseweb="select"],
.stMultiSelect [data-baseweb="select"] {
    font-size: 13px !important;
}

/* HSBC Download Button - Clean Design */
.stDownloadButton > button {
    background: #2D2D2D;
    color: white;
    border: none;
    border-radius: 2px;
    padding: 8px 20px;
    font-weight: 400;
    font-size: 13px;
    box-shadow: none;
}

.stDownloadButton > button:hover {
    background: #1A1A1A;
}

</style>

""", unsafe_allow_html=True)

 

# --- HSBC Navigation Header with App Tabs ---

# Create session state for tab selection
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 'Overview'

st.markdown("""
<div style='background: #2D2D2D; padding: 0; margin: -1rem -1rem 0 -1rem;'>
    <div style='display: flex; align-items: center; padding: 12px 24px;'>
        <div style='display: flex; align-items: center; gap: 8px; margin-right: 40px;'>
            <svg width="24" height="24" viewBox="0 0 24 24" style="fill: #DB0011;">
                <rect width="24" height="12" fill="#DB0011"/>
                <rect y="12" width="24" height="12" fill="white"/>
            </svg>
            <span style='color: white; font-size: 18px; font-weight: 700; letter-spacing: 4px;'>HSBC</span>
        </div>
        <div style='display: flex; gap: 0; align-items: center;'>
            <div id="tab-overview" style='color: white; font-size: 13px; font-weight: 400; padding: 12px 20px; cursor: pointer; border-bottom: 2px solid #DB0011;'>🏁 Overview</div>
            <div id="tab-leaderboard" style='color: #999999; font-size: 13px; font-weight: 400; padding: 12px 20px; cursor: pointer; border-bottom: 2px solid transparent;'>🏆 Leaderboard</div>
            <div id="tab-badges" style='color: #999999; font-size: 13px; font-weight: 400; padding: 12px 20px; cursor: pointer; border-bottom: 2px solid transparent;'>🎖️ Badges</div>
            <div id="tab-teams" style='color: #999999; font-size: 13px; font-weight: 400; padding: 12px 20px; cursor: pointer; border-bottom: 2px solid transparent;'>📊 Team Trends</div>
            <div id="tab-docs" style='color: #999999; font-size: 13px; font-weight: 400; padding: 12px 20px; cursor: pointer; border-bottom: 2px solid transparent;'>📘 Docs</div>
        </div>
    </div>
</div>
<div style='background: white; padding: 20px 24px; margin: 0 -1rem 20px -1rem; border-bottom: 1px solid #E5E5E5;'>
    <h1 style='color: #2D2D2D; font-size: 22px; font-weight: 400; margin: 0;'>DevOps Transformation Dashboard</h1>
    <p style='color: #666666; font-size: 13px; margin: 8px 0 0 0;'>Track team performance and DevOps maturity metrics | Target: RF 280 | LTTD 1.8</p>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const tabs = ['overview', 'leaderboard', 'badges', 'teams', 'docs'];
    
    tabs.forEach(tab => {
        const element = document.getElementById('tab-' + tab);
        if (element) {
            element.addEventListener('click', function() {
                // Reset all tabs
                tabs.forEach(t => {
                    const el = document.getElementById('tab-' + t);
                    if (el) {
                        el.style.color = '#999999';
                        el.style.borderBottom = '2px solid transparent';
                    }
                });
                
                // Activate clicked tab
                this.style.color = 'white';
                this.style.borderBottom = '2px solid #DB0011';
                
                // Store active tab (you'll need to handle this with Streamlit)
                window.parent.postMessage({type: 'tab-change', tab: tab}, '*');
            });
        }
    });
});
</script>
""", unsafe_allow_html=True)

# Tab selection buttons (hidden but functional)
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("Overview", key="btn_overview", help="Overview tab"):
        st.session_state.active_tab = 'Overview'
with col2:
    if st.button("Leaderboard", key="btn_leaderboard", help="Leaderboard tab"):
        st.session_state.active_tab = 'Leaderboard'
with col3:
    if st.button("Badges", key="btn_badges", help="Badges tab"):
        st.session_state.active_tab = 'Badges'
with col4:
    if st.button("Team Trends", key="btn_teams", help="Team Trends tab"):
        st.session_state.active_tab = 'Team Trends'
with col5:
    if st.button("Docs", key="btn_docs", help="Docs tab"):
        st.session_state.active_tab = 'Docs'

# Hide the buttons with CSS
st.markdown("""
<style>
[data-testid="column"]:has([title="Overview tab"]),
[data-testid="column"]:has([title="Leaderboard tab"]),
[data-testid="column"]:has([title="Badges tab"]),
[data-testid="column"]:has([title="Team Trends tab"]),
[data-testid="column"]:has([title="Docs tab"]) {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

 

 


 

# --- DPI Calculation Functions ---
# NOTE: DPI is now calculated in metrics_calculator.py and stored in database
# The UI reads scores directly from the database - no recalculation needed

 


 

# --- CSV schema and validation ---

 

REQUIRED_COLUMNS = [

 

    'Team','Week','RF','LTTD','LTTD_Measurable','CFR','MTTR','Priv_Access',

 

    'CI','CD','IaC','Rollback','Self_Service','CFR_Reported','Automation_Audited',

 

    'Critical_Data_Present','Stack','Business Unit'

 

]

 


 

def parse_bool(x):

 

    if pd.isna(x):

 

        return False

 

    if isinstance(x, bool):

 

        return x

 

    s = str(x).strip().lower()

 

    return s in ('1','true','t','yes','y')

 


 

def validate_and_normalize(df):

 

    errors = []

 

    # check columns

 

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]

 

    if missing:

 

        errors.append(f"Missing required columns: {missing}")

 

        return None, errors

 


 

    df = df.copy()

 

    # parse Week as date (start of ISO week)

 

    try:

 

        df['Week'] = pd.to_datetime(df['Week'])

 

        # normalize to week start for grouping

 

        df['Week_Start'] = df['Week'].dt.to_period('W').apply(lambda r: r.start_time)

 

    except Exception as e:

 

        errors.append(f"Invalid Week column: {e}")

 

        return None, errors

 


 

    # types and ranges

 

    df['RF'] = pd.to_numeric(df['RF'], errors='coerce').fillna(0).astype(int)

 

    df['LTTD'] = pd.to_numeric(df['LTTD'], errors='coerce').fillna(9999).astype(float)

 

    df['LTTD_Measurable'] = pd.to_numeric(df['LTTD_Measurable'], errors='coerce').fillna(1.0).astype(float)

 

    df['CFR'] = pd.to_numeric(df['CFR'], errors='coerce').fillna(1.0).astype(float)

 

    df['MTTR'] = pd.to_numeric(df['MTTR'], errors='coerce').fillna(999.0).astype(float)

 

    df['Priv_Access'] = pd.to_numeric(df['Priv_Access'], errors='coerce').fillna(0).astype(int)

 


 

    # booleans

 

    for b in ['CI','CD','IaC','Rollback','Self_Service','CFR_Reported','Automation_Audited','Critical_Data_Present']:

 

        df[b] = df[b].apply(parse_bool)

 


 

    # basic validations

 

    if (df['LTTD_Measurable'] < 0).any() or (df['LTTD_Measurable'] > 1).any():

 

        errors.append('LTTD_Measurable must be between 0 and 1')

 

    if (df['CFR'] < 0).any() or (df['CFR'] > 1).any():

 

        errors.append('CFR must be between 0 and 1')

 

    if not df['Priv_Access'].isin([0,1,2,3]).all():

 

        errors.append('Priv_Access must be 0,1,2 or 3')

 


 

    if errors:

 

        return None, errors

 


 

    # DPI fields now come from database - no computation needed
    # Database provides: DPI, Tier, Velocity, Flow, Stability, Automation, Quality_Security, AI_Adoption

 

    return df, []

 


 

# --- History persistence (single CSV with last 5 weeks) ---

 

HISTORY_FILE = os.path.join(os.path.dirname(__file__), 'metrics_history.csv')

 


 

def create_sample_history(path, teams=70, weeks=5):

 

    rows = []

 

    today = pd.Timestamp(dt.date.today())

 

    # get last `weeks` Monday starts

 

    week_starts = [(today - pd.Timedelta(days=today.weekday())) - pd.Timedelta(weeks=i) for i in reversed(range(weeks))]

 

    for ws in week_starts:

 

        for i in range(1, teams+1):

 

            row = {

 

                'Team': f'Team {i}',

 

                'Week': ws.strftime('%Y-%m-%d'),

 

                'RF': int(np.random.randint(10, 350)),

 

                'LTTD': round(np.random.uniform(1, 25), 1),

 

                'LTTD_Measurable': round(np.random.uniform(0.85, 1.0), 2),

 

                'CFR': round(np.random.uniform(0.01, 0.3), 2),

 

                'MTTR': round(np.random.uniform(0.5, 3), 1),

 

                'Priv_Access': int(np.random.randint(0,4)),

 

                'CI': np.random.choice([True, False]),

 

                'CD': np.random.choice([True, False]),

 

                'IaC': np.random.choice([True, False]),

 

                'Rollback': np.random.choice([True, False]),

 

                'Self_Service': np.random.choice([True, False]),

 

                'CFR_Reported': True,

 

                'Automation_Audited': True,

 

                'Critical_Data_Present': True,

 

                'Stack': np.random.choice(['Cloud Native','Hybrid','Legacy']),

 

                'Business Unit': np.random.choice(['BU A','BU B','BU C'])

 

            }

 

            rows.append(row)

 

    df = pd.DataFrame(rows)

 

    df_valid, errs = validate_and_normalize(df)

 

    if errs:

 

        st.warning('Sample history generation had validation issues: ' + '; '.join(errs))

 

    else:

 

        df_valid.to_csv(path, index=False)

 

    return df_valid

 


 

# OLD CSV-based loading (replaced with database)

# def load_history():

#     if os.path.exists(HISTORY_FILE):

#         hist = pd.read_csv(HISTORY_FILE, parse_dates=['Week','Week_Start'])

#         return hist

#     else:

#         return create_sample_history(HISTORY_FILE)

 

# NEW: Load data from database (real-time API data)

latest_df, history_df = load_dashboard_data()

 

# If no data in database, create sample data

if history_df.empty:

    st.warning('⚠️ No data in database. Please configure bearer tokens and refresh data.')

    history_df = create_sample_history(HISTORY_FILE)

 


 

# Data upload section removed - using history file only

 


 

# ensure history has Week_Start column

 

if 'Week_Start' not in history_df.columns:

 

    history_df['Week_Start'] = pd.to_datetime(history_df['Week']).dt.to_period('W').apply(lambda r: r.start_time)

 


 

# --- Compute latest-week leaderboard and Δ Rank ---

 

latest_week = history_df['Week_Start'].max()

 

prev_weeks = sorted(history_df['Week_Start'].unique())

 

prev_week = prev_weeks[-2] if len(prev_weeks) > 1 else None

 


 

latest_df = history_df[history_df['Week_Start'] == latest_week].copy()

 

latest_df = latest_df.sort_values(by='DPI', ascending=False).reset_index(drop=True)

 

latest_df['Rank'] = latest_df.index + 1

 


 

if prev_week is not None:

 

    prev_df = history_df[history_df['Week_Start'] == prev_week][['Team','DPI']].copy()

 

    prev_df['Prev_Rank'] = prev_df['DPI'].rank(method='min', ascending=False).astype(int)

 

    merged = latest_df.merge(prev_df[['Team','Prev_Rank']], on='Team', how='left')

 

    merged['Prev_Rank'] = merged['Prev_Rank'].fillna(len(latest_df)+1).astype(int)

 

    merged['Δ Rank'] = merged['Prev_Rank'] - merged['Rank']

 

    latest_df = merged

 

else:

 

    latest_df['Δ Rank'] = 0

 


 

# Prepare spark_hist for sparklines / trend charts

 

if 'Week_Start' not in history_df.columns:

 

    history_df['Week_Start'] = pd.to_datetime(history_df['Week']).dt.to_period('W').apply(lambda r: r.start_time)

 

try:

 

    spark_hist = history_df.pivot_table(index='Week_Start', columns='Team', values='DPI').sort_index()

 

except Exception:

 

    spark_hist = pd.DataFrame()

 


 

# --- Prepare badges and BU selection ---

 

# compute badges for latest_df

 

def compute_badges(df_row):

 

    badges = []

 

    # 6-PILLAR BADGE SYSTEM - One badge per pillar (≥70 threshold)
    
    # 1. Release Velocity (30%)
    release_velocity = df_row.get('Release_Velocity_Score', 0)
    if release_velocity is not None and release_velocity >= 70:
        badges.append('Velocity Champion')
    
    # 2. Git Hygiene (20%)
    git_hygiene = df_row.get('Git_Hygiene_Score', 0)
    if git_hygiene is not None and git_hygiene >= 70:
        badges.append('Code Quality')
    
    # 3. Pipeline Maturity (20%)
    pipeline_maturity = df_row.get('Pipeline_Maturity_Score', 0)
    if pipeline_maturity is not None and pipeline_maturity >= 70:
        badges.append('Automation Pro')
    
    # 4. Compliance (15%)
    compliance = df_row.get('Compliance_Score', 0)
    if compliance is not None and compliance >= 70:
        badges.append('Governance')
    
    # 5. Quality & Security (10%)
    quality_security = df_row.get('Quality_Security_Score', 0)
    if quality_security is not None and quality_security >= 70:
        badges.append('Security Shield')
    
    # 6. Adoption (5%)
    adoption = df_row.get('Adoption_Score', 0)
    if adoption is not None and adoption >= 70:
        badges.append('Innovation')

 

    return badges

 


 

latest_df['Badges'] = latest_df.apply(compute_badges, axis=1)

 


 

# Use all data for metrics (Business Unit filter removed)

 

metric_base = history_df

 


 

# UI helpers: CSS, badges, tier chips, tooltips

 

 


 

BADGE_ICONS = {

 

    'Release Champion': '🏆',

 

    'High Velocity': '⚡',

 

    'Flow Master': '💨',

 

    'Stability Shield': '🛡️',

 

    'Automation Pro': '🤖'

 

}

 

BADGE_DESC = {

 

    'Release Champion': 'RF ≥ 250 — exceptional delivery cadence',

 

    'High Velocity': 'RF ≥ 180 — high release frequency',

 

    'Flow Master': 'LTTD < 2 days — excellent flow',

 

    'Stability Shield': 'CFR < 5% — very stable releases',

 

    'Automation Pro': 'Full automation coverage — top automation maturity'

 

}

 


 

TIER_DESC = {

 

    'Elite': 'DPI ≥ 85: Elite — Continue scaling automation and reliability',

 

    'Advanced': '70–84: Advanced — Strong performance, optimize further',

 

    'Emerging': '50–69: Emerging — Improving but needs focus',

 

    'Needs Support': '<50: Needs Support — Prioritise friction removal',

 

    'Not Published': 'Critical data missing — score not published'

 

}

 


 

COLOR_MAP = {'Elite':'#16a34a','Advanced':'#2563eb','Emerging':'#f59e0b','Needs Support':'#ef4444','Not Published':'#6b7280'}

 


 

def badge_html(badge):

 

    icon = BADGE_ICONS.get(badge, '🔖')

 

    desc = BADGE_DESC.get(badge, '')

 

    return f"<span style='background: linear-gradient(135deg, #8b5cf6, #6366f1); padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; margin: 0 4px; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.2);' title='{desc}'>{icon} {badge}</span>"

 


 

def tier_html(tier, dpi=None):

 

    color = COLOR_MAP.get(tier, '#6b7280')

 

    desc = TIER_DESC.get(tier, '')

 

    dpi_text = f" ({dpi:.1f})" if dpi is not None and not pd.isna(dpi) else ''

 

    return f"<div style='padding: 8px 16px; border-radius: 20px; font-size: 14px; font-weight: 700; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.2); background:{color}' title='{desc}'>{tier}{dpi_text}</div>"

 


 

# Tabs layout (add Badges tab)

 

# one tabs declaration only (emoji labels)

 

# Replace Streamlit tabs with conditional content based on session state
# tab1, tab2, tab3, tab4, tab5 = st.tabs(['🏁 Overview','🏆 Leaderboard','🎖️ Badges','📈 Team Trends','📘 Docs'])

 


 

# compute display datasets (Business Unit filter removed)

 

display_history = history_df.copy()


 

# ---- Column name normalization (DB vs CSV) ----

# Some sources may provide score columns in lowercase (rf_score) while the UI expects Title Case (RF_Score).

# Normalize once so all downstream UI code consistently works.

_rename_scores = {

    'rf_score': 'RF_Score',

    'flow_score': 'Flow_Score',

    'cfr_score': 'CFR_Score',

    'mttr_score': 'MTTR_Score',

    'priv_score': 'Priv_Score',

    'automation_score': 'Automation_Score',

    'stability_score': 'Stability_Score',

}

display_history = display_history.rename(columns={k: v for k, v in _rename_scores.items() if k in display_history.columns})

 


 

# latest and previous for display

 

display_latest_week = display_history['Week_Start'].max()

# Convert to datetime if it's a string (from database date() function)
if isinstance(display_latest_week, str):
    display_latest_week = pd.to_datetime(display_latest_week)

 

display_prev_weeks = sorted(display_history['Week_Start'].unique())

 

display_prev_week = display_prev_weeks[-2] if len(display_prev_weeks) > 1 else None

 


 

display_latest_df = display_history[display_history['Week_Start'] == display_latest_week].copy()

# Remove duplicates - keep only the first occurrence of each team (highest DPI if sorted)
display_latest_df = display_latest_df.drop_duplicates(subset=['Team'], keep='first')

 

display_latest_df = display_latest_df.sort_values(by='DPI', ascending=False).reset_index(drop=True)

 

display_latest_df['Rank'] = display_latest_df.index + 1

 


 

if display_prev_week is not None:

 

    prev_df_disp = display_history[display_history['Week_Start'] == display_prev_week][['Team','DPI']].copy()

 

    prev_df_disp['Prev_Rank'] = prev_df_disp['DPI'].rank(method='min', ascending=False).astype(int)

 

    merged_disp = display_latest_df.merge(prev_df_disp[['Team','Prev_Rank']], on='Team', how='left')

 

    merged_disp['Prev_Rank'] = merged_disp['Prev_Rank'].fillna(len(display_latest_df)+1).astype(int)

 

    merged_disp['Δ Rank'] = merged_disp['Prev_Rank'] - merged_disp['Rank']

 

    display_latest_df = merged_disp

 

else:

 

    display_latest_df['Δ Rank'] = 0

 


 

# badges for display

 

display_latest_df['Badges'] = display_latest_df.apply(compute_badges, axis=1)

 


 

# spark_hist for display

 

try:

 

    spark_hist = display_history.pivot_table(index='Week_Start', columns='Team', values='DPI').sort_index()

 

except Exception:

 

    spark_hist = pd.DataFrame()

 


 

# data quality indicator (global for selected BU)

 

quality_flags = []

 

# Check if columns exist before accessing them

if 'Critical_Data_Present' in display_history.columns:

    if (display_history['Critical_Data_Present'] == False).any():

        quality_flags.append('Some teams missing critical data (scores hidden)')

 

if 'LTTD_Measurable' in display_history.columns:

    if (display_history['LTTD_Measurable'] < 0.9).any():

        quality_flags.append('Some teams have LTTD measurability <90% (flow capped)')

 

if 'CFR_Reported' in display_history.columns:

    if (display_history['CFR_Reported'] == False).any():

        quality_flags.append('Some teams not reporting CFR (stability capped)')

 


 

if quality_flags:

 

    quality_status = ('yellow' if len(quality_flags) < 3 else 'red', quality_flags)

 

else:

 

    quality_status = ('green', ['All critical data present'])

 

# Data quality indicator removed from sidebar

 


 

# prepare monthly averages for badges / top5

 

monthly_avg = display_history.groupby('Team')['DPI'].mean().reset_index().rename(columns={'DPI':'Monthly_Avg_DPI'})

 

monthly_sorted = monthly_avg.sort_values(by='Monthly_Avg_DPI', ascending=False)

 


 

# === OVERVIEW TAB ===
if st.session_state.active_tab == 'Overview':

    st.markdown(f"<h2 style='color:#2D2D2D; text-align:center; margin-bottom:30px;'>📊 Overview — Week of {display_latest_week.date()}</h2>", unsafe_allow_html=True)

 

    # Scoring summary in Overview tab

    with st.expander("📋 Scoring Summary (Quick Reference)", expanded=False):

        st.markdown("""<div style='color:white;'>

<ul style='color:white;'>

<li style='color:white; margin-bottom:10px;'><strong>Release Velocity</strong> — 20% weight (RF 50%, LTTD 50%)</li>

<li style='color:white; margin-bottom:10px;'><strong>Git Hygiene</strong> — 15% weight (Stale branches, Large PRs, Unreviewed PRs)</li>

<li style='color:white; margin-bottom:10px;'><strong>Pipeline Maturity</strong> — 20% weight (CI, CD, IaC, Rollback, Self-service)</li>

<li style='color:white; margin-bottom:10px;'><strong>Compliance</strong> — 15% weight (CFR reporting, Privileged access, Documentation)</li>

<li style='color:white; margin-bottom:10px;'><strong>Quality & Security</strong> — 15% weight (Code coverage, Security scanning, MTTR)</li>

<li style='color:white; margin-bottom:10px;'><strong>Adoption</strong> — 15% weight (Modern tooling, Best practices adoption)</li>

</ul>

<p style='color:rgba(255,255,255,0.7); margin-top:15px; font-size:13px;'>DPI = Weighted average of all 6 pillars (0-100 scale)</p>

</div>

        """, unsafe_allow_html=True)

 

    # top metrics for selected BU with animated cards
    
    # Re-inject critical CSS to ensure it's loaded (workaround for timing issues)
    st.markdown("""<style>
    .metric-card {
        background: rgba(45,55,72,0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(6,182,212,0.3);
        border-color: rgba(6,182,212,0.5);
    }
    .metric-value {
        font-size: 48px;
        font-weight: 800;
        background: linear-gradient(135deg, #06b6d4, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .metric-label {
        color: rgba(255,255,255,0.7);
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
    """, unsafe_allow_html=True)

 

    col1, col2, col3, col4 = st.columns(4)

 

    avg_dpi = display_history.groupby('Team')['DPI'].mean().mean()

    avg_rf = display_history.groupby('Team')['RF'].mean().mean()

    avg_lttd = display_history.groupby('Team')['LTTD'].mean().mean()

    pct = (display_history[display_history['Tier'].isin(['Elite','Advanced'])]['Team'].nunique() / display_history['Team'].nunique()) * 100

 

    with col1:

        avg_dpi_display = f"{avg_dpi:.1f}" if avg_dpi is not None and not pd.isna(avg_dpi) else "N/A"

        st.markdown(f"""<div style='background: rgba(45,55,72,0.2); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 25px; text-align: center; transition: all 0.3s ease; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
<div style='font-size: 48px; font-weight: 800; background: linear-gradient(135deg, #06b6d4, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;'>{avg_dpi_display}</div>
<div style='color: rgba(255,255,255,0.7); font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;'>🎯 Avg DPI</div>
</div>""", unsafe_allow_html=True)

 

    with col2:

        avg_rf_display = f"{avg_rf:.0f}" if avg_rf is not None and not pd.isna(avg_rf) else "N/A"

        st.markdown(f"""<div style='background: rgba(45,55,72,0.2); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 25px; text-align: center; transition: all 0.3s ease; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
<div style='font-size: 48px; font-weight: 800; background: linear-gradient(135deg, #06b6d4, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;'>{avg_rf_display}</div>
<div style='color: rgba(255,255,255,0.7); font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;'>⚡ Avg RF</div>
</div>""", unsafe_allow_html=True)

 

    with col3:

        avg_lttd_display = f"{avg_lttd:.1f}" if avg_lttd is not None and not pd.isna(avg_lttd) else "N/A"

        st.markdown(f"""<div style='background: rgba(45,55,72,0.2); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 25px; text-align: center; transition: all 0.3s ease; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
<div style='font-size: 48px; font-weight: 800; background: linear-gradient(135deg, #06b6d4, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;'>{avg_lttd_display}</div>
<div style='color: rgba(255,255,255,0.7); font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;'>⏱ Avg LTTD</div>
</div>""", unsafe_allow_html=True)

 

    with col4:

        st.markdown(f"""<div style='background: rgba(45,55,72,0.2); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 25px; text-align: center; transition: all 0.3s ease; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
<div style='font-size: 48px; font-weight: 800; background: linear-gradient(135deg, #06b6d4, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;'>{pct:.0f}%</div>
<div style='color: rgba(255,255,255,0.7); font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;'>🏆 Elite/Advanced</div>
</div>""", unsafe_allow_html=True)

 


 

    # Overall Statistics Graphs Section
    st.markdown("<h3 style='color:white; margin-top:40px;'>📊 Overall Statistics</h3>", unsafe_allow_html=True)
    
    # Create charts showing overall trends and distributions
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("<h4 style='color:white; margin-bottom:15px;'>📈 DPI Distribution by Tier</h4>", unsafe_allow_html=True)
        
        # Create tier distribution chart
        tier_counts = display_latest_df['Tier'].value_counts()
        tier_data = pd.DataFrame({
            'Tier': tier_counts.index,
            'Count': tier_counts.values
        })
        
        # Display as a simple bar chart using Streamlit
        st.bar_chart(tier_data.set_index('Tier'))
    
    with chart_col2:
        st.markdown("<h4 style='color:white; margin-bottom:15px;'>🏢 Teams by Stack</h4>", unsafe_allow_html=True)
        
        # Create stack distribution chart
        stack_counts = display_latest_df['Stack'].value_counts()
        stack_data = pd.DataFrame({
            'Stack': stack_counts.index,
            'Count': stack_counts.values
        })
        
        # Display as a simple bar chart using Streamlit
        st.bar_chart(stack_data.set_index('Stack'))
    
    # Add overall trend chart
    st.markdown("<h4 style='color:white; margin-top:30px; margin-bottom:15px;'>📊 6-Pillar Average Scores</h4>", unsafe_allow_html=True)
    
    # Calculate average scores for each pillar
    pillar_cols = ['Release_Velocity_Score', 'Git_Hygiene_Score', 'Pipeline_Maturity_Score', 
                   'Compliance_Score', 'Quality_Security_Score', 'Adoption_Score']
    pillar_names = ['Release Velocity', 'Git Hygiene', 'Pipeline Maturity', 
                    'Compliance', 'Quality & Security', 'Adoption']
    
    pillar_averages = []
    for col in pillar_cols:
        if col in display_latest_df.columns:
            avg_val = display_latest_df[col].mean()
            pillar_averages.append(avg_val if not pd.isna(avg_val) else 0)
        else:
            pillar_averages.append(0)
    
    pillar_chart_data = pd.DataFrame({
        'Pillar': pillar_names,
        'Average Score': pillar_averages
    })
    
    st.bar_chart(pillar_chart_data.set_index('Pillar'))

 


 

# === LEADERBOARD TAB ===
elif st.session_state.active_tab == 'Leaderboard':

    st.markdown("<h2 style='color:#2D2D2D; text-align:center; margin-bottom:20px;'>🏆 Leaderboard</h2>", unsafe_allow_html=True)

   

    # Remove sub-tabs - show only team rankings
    
    # Layout: Compact podium on left, sortable table on right
    podium_col, table_col = st.columns([1, 3])

    
    with podium_col:
        st.markdown("<h4 style='color:white; text-align:center; margin-bottom:15px;'>🏆 Top 3</h4>", unsafe_allow_html=True)
        
        if len(display_latest_df) >= 3:
            top3 = display_latest_df.head(3)
            for idx, (_, row) in enumerate(top3.iterrows()):
                rank = idx + 1
                medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
                medal_color = "rgba(255,215,0,0.2)" if rank == 1 else "rgba(192,192,192,0.15)" if rank == 2 else "rgba(205,127,50,0.15)"
                
                st.markdown(f"""<div style='background: rgba(45,55,72,0.2); border-radius: 15px; padding: 20px; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.1); background:{medal_color}; padding:15px; margin-bottom:10px; text-align:center;'>
<div style='font-size:32px; margin-bottom:5px;'>{medal}</div>
<div style='font-size:14px; font-weight:700; color:white; margin-bottom:3px;'>{row['Team']}</div>
<div style='font-size:18px; font-weight:800; color:#93c5fd;'>{f"{row.get('DPI', 0):.1f}" if row.get('DPI') is not None else 'N/A'}</div>
<div style='font-size:11px; color:rgba(255,255,255,0.6); margin-top:3px;'>Rank #{rank}</div>
</div>""", unsafe_allow_html=True)

    
    with table_col:
        # Header with sort controls
        st.markdown("<h3 style='color:white; margin-bottom:15px;'>📊 Team Rankings</h3>", unsafe_allow_html=True)
        
        # Simplified filters - single row with dropdowns
        filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 2])
        
        with filter_col1:
            sort_by = st.selectbox('Sort by', options=['DPI', 'RF', 'LTTD'], index=0, key='sort_metric')
        
        with filter_col2:
            # Simple dropdown for Stack with no default selection
            selected_stacks = st.multiselect('Filter by Stack', 
                                           options=sorted(display_history['Stack'].unique()), 
                                           default=[], 
                                           key='lb_stack')
        
        with filter_col3:
            # Simple dropdown for Tier with no default selection
            selected_tiers = st.multiselect('Filter by Tier', 
                                          options=sorted(display_latest_df['Tier'].unique()), 
                                          default=[], 
                                          key='lb_tier')

        
        # Apply filters and sorting - show all if no filters selected
        if selected_stacks and selected_tiers:
            lb = display_latest_df[display_latest_df['Stack'].isin(selected_stacks) & display_latest_df['Tier'].isin(selected_tiers)].copy()
        elif selected_stacks:
            lb = display_latest_df[display_latest_df['Stack'].isin(selected_stacks)].copy()
        elif selected_tiers:
            lb = display_latest_df[display_latest_df['Tier'].isin(selected_tiers)].copy()
        else:
            lb = display_latest_df.copy()

        
        # Sort based on selection
        if sort_by == 'DPI':
            lb = lb.sort_values(by='DPI', ascending=False)
        elif sort_by == 'RF':
            lb = lb.sort_values(by='RF', ascending=False)
        elif sort_by == 'LTTD':
            lb = lb.sort_values(by='LTTD', ascending=True)  # Lower is better

        
        # Use Streamlit's native dataframe component for better visibility
        # Prepare display dataframe
        display_df = lb.copy()
        
        # Format columns for display
        if 'RF' in display_df.columns:
            display_df['RF'] = display_df['RF'].apply(lambda x: f"{x:.0f}" if pd.notna(x) else "N/A")
        if 'LTTD' in display_df.columns:
            display_df['LTTD'] = display_df['LTTD'].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "N/A")
        if 'DPI' in display_df.columns:
            display_df['DPI'] = display_df['DPI'].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "N/A")
        if 'Δ Rank' in display_df.columns:
            display_df['Δ Rank'] = display_df['Δ Rank'].apply(
                lambda x: f"↑ {x}" if x > 0 else f"↓ {abs(x)}" if x < 0 else "—"
            )
        
        # Select and reorder columns for display
        display_columns = ['Rank', 'Team', 'DPI', 'RF', 'LTTD', 'Tier', 'Δ Rank']
        available_columns = [col for col in display_columns if col in display_df.columns]
        
        st.dataframe(
            display_df[available_columns],
            use_container_width=True,
            hide_index=True
        )


# === BADGES TAB ===
elif st.session_state.active_tab == 'Badges':

    st.markdown("<h2 style='color:#2D2D2D; text-align:center; margin-bottom:30px;'>🎖️ Achievements & Badges</h2>", unsafe_allow_html=True)

   

    # Layout: Compact criteria on left, main content on right

    criteria_col, content_col = st.columns([1, 3])

   

    with criteria_col:
        # Make badge criteria collapsible and collapsed by default
        with st.expander("📋 Badge Criteria", expanded=False):
            st.markdown("""<div style='font-size:11px; line-height:1.6; color:rgba(255,255,255,0.9);'>

<div style='margin-bottom:8px;'><strong>🚀 Velocity Champion</strong> <span style='opacity:0.6; cursor:help;' title='High release frequency and fast delivery'>ℹ️</span><br/><span style='font-size:10px; opacity:0.8;'>Release Velocity ≥ 70</span></div>

<div style='margin-bottom:8px;'><strong>🧹 Code Quality</strong> <span style='opacity:0.6; cursor:help;' title='Clean repositories with good hygiene practices'>ℹ️</span><br/><span style='font-size:10px; opacity:0.8;'>Git Hygiene ≥ 70</span></div>

<div style='margin-bottom:8px;'><strong>⚙️ Automation Pro</strong> <span style='opacity:0.6; cursor:help;' title='Mature CI/CD pipeline with automation'>ℹ️</span><br/><span style='font-size:10px; opacity:0.8;'>Pipeline Maturity ≥ 70</span></div>

<div style='margin-bottom:8px;'><strong>📋 Governance</strong> <span style='opacity:0.6; cursor:help;' title='Strong compliance and governance practices'>ℹ️</span><br/><span style='font-size:10px; opacity:0.8;'>Compliance ≥ 70</span></div>

<div style='margin-bottom:8px;'><strong>🛡️ Security Shield</strong> <span style='opacity:0.6; cursor:help;' title='Excellent security and quality standards'>ℹ️</span><br/><span style='font-size:10px; opacity:0.8;'>Quality & Security ≥ 70</span></div>

<div style='margin-bottom:8px;'><strong>🎯 Innovation</strong> <span style='opacity:0.6; cursor:help;' title='Adopting new tools and practices'>ℹ️</span><br/><span style='font-size:10px; opacity:0.8;'>Adoption ≥ 70</span></div>

</div>""", unsafe_allow_html=True)

   

    with content_col:

        # Group teams by badges they've earned - 6 PILLAR BADGES

        badge_groups = {

            'Velocity Champion': [],

            'Code Quality': [],

            'Automation Pro': [],

            'Governance': [],

            'Security Shield': [],

            'Innovation': []

        }

       

        for _, row in display_latest_df.iterrows():

            for badge in row['Badges']:

                if badge in badge_groups:

                    badge_groups[badge].append({

                        'Team': row['Team'],

                        'DPI': row['DPI'],

                        'Rank': row['Rank'],

                        'Release_Velocity_Score': row.get('Release_Velocity_Score', 0),

                        'Git_Hygiene_Score': row.get('Git_Hygiene_Score', 0),

                        'Pipeline_Maturity_Score': row.get('Pipeline_Maturity_Score', 0),

                        'Compliance_Score': row.get('Compliance_Score', 0),

                        'Quality_Security_Score': row.get('Quality_Security_Score', 0),

                        'Adoption_Score': row.get('Adoption_Score', 0)

                    })

       

        # Badge Statistics FIRST

        st.markdown("<h3 style='color:white; margin-bottom:20px;'>📊 Badge Statistics</h3>", unsafe_allow_html=True)

       

        badge_configs = [

            ('Velocity Champion', '🚀', 'rgba(6,182,212,0.15)', 'Release_Velocity_Score'),

            ('Code Quality', '🧹', 'rgba(16,185,129,0.15)', 'Git_Hygiene_Score'),

            ('Automation Pro', '⚙️', 'rgba(96,165,250,0.15)', 'Pipeline_Maturity_Score'),

            ('Governance', '📋', 'rgba(236,72,153,0.15)', 'Compliance_Score'),

            ('Security Shield', '🛡️', 'rgba(249,115,22,0.15)', 'Quality_Security_Score'),

            ('Innovation', '🎯', 'rgba(139,92,246,0.15)', 'Adoption_Score')

        ]

       

        # Display badge statistics first

        stat_cols = st.columns(6)

        for idx, (badge_name, icon, _, _) in enumerate(badge_configs):

            count = len(badge_groups[badge_name])

            with stat_cols[idx]:

                st.markdown(f"""<div style='background: rgba(45,55,72,0.2); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 25px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>

<div style='font-size:36px; margin-bottom:10px;'>{icon}</div>

<div style='font-size: 48px; font-weight: 800; background: linear-gradient(135deg, #06b6d4, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px; font-size:32px;'>{count}</div>

<div style='color: rgba(255,255,255,0.7); font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; font-size:11px;'>{badge_name}</div>

</div>

                """, unsafe_allow_html=True)

       

        # Badge Winners BELOW statistics

        st.markdown("<h3 style='color:white; margin-top:40px;'>🏆 Badge Winners</h3>", unsafe_allow_html=True)

       

        for badge_name, icon, bg_color, metric_key in badge_configs:

            teams = badge_groups[badge_name]

           

            if teams:

                # Sort teams by the relevant metric

                if metric_key == 'LTTD':

                    teams_sorted = sorted(teams, key=lambda x: x[metric_key])  # Lower is better

                else:

                    teams_sorted = sorted(teams, key=lambda x: x[metric_key], reverse=True)  # Higher is better

               

                with st.expander(f"{icon} {badge_name} ({len(teams)} teams)", expanded=False):

                    # Display in a grid

                    cols = st.columns(3)

                    for idx, team_data in enumerate(teams_sorted):

                        with cols[idx % 3]:

                            # Display the pillar score for this badge
                            metric_val = team_data.get(metric_key, 0)
                            metric_display = f"{metric_key.replace('_', ' ').replace('Score', '').strip()}: {metric_val:.1f}/100" if metric_val is not None else "Score: N/A"

                           

                            st.markdown(f"""<div style='background: rgba(45,55,72,0.2); border-radius: 15px; padding: 20px; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.1); background:{bg_color}; margin-bottom:15px; border: 1px solid rgba(255,255,255,0.1);'>

<div style='text-align:center;'>

<div style='font-size:28px; margin-bottom:8px;'>{icon}</div>

<div style='font-size:16px; font-weight:700; margin-bottom:5px; color:white;'>{team_data['Team']}</div>

<div style='font-size:14px; color:rgba(255,255,255,0.8);'>{metric_display}</div>

<div style='font-size:12px; margin-top:5px; color:rgba(255,255,255,0.6);'>DPI: {f"{team_data.get('DPI', 0):.1f}" if team_data.get('DPI') is not None else 'N/A'} | Rank #{team_data.get('Rank', 'N/A')}</div>

</div>

</div>

                            """, unsafe_allow_html=True)

            else:

                with st.expander(f"{icon} {badge_name} (0 teams)", expanded=False):

                    st.markdown(f"""<div style='text-align:center; color:rgba(255,255,255,0.6); padding:20px;'>

                        {icon} No teams earned this badge yet

</div>

                    """, unsafe_allow_html=True)

 


 

# === TEAM TRENDS TAB ===
elif st.session_state.active_tab == 'Team Trends':

 

    st.markdown("<h2 style='color:#2D2D2D; text-align:center; margin-bottom:30px;'>📈 Team Trends</h2>", unsafe_allow_html=True)

 

    # Natural sort for team numbers

    def natural_sort_key(team_name):

        return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', str(team_name))]

   

    teams_for_detail = sorted(display_history['Team'].unique(), key=natural_sort_key)

 

    team = st.selectbox('🔍 Select Team for Detailed Analysis', options=teams_for_detail, key='team_detail')

 

    team_data = display_latest_df[display_latest_df['Team']==team]
    
    if team_data.empty:
        st.error(f"⚠️ No data found for team '{team}'. Please run `python3 quick_populate.py` to populate the database.")
        st.stop()
    
    t_latest = team_data.iloc[0]

 


 

    # Top row: left = tier + badges + DPI, right = trend chart

 

    r1c1, r1c2 = st.columns([2,3])

 

    with r1c1:

        st.markdown(f"""<div style='border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.1); background: linear-gradient(135deg, {COLOR_MAP.get(t_latest['Tier'], '#6b7280')}, {COLOR_MAP.get(t_latest['Tier'], '#6b7280')});'>

<div style='font-size: 48px; margin-bottom: 15px;'>🏆</div>

<div style='text-align:center;'>

<div style='font-size:32px; font-weight:800; margin-bottom:10px;'>{t_latest.get('Tier', 'N/A')}</div>

<div style='font-size:20px;'>DPI Score: <span style='font-weight:800; color:#ffd700;'>{f"{t_latest.get('DPI', 0):.1f}" if t_latest.get('DPI') is not None else 'N/A'}</span></div>

</div>

</div>

        """, unsafe_allow_html=True)

 

        if t_latest['Badges']:

 

            st.markdown("<div style='margin-top:20px; text-align:center;'><div style='color:white; font-weight:600; margin-bottom:10px;'>🎖️ Earned Badges</div>" + ' '.join([badge_html(b) for b in t_latest['Badges']]) + '</div>', unsafe_allow_html=True)

 

    with r1c2:

 

        st.markdown("<h3 style='color:white;'>📈 Performance Trend (Last 5 Weeks)</h3>", unsafe_allow_html=True)

 

        team_tr = spark_hist.get(team, pd.Series()).dropna() if isinstance(spark_hist, pd.DataFrame) else pd.Series()

 

        if not team_tr.empty:

 

            team_tr_df = team_tr.reset_index()

            team_tr_df.columns = ['Week_Start', 'DPI']

            team_tr_df['Week_Label'] = pd.to_datetime(team_tr_df['Week_Start'], errors='coerce').dt.strftime('%Y-%m-%d')

            st.line_chart(team_tr_df.set_index('Week_Label')['DPI'], width='stretch')

 

        else:

 

            st.markdown("""<div style='border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.1); background: linear-gradient(135deg, #6b7280, #4b5563);'>

<div style='text-align:center;'>ℹ️ No trend data available</div>

</div>

            """, unsafe_allow_html=True)

 


 

    # Second row: left = scores breakdown, right = week-over-week deltas

 

    r2c1, r2c2 = st.columns([2,2])

 

    with r2c1:

 

        st.markdown("<h3 style='color:white; margin-top:30px;'>📊 6-Pillar Score Breakdown</h3>", unsafe_allow_html=True)

 

        # New 6-pillar scoring system - use correct column names from database
        scores_data = [

            ('🚀 Release Velocity', t_latest.get('Release_Velocity_Score', 0), 100, '#06b6d4'),

            ('🧹 Git Hygiene', t_latest.get('Git_Hygiene_Score', 0), 100, '#10b981'),

            ('⚙️ Pipeline Maturity', t_latest.get('Pipeline_Maturity_Score', 0), 100, '#60a5fa'),

            ('📋 Compliance', t_latest.get('Compliance_Score', 0), 100, '#ec4899'),

            ('🔒 Quality & Security', t_latest.get('Quality_Security_Score', 0), 100, '#f97316'),

            ('🎯 Adoption', t_latest.get('Adoption_Score', 0), 100, '#8b5cf6')

        ]

       

        for metric, value, max_val, color in scores_data:

            # Fix -0 display issue by ensuring value is not None and handle negative zero
            if value is None or pd.isna(value):
                value = 0
            value = abs(value) if value == 0 else value  # Convert -0 to 0
            
            pct = int((value/max_val)*100) if value is not None else 0

            st.markdown(f"""<div style='margin-bottom:15px;'>

<div style='display:flex; justify-content:space-between; color:white; font-weight:600; margin-bottom:5px;'>

<span>{metric}</span>

<span>{value:.1f} / {max_val}</span>

</div>

<div style='width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 10px; overflow: hidden;'>

<div style='height: 100%; border-radius: 10px; transition: width 0.3s ease; width:{pct}%; background:{color};'></div>

</div>

</div>

            """, unsafe_allow_html=True)

 

    with r2c2:

 

        st.markdown("<h3 style='color:white; margin-top:30px;'>📊 Week-over-Week Changes</h3>", unsafe_allow_html=True)

 

        if display_prev_week is not None:

 

            prev_row = display_history[(display_history['Team']==team) & (display_history['Week_Start']==display_prev_week)].iloc[0]

 

            deltas = {

 

                '🚀 Release Velocity': (t_latest.get('Release_Velocity_Score', 0) or 0) - (prev_row.get('Release_Velocity_Score', 0) or 0),

 

                '🧹 Git Hygiene': (t_latest.get('Git_Hygiene_Score', 0) or 0) - (prev_row.get('Git_Hygiene_Score', 0) or 0),

 

                '⚙️ Pipeline Maturity': (t_latest.get('Pipeline_Maturity_Score', 0) or 0) - (prev_row.get('Pipeline_Maturity_Score', 0) or 0),

 

                '� Compliance': (t_latest.get('Compliance_Score', 0) or 0) - (prev_row.get('Compliance_Score', 0) or 0),

 

                '🔒 Quality & Security': (t_latest.get('Quality_Security_Score', 0) or 0) - (prev_row.get('Quality_Security_Score', 0) or 0),

 

                '🎯 Adoption': (t_latest.get('Adoption_Score', 0) or 0) - (prev_row.get('Adoption_Score', 0) or 0),

 

                '📊 DPI': (t_latest.get('DPI', 0) or 0) - (prev_row.get('DPI', 0) or 0)

 

            }

 

            for metric, delta in deltas.items():

                delta_color = '#10b981' if delta > 0 else '#ef4444' if delta < 0 else '#6b7280'

                delta_icon = '↑' if delta > 0 else '↓' if delta < 0 else '→'

                st.markdown(f"""<div style='background: rgba(45,55,72,0.2); border-radius: 15px; padding: 20px; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.1); margin-bottom:10px;'>

<div style='display:flex; justify-content:space-between; align-items:center;'>

<span style='color:white; font-weight:600;'>{metric}</span>

<span style='color:{delta_color}; font-size:20px; font-weight:800;'>{delta_icon} {abs(delta):.1f}</span>

</div>

</div>

                """, unsafe_allow_html=True)

 

        else:

 

            st.markdown("""<div style='border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.1); background: linear-gradient(135deg, #6b7280, #4b5563);'>

<div style='text-align:center;'>ℹ️ No previous week data to compare</div>

</div>

            """, unsafe_allow_html=True)

 


 

    # Third row: Recommendations section

    st.markdown("<h3 style='color:white; margin-top:40px; margin-bottom:20px;'>💡 Recommended Actions</h3>", unsafe_allow_html=True)

    

    try:

        from recommendation_helper import get_recommendation_helper

        from registry_loader import RegistryLoader

        

        loader = RegistryLoader()

        apps = loader.load_all()

        

        app_entry = None

        for app in apps:

            if app.app_name == team or str(app.eim) == team:

                app_entry = app

                break

        

        if app_entry:

            app_data = {

                'eim': app_entry.eim,

                'app_name': app_entry.app_name,

                'app_type': app_entry.app_type,

                'tier': app_entry.tier,

                'stack': app_entry.stack,

                'ci_automated': app_entry.ci_automated,

                'cd_automated': app_entry.cd_automated,

                'automated_rollback': app_entry.automated_rollback,

                'zero_touch_deployment': app_entry.zero_touch_deployment,

            }

            

            score_data = {

                'dpi': t_latest.get('DPI', 0),

                'rf_score': t_latest.get('RF_Score', 0),

                'flow_score': t_latest.get('Flow_Score', 0),

                'stability_score': t_latest.get('Stability_Score', 0),

                'automation_score': t_latest.get('Automation_Score', 0),

            }

            

            helper = get_recommendation_helper()

            recommendations = helper.get_recommendations(app_data, score_data, max_recommendations=3)

            

            if recommendations:

                for i, rec in enumerate(recommendations, 1):

                    effort_colors = {

                        'low': 'linear-gradient(135deg, #10b981, #059669)',

                        'medium': 'linear-gradient(135deg, #f59e0b, #d97706)',

                        'high': 'linear-gradient(135deg, #ef4444, #dc2626)'

                    }

                    bg_color = effort_colors.get(rec['effort'], 'linear-gradient(135deg, #6b7280, #4b5563)')

                    

                    st.markdown(f"""<div style='background: {bg_color}; border-radius: 15px; padding: 20px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.1);'>

<div style='display:flex; justify-content:space-between; align-items:start; margin-bottom:10px;'>

<div style='font-size:18px; font-weight:700; color:white;'>{rec['effort_emoji']} {rec['action']}</div>

<div style='background:rgba(255,255,255,0.2); padding:5px 12px; border-radius:20px; font-size:12px; font-weight:600; color:white;'>+{rec['points_gain']} pts</div>

</div>

<div style='font-size:13px; color:rgba(255,255,255,0.9); margin-bottom:8px;'>{rec['detail']}</div>

<div style='display:flex; justify-content:space-between; font-size:11px; color:rgba(255,255,255,0.7);'>

<span>📊 {rec['pillar']}</span>

<span>⏱️ Effort: {rec['effort'].title()}</span>

</div>

</div>

                    """, unsafe_allow_html=True)

            else:

                st.markdown("""<div style='border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.1); background: linear-gradient(135deg, #10b981, #059669);'>

<div style='text-align:center;'>

<div style='font-size:32px; margin-bottom:10px;'>🎉</div>

<div style='font-size:18px; font-weight:700;'>Excellent Work!</div>

<div style='font-size:14px; opacity:0.9; margin-top:5px;'>No critical improvements needed!</div>

</div>

</div>

                """, unsafe_allow_html=True)

        else:

            st.markdown(f"""<div style='border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.1); background: linear-gradient(135deg, #6b7280, #4b5563);'>

<div style='text-align:center;'>

<div style='font-size:16px; font-weight:600; margin-bottom:5px;'>ℹ️ No Registry Data</div>

<div style='font-size:13px; opacity:0.8;'>Add {team} to YAML registry for recommendations</div>

</div>

</div>

            """, unsafe_allow_html=True)

            

    except Exception as e:

        st.markdown("""<div style='border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.1); background: linear-gradient(135deg, #6b7280, #4b5563);'>

<div style='text-align:center;'>

<div style='font-size:14px; opacity:0.8;'>💡 Recommendations coming soon</div>

</div>

</div>

        """, unsafe_allow_html=True)



# === DOCS TAB ===
elif st.session_state.active_tab == 'Docs':

 

    st.markdown("<h2 style='color:#2D2D2D; text-align:center; margin-bottom:30px;'>📘 Documentation & Guide</h2>", unsafe_allow_html=True)

 

    col1,col2,col3 = st.columns(3)

 

    with col1:

 

        st.markdown("""<div style='border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.1); background: linear-gradient(135deg, #3b82f6, #2563eb);'>

<div style='font-size: 48px; margin-bottom: 15px;'>📤</div>

<div style='text-align:center;'>

<div style='font-size:20px; font-weight:700; margin-bottom:10px;'>How to Use</div>

<div style='font-size:14px; opacity:0.9;'>Upload weekly CSV, validate, and publish to add to history. Use BU selector to scope views.</div>

</div>

</div>

        """, unsafe_allow_html=True)

 

    with col2:

 

        st.markdown("""<div style='border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.1); background: linear-gradient(135deg, #8b5cf6, #7c3aed);'>

<div style='font-size: 48px; margin-bottom: 15px;'>📊</div>

<div style='text-align:center;'>

<div style='font-size:20px; font-weight:700; margin-bottom:10px;'>Scoring Rules</div>

<div style='font-size:14px; opacity:0.9;'>Open the scoring card at the top for quick rules. Check the expander for detailed scoring breakdown.</div>

</div>

</div>

        """, unsafe_allow_html=True)

 

    with col3:

 

        st.markdown("""<div style='border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.1); background: linear-gradient(135deg, #10b981, #059669);'>

<div style='font-size: 48px; margin-bottom: 15px;'>🎖️</div>

<div style='text-align:center;'>

<div style='font-size:20px; font-weight:700; margin-bottom:10px;'>Badges & Tiers</div>

<div style='font-size:14px; opacity:0.9;'>Badges are awarded based on RF, LTTD, CFR and automation. Tiers reflect overall DPI performance.</div>

</div>

</div>

        """, unsafe_allow_html=True)

 

# --- DATA REFRESH SECTION ---

# Sidebar removed - use weekly_refresh.py or setup_database.py to add new week data

# show_data_refresh_section()

# --- HSBC Footer ---
st.markdown("""
<div style='background: #2D2D2D; color: #999999; padding: 16px 24px; text-align: center; margin: 40px -1rem -1rem -1rem; font-size: 12px;'>
    <div style='display: flex; justify-content: center; align-items: center; gap: 12px;'>
        <span>Support</span>
        <span>|</span>
        <span>© HSBC Bank plc 2026</span>
    </div>
</div>
""", unsafe_allow_html=True)
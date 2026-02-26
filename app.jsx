import os

import datetime as dt

import streamlit as st

import pandas as pd

import numpy as np

import re

 

st.set_page_config(layout="wide", page_title="🚀 DevOps Gamification Dashboard", page_icon="🏆")

 

# --- Custom CSS for Gamification UI ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');

* {
    font-family: 'Poppins', sans-serif;
}

.main {
    background: #1a202c;
    background-attachment: fixed;
}

.stApp {
    background: #1a202c;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background: #1a202c;
}

[data-testid="stSidebar"] > div:first-child {
    background: #1a202c;
}

[data-testid="stSidebar"] .stMarkdown {
    color: white;
}

[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3, 
[data-testid="stSidebar"] h4 {
    color: white !important;
}

[data-testid="stSidebar"] label {
    color: white !important;
    font-weight: 600;
}

[data-testid="stSidebar"] .stFileUploader {
    background: rgba(255,255,255,0.1);
    border-radius: 15px;
    padding: 20px;
    border: 2px dashed rgba(255,255,255,0.3);
}

[data-testid="stSidebar"] .stFileUploader label {
    color: white !important;
}

[data-testid="stSidebar"] .stFileUploader [data-testid="stFileUploaderDropzone"] {
    background: rgba(255,255,255,0.05);
    border: 2px dashed rgba(255,255,255,0.4);
    border-radius: 10px;
}

[data-testid="stSidebar"] .stFileUploader [data-testid="stFileUploaderDropzoneInstructions"] {
    color: rgba(255,255,255,0.9) !important;
}

[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label {
    color: white !important;
    font-weight: 600;
}

[data-testid="stSidebar"] [data-baseweb="select"] {
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
}

[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.1);
    color: white;
}

/* Fix text visibility in main content */
.stMarkdown, .stText {
    color: white;
}

h1, h2, h3, h4, h5, h6 {
    color: white !important;
}

p {
    color: rgba(255,255,255,0.9);
}

/* Fix expander styling */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
    color: white !important;
    font-weight: 600;
}

.streamlit-expanderHeader p {
    color: white !important;
}

.streamlit-expanderContent {
    background: rgba(255,255,255,0.05);
    border-radius: 0 0 10px 10px;
    color: white !important;
}

.streamlit-expanderContent p,
.streamlit-expanderContent li,
.streamlit-expanderContent div {
    color: white !important;
}

/* Chart styling */
.stVegaLiteChart {
    background: rgba(255,255,255,0.95);
    border-radius: 15px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.2);
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

/* Fix multiselect styling */
[data-baseweb="tag"] {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
}

/* Fix dataframe styling */
.stDataFrame {
    background: rgba(255,255,255,0.05);
    border-radius: 15px;
    padding: 10px;
}

.stDataFrame table {
    color: white !important;
}

.stDataFrame th {
    background: rgba(255,255,255,0.1) !important;
    color: white !important;
}

.stDataFrame td {
    color: white !important;
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

</style>
""", unsafe_allow_html=True)

# --- Animated Hero Header ---
st.markdown("""
<div class='hero-header'>
    <h1 class='hero-title'>🚀 DevOps Transformation Gamification 2026</h1>
    <p class='hero-subtitle'>⚡ Target: RF 280 | ⏱ LTDD 1.8 | 🎯 Sustainable Maturity</p>
</div>
""", unsafe_allow_html=True)


 

# --- DPI Calculation Functions ---

 

def calculate_rf_score(rf):

    if rf <= 50: return 5

    if 50 < rf <= 100: return 10

    if 100 < rf <= 180: return 18

    if 180 < rf <= 250: return 25

    if 250 < rf <= 300: return 32

    return 35

 

def calculate_ltdd_score(ltdd, measurable_crs_perc):

    score = 0

    if ltdd < 2: score = 25

    elif 2 <= ltdd <= 5: score = 20

    elif 5 < ltdd <= 10: score = 15

    elif 10 < ltdd <= 20: score = 10

    else: score = 5

 

    if pd.isna(measurable_crs_perc):

        measurable_crs_perc = 1.0

    if measurable_crs_perc < 0.9:

        return min(score, 10)

    return score

 

def calculate_cfr_score(cfr):

    if cfr > 0.2: return 1

    if 0.1 <= cfr <= 0.2: return 4

    return 7

 

def calculate_mttr_score(mttr):

    if mttr > 2: return 1

    if 1 <= mttr <= 2: return 4

    return 7

 

def calculate_priv_access_score(level):

    score_map = {0:0, 1:2, 2:4, 3:6}

    return score_map.get(int(level) if not pd.isna(level) else 0, 0)

 

def calculate_automation_score(ci, cd, iac, rollback, self_service):

    score = 0

    if ci: score += 5

    if cd: score += 5

    if iac: score += 4

    if rollback: score += 3

    if self_service: score += 3

    return score

 

def get_tier(dpi):

    if dpi >= 85: return "Elite"

    if 70 <= dpi < 85: return "Advanced"

    if 50 <= dpi < 70: return "Emerging"

    return "Needs Support"

 

def calculate_dpi_row(row):

    # expects a normalized row (booleans, numbers)

    # If critical data missing => not published

    if not row.get('Critical_Data_Present', True):

        return {

            'DPI': np.nan,

            'Tier': 'Not Published',

            'RF_Score': np.nan,

            'Flow_Score': np.nan,

            'CFR_Score': np.nan,

            'MTTR_Score': np.nan,

            'Priv_Score': np.nan,

            'Automation_Score': np.nan,

            'Stability_Score': np.nan,

            'Data_Quality_Flags': ['Critical_Data_Missing']

        }

 

    flags = []

    rf_score = calculate_rf_score(row.get('RF', 0))

    flow_score = calculate_ltdd_score(row.get('LTDD', 9999), row.get('LTDD_Measurable', 1.0))

    if row.get('LTDD_Measurable', 1.0) < 0.9:

        flags.append('LTDD_Measurability<90% -> Flow capped')

 

    cfr_score = calculate_cfr_score(row.get('CFR', 1.0))

    mttr_score = calculate_mttr_score(row.get('MTTR', 999))

    priv_score = calculate_priv_access_score(row.get('Priv_Access', 0))

 

    stability_score = cfr_score + mttr_score + priv_score

    if not row.get('CFR_Reported', True):

        flags.append('CFR not reported -> Stability capped at 8')

        stability_score = min(stability_score, 8)

 

    automation_score = calculate_automation_score(row.get('CI', False), row.get('CD', False), row.get('IaC', False), row.get('Rollback', False), row.get('Self_Service', False))

    if not row.get('Automation_Audited', True) and automation_score > 0:

        flags.append('Automation claimed but not audited -> Automation capped at 10')

        automation_score = min(automation_score, 10)

 

    total = rf_score + flow_score + stability_score + automation_score

    tier = get_tier(total)

 

    return {

        'DPI': total,

        'Tier': tier,

        'RF_Score': rf_score,

        'Flow_Score': flow_score,

        'CFR_Score': cfr_score,

        'MTTR_Score': mttr_score,

        'Priv_Score': priv_score,

        'Automation_Score': automation_score,

        'Stability_Score': stability_score,

        'Data_Quality_Flags': flags

    }

 

# --- CSV schema and validation ---

REQUIRED_COLUMNS = [

    'Team','Week','RF','LTDD','LTDD_Measurable','CFR','MTTR','Priv_Access',

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

    df['LTDD'] = pd.to_numeric(df['LTDD'], errors='coerce').fillna(9999).astype(float)

    df['LTDD_Measurable'] = pd.to_numeric(df['LTDD_Measurable'], errors='coerce').fillna(1.0).astype(float)

    df['CFR'] = pd.to_numeric(df['CFR'], errors='coerce').fillna(1.0).astype(float)

    df['MTTR'] = pd.to_numeric(df['MTTR'], errors='coerce').fillna(999.0).astype(float)

    df['Priv_Access'] = pd.to_numeric(df['Priv_Access'], errors='coerce').fillna(0).astype(int)

 

    # booleans

    for b in ['CI','CD','IaC','Rollback','Self_Service','CFR_Reported','Automation_Audited','Critical_Data_Present']:

        df[b] = df[b].apply(parse_bool)

 

    # basic validations

    if (df['LTDD_Measurable'] < 0).any() or (df['LTDD_Measurable'] > 1).any():

        errors.append('LTDD_Measurable must be between 0 and 1')

    if (df['CFR'] < 0).any() or (df['CFR'] > 1).any():

        errors.append('CFR must be between 0 and 1')

    if not df['Priv_Access'].isin([0,1,2,3]).all():

        errors.append('Priv_Access must be 0,1,2 or 3')

 

    if errors:

        return None, errors

 

    # compute DPI fields

    computed = df.apply(lambda r: pd.Series(calculate_dpi_row(r)), axis=1)

    df = pd.concat([df, computed], axis=1)

 

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

                'LTDD': round(np.random.uniform(1, 25), 1),

                'LTDD_Measurable': round(np.random.uniform(0.85, 1.0), 2),

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

 

def load_history():

    if os.path.exists(HISTORY_FILE):

        hist = pd.read_csv(HISTORY_FILE, parse_dates=['Week','Week_Start'])

        return hist

    else:

        return create_sample_history(HISTORY_FILE)

 

history_df = load_history()

 

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

    if df_row['RF'] >= 250:

        badges.append('Release Champion')

    elif df_row['RF'] >= 180:

        badges.append('High Velocity')

    if df_row['LTDD'] < 2:

        badges.append('Flow Master')

    if df_row['CFR'] < 0.05:

        badges.append('Stability Shield')

    if df_row.get('Automation_Score', 0) >= 20:

        badges.append('Automation Pro')

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

    'Flow Master': 'LTDD < 2 days — excellent flow',

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

    return f"<span class='badge' title='{desc}'>{icon} {badge}</span>"

 

def tier_html(tier, dpi=None):

    color = COLOR_MAP.get(tier, '#6b7280')

    desc = TIER_DESC.get(tier, '')

    dpi_text = f" ({dpi:.1f})" if dpi is not None and not pd.isna(dpi) else ''

    return f"<div class='tier-badge' style='background:{color}' title='{desc}'>{tier}{dpi_text}</div>"

 

# Tabs layout (add Badges tab)

# one tabs declaration only (emoji labels)

tab1, tab2, tab3, tab4, tab5 = st.tabs(['🏁 Overview','🏆 Leaderboard','🎖️ Badges','👥 Team','📘 Docs'])

 

# compute display datasets (Business Unit filter removed)

display_history = history_df.copy()

 

# latest and previous for display

display_latest_week = display_history['Week_Start'].max()

display_prev_weeks = sorted(display_history['Week_Start'].unique())

display_prev_week = display_prev_weeks[-2] if len(display_prev_weeks) > 1 else None

 

display_latest_df = display_history[display_history['Week_Start'] == display_latest_week].copy()

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

if (display_history['Critical_Data_Present'] == False).any():

    quality_flags.append('Some teams missing critical data (scores hidden)')

if (display_history['LTDD_Measurable'] < 0.9).any():

    quality_flags.append('Some teams have LTDD measurability <90% (flow capped)')

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

 

with tab1:

    st.markdown(f"<h2 style='color:white; text-align:center; margin-bottom:30px;'>📊 Overview — Week of {display_latest_week.date()}</h2>", unsafe_allow_html=True)

    # Scoring summary in Overview tab
    with st.expander("📋 Scoring Summary (Quick Reference)", expanded=False):
        st.markdown("""
        <div style='color:white;'>
        <ul style='color:white;'>
            <li style='color:white; margin-bottom:10px;'><strong>Velocity (RF)</strong> — 35 pts (target 280 → 32 pts)</li>
            <li style='color:white; margin-bottom:10px;'><strong>Flow (LTDD)</strong> — 25 pts (LTDD &lt;2 → 25 pts). If LTDD measurability &lt;90% → Flow capped at 10.</li>
            <li style='color:white; margin-bottom:10px;'><strong>Stability</strong> — 20 pts (CFR 7 pts, MTTR 7 pts, Privileged Access 6 pts). If CFR not reported → Stability capped at 8.</li>
            <li style='color:white; margin-bottom:10px;'><strong>Automation</strong> — 20 pts (CI 5, CD 5, IaC 4, Rollback 3, Self-service 3). If automation not audited → capped at 10.</li>
            <li style='color:white; margin-bottom:10px;'><strong>Integrity</strong>: If critical data missing → score not published.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    # top metrics for selected BU with animated cards

    col1, col2, col3, col4 = st.columns(4)

    avg_dpi = display_history.groupby('Team')['DPI'].mean().mean()
    avg_rf = display_history.groupby('Team')['RF'].mean().mean()
    avg_ltdd = display_history.groupby('Team')['LTDD'].mean().mean()
    pct = (display_history[display_history['Tier'].isin(['Elite','Advanced'])]['Team'].nunique() / display_history['Team'].nunique()) * 100

    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{avg_dpi:.1f}</div>
            <div class='metric-label'>🎯 Avg DPI</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{avg_rf:.0f}</div>
            <div class='metric-label'>⚡ Avg RF</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{avg_ltdd:.1f}</div>
            <div class='metric-label'>⏱ Avg LTDD</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{pct:.0f}%</div>
            <div class='metric-label'>🏆 Elite/Advanced</div>
        </div>
        """, unsafe_allow_html=True)

 

    st.markdown("<h3 style='color:white; margin-top:40px;'>🎮 Team Performance Dashboard</h3>", unsafe_allow_html=True)

    left, right = st.columns([2,1])

    with left:

        st.markdown("<p style='color:rgba(255,255,255,0.8);'>Select a team to view detailed performance metrics</p>", unsafe_allow_html=True)

        # Natural sort for team numbers (Team 1, Team 2, ..., Team 10, Team 11, etc.)
        def natural_sort_key(team_name):
            return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', str(team_name))]
        
        teams_for_overview = sorted(display_history['Team'].unique(), key=natural_sort_key)

        team_choice = st.selectbox('🏢 Select Team', options=teams_for_overview, key='overview_team')

        trow = display_latest_df[display_latest_df['Team'] == team_choice].iloc[0]

        st.markdown(f"""
        <div class='team-card'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <h2 class='team-name'>{team_choice}</h2>
                    <div style='font-size:16px; color:rgba(255,255,255,0.8);'>DPI Score: <span style='font-size:24px; font-weight:800; color:#ffd700;'>{trow['DPI']:.1f}</span></div>
                </div>
                <div>{tier_html(trow['Tier'])}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # show numeric score bars with labels
        st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

        cols = st.columns(2)

        with cols[0]:
            rf_pct = int((trow['RF_Score']/35)*100) if not pd.isna(trow['RF_Score']) else 0
            st.markdown(f"""
            <div style='margin-bottom:20px;'>
                <div style='color:white; font-weight:600; margin-bottom:8px;'>⚡ RF Score</div>
                <div class='metric-bar'>
                    <div class='metric-fill' style='width:{rf_pct}%; background:#06b6d4;'></div>
                </div>
                <div style='color:rgba(255,255,255,0.7); font-size:14px; margin-top:5px;'>{trow['RF_Score']:.1f} / 35</div>
            </div>
            """, unsafe_allow_html=True)

            flow_pct = int((trow['Flow_Score']/25)*100) if not pd.isna(trow['Flow_Score']) else 0
            st.markdown(f"""
            <div style='margin-bottom:20px;'>
                <div style='color:white; font-weight:600; margin-bottom:8px;'>💨 Flow Score</div>
                <div class='metric-bar'>
                    <div class='metric-fill' style='width:{flow_pct}%; background:#60a5fa;'></div>
                </div>
                <div style='color:rgba(255,255,255,0.7); font-size:14px; margin-top:5px;'>{trow['Flow_Score']:.1f} / 25</div>
            </div>
            """, unsafe_allow_html=True)

        with cols[1]:
            stab_pct = int((trow['Stability_Score']/20)*100) if not pd.isna(trow['Stability_Score']) else 0
            st.markdown(f"""
            <div style='margin-bottom:20px;'>
                <div style='color:white; font-weight:600; margin-bottom:8px;'>🛡️ Stability Score</div>
                <div class='metric-bar'>
                    <div class='metric-fill' style='width:{stab_pct}%; background:#f97316;'></div>
                </div>
                <div style='color:rgba(255,255,255,0.7); font-size:14px; margin-top:5px;'>{trow['Stability_Score']:.1f} / 20</div>
            </div>
            """, unsafe_allow_html=True)

            auto_pct = int((trow['Automation_Score']/20)*100) if not pd.isna(trow['Automation_Score']) else 0
            st.markdown(f"""
            <div style='margin-bottom:20px;'>
                <div style='color:white; font-weight:600; margin-bottom:8px;'>🤖 Automation Score</div>
                <div class='metric-bar'>
                    <div class='metric-fill' style='width:{auto_pct}%; background:#10b981;'></div>
                </div>
                <div style='color:rgba(255,255,255,0.7); font-size:14px; margin-top:5px;'>{trow['Automation_Score']:.1f} / 20</div>
            </div>
            """, unsafe_allow_html=True)

    with right:

        st.markdown("""
        <div class='achievement-card' style='background: linear-gradient(135deg, #8b5cf6, #6366f1);'>
            <div style='font-size:20px; font-weight:700; margin-bottom:15px;'>💡 Recommended Actions</div>
        """, unsafe_allow_html=True)

        rf_progress = min(1.0, trow['RF'] / 280.0)

        ltdd_progress = min(1.0, 1.8 / max(trow['LTDD'], 0.001))

        automation_progress = trow['Automation_Score'] / 20.0 if not pd.isna(trow['Automation_Score']) else 0

        stability_progress = trow['Stability_Score'] / 20.0 if not pd.isna(trow['Stability_Score']) else 0

        recs = []

        if rf_progress < 0.5:

            recs.append('🚀 Increase release cadence: automate CD and reduce batch sizes')

        if ltdd_progress < 0.8:

            recs.append('⏱️ Improve LTDD measurement and CI speed')

        if automation_progress < 0.5:

            recs.append('🤖 Prioritise CI/CD and IaC coverage')

        if stability_progress < 0.5:

            recs.append('🛡️ Invest in observability, incident response and rollback')

        if not recs:

            recs = ['✨ Keep optimizing and scale automation']

        for r in recs[:5]:
            st.markdown(f"<div style='padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.1);'>{r}</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

 

with tab2:
    st.markdown("<h2 style='color:white; text-align:center; margin-bottom:20px;'>🏆 Leaderboard</h2>", unsafe_allow_html=True)
    
    # Create sub-tabs for better organization
    leaderboard_subtab1, leaderboard_subtab2 = st.tabs(['📋 Team Rankings', '📊 Performance Graphs'])
    
    with leaderboard_subtab1:
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
                    
                    st.markdown(f"""
                    <div class='team-card' style='background:{medal_color}; padding:15px; margin-bottom:10px; text-align:center;'>
                        <div style='font-size:32px; margin-bottom:5px;'>{medal}</div>
                        <div style='font-size:14px; font-weight:700; color:white; margin-bottom:3px;'>{row['Team']}</div>
                        <div style='font-size:18px; font-weight:800; color:#93c5fd;'>{row['DPI']:.1f}</div>
                        <div style='font-size:11px; color:rgba(255,255,255,0.6); margin-top:3px;'>Rank #{rank}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        with table_col:
            # Header with sort controls
            st.markdown("<h3 style='color:white; margin-bottom:15px;'>📊 Team Rankings</h3>", unsafe_allow_html=True)
            
            # Filters and sorting
            filter_row1, filter_row2 = st.columns([3, 1])
            with filter_row1:
                sort_by = st.selectbox('Sort by', options=['DPI', 'RF', 'LTDD'], index=0, key='sort_metric')
            with filter_row2:
                st.download_button('⬇️ Export', data=display_latest_df.to_csv(index=False), file_name='leaderboard_latest.csv')
            
            # Filter controls
            f1, f2 = st.columns([3, 1])
            with f1:
                stacks = st.multiselect('Stack', options=display_history['Stack'].unique(), default=display_history['Stack'].unique(), key='lb_stack')
            with f2:
                tiers = st.multiselect('Tier', options=display_latest_df['Tier'].unique(), default=display_latest_df['Tier'].unique(), key='lb_tier')
            
            # Apply filters and sorting
            lb = display_latest_df[display_latest_df['Stack'].isin(stacks) & display_latest_df['Tier'].isin(tiers)].copy()
            
            # Sort based on selection
            if sort_by == 'DPI':
                lb = lb.sort_values(by='DPI', ascending=False)
            elif sort_by == 'RF':
                lb = lb.sort_values(by='RF', ascending=False)
            elif sort_by == 'LTDD':
                lb = lb.sort_values(by='LTDD', ascending=True)  # Lower is better
            
            # Build complete table HTML as single string
            table_html = """
            <style>
            .rank-table {
                width: 100%;
                border-collapse: collapse;
            }
            .rank-table-header {
                background: rgba(45,55,72,0.4);
                color: white;
                font-weight: 700;
                padding: 12px;
                text-align: left;
                border-bottom: 2px solid rgba(96,165,250,0.3);
            }
            .rank-table-row {
                background: rgba(45,55,72,0.2);
                border-bottom: 1px solid rgba(255,255,255,0.05);
                transition: all 0.3s ease;
            }
            .rank-table-row:hover {
                background: rgba(45,55,72,0.35);
                transform: translateX(5px);
            }
            .rank-table-cell {
                padding: 12px;
                color: white;
            }
            </style>
            <table class='rank-table'>
                <tr>
                    <th class='rank-table-header' style='width:60px;'>Rank</th>
                    <th class='rank-table-header'>Team</th>
                    <th class='rank-table-header' style='width:80px;'>DPI</th>
                    <th class='rank-table-header' style='width:70px;'>RF</th>
                    <th class='rank-table-header' style='width:80px;'>LTDD</th>
                    <th class='rank-table-header' style='width:100px;'>Tier</th>
                    <th class='rank-table-header' style='width:80px;'>Δ Rank</th>
                </tr>
            """
            
            # Build table rows
            for _, row in lb.iterrows():
                rank_change = row['Δ Rank']
                rank_indicator = f"<span style='color:#10b981;'>↑ {rank_change}</span>" if rank_change > 0 else f"<span style='color:#ef4444;'>↓ {abs(rank_change)}</span>" if rank_change < 0 else "<span style='color:#6b7280;'>—</span>"
                tier_color = COLOR_MAP.get(row['Tier'], '#6b7280')
                
                table_html += f"""
                <tr class='rank-table-row'>
                    <td class='rank-table-cell' style='font-weight:800; font-size:18px; color:#93c5fd;'>#{row['Rank']}</td>
                    <td class='rank-table-cell' style='font-weight:700;'>{row['Team']}</td>
                    <td class='rank-table-cell' style='font-weight:700; color:#fbbf24;'>{row['DPI']:.1f}</td>
                    <td class='rank-table-cell'>{row['RF']:.0f}</td>
                    <td class='rank-table-cell'>{row['LTDD']:.1f}</td>
                    <td class='rank-table-cell'><span style='background:{tier_color}; padding:4px 10px; border-radius:12px; font-size:11px; font-weight:700;'>{row['Tier']}</span></td>
                    <td class='rank-table-cell'>{rank_indicator}</td>
                </tr>
                """
            
            table_html += "</table>"
            
            # Render complete table
            st.markdown(table_html, unsafe_allow_html=True)
    
    with leaderboard_subtab2:
        # Overall statistics FIRST (moved to top)
        st.markdown("<h3 style='color:white; margin-top:20px;'>📊 Overall Statistics</h3>", unsafe_allow_html=True)
        
        # Use same filtered data
        f1_graph, f2_graph = st.columns([3,1])
        
        with f1_graph:
            stacks_graph = st.multiselect('Stack', options=display_history['Stack'].unique(), default=display_history['Stack'].unique(), key='graph_stack')
        
        with f2_graph:
            tiers_graph = st.multiselect('Tier', options=display_latest_df['Tier'].unique(), default=display_latest_df['Tier'].unique(), key='graph_tier')
        
        lb_graph = display_latest_df[display_latest_df['Stack'].isin(stacks_graph) & display_latest_df['Tier'].isin(tiers_graph)].copy()
        
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        
        with stat_col1:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value'>{lb_graph['RF'].mean():.0f}</div>
                <div class='metric-label'>Avg RF</div>
            </div>
            """, unsafe_allow_html=True)
        
        with stat_col2:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value'>{lb_graph['RF'].max():.0f}</div>
                <div class='metric-label'>Max RF</div>
            </div>
            """, unsafe_allow_html=True)
        
        with stat_col3:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value'>{lb_graph['LTDD'].mean():.1f}</div>
                <div class='metric-label'>Avg LTDD</div>
            </div>
            """, unsafe_allow_html=True)
        
        with stat_col4:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value'>{len(lb_graph)}</div>
                <div class='metric-label'>Teams</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Performance graphs BELOW statistics
        st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:white;'>📈 Performance Metrics Comparison</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color:rgba(255,255,255,0.8); margin-bottom:20px;'>Compare Release Frequency and Lead Time across all teams</p>", unsafe_allow_html=True)
        
        c1,c2 = st.columns(2)

        with c1:
            st.markdown("<p style='color:rgba(255,255,255,0.8); text-align:center; font-weight:600; font-size:16px;'>⚡ Release Frequency (RF)</p>", unsafe_allow_html=True)
            st.bar_chart(lb_graph.set_index('Team')['RF'], color='#06b6d4')

        with c2:
            st.markdown("<p style='color:rgba(255,255,255,0.8); text-align:center; font-weight:600; font-size:16px;'>⏱️ Lead Time (LTDD)</p>", unsafe_allow_html=True)
            st.bar_chart(lb_graph.set_index('Team')['LTDD'], color='#f59e0b')

 

with tab3:
    st.markdown("<h2 style='color:white; text-align:center; margin-bottom:30px;'>🎖️ Achievements & Badges</h2>", unsafe_allow_html=True)
    
    # Layout: Compact criteria on left, main content on right
    criteria_col, content_col = st.columns([1, 3])
    
    with criteria_col:
        st.markdown("""
        <div class='achievement-card' style='background: rgba(96,165,250,0.15); padding:15px;'>
            <div style='font-size:14px; font-weight:700; margin-bottom:12px; color:white;'>📋 Badge Criteria</div>
            <div style='font-size:11px; line-height:1.6; color:rgba(255,255,255,0.9);'>
                <div style='margin-bottom:8px;'><strong>🏆 Release Champion</strong><br/>RF ≥ 250</div>
                <div style='margin-bottom:8px;'><strong>⚡ High Velocity</strong><br/>RF ≥ 180</div>
                <div style='margin-bottom:8px;'><strong>💨 Flow Master</strong><br/>LTDD < 2 days</div>
                <div style='margin-bottom:8px;'><strong>🛡️ Stability Shield</strong><br/>CFR < 5%</div>
                <div style='margin-bottom:8px;'><strong>🤖 Automation Pro</strong><br/>Auto Score = 20</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with content_col:
        # Group teams by badges they've earned
        badge_groups = {
            'Release Champion': [],
            'High Velocity': [],
            'Flow Master': [],
            'Stability Shield': [],
            'Automation Pro': []
        }
        
        for _, row in display_latest_df.iterrows():
            for badge in row['Badges']:
                if badge in badge_groups:
                    badge_groups[badge].append({
                        'Team': row['Team'],
                        'DPI': row['DPI'],
                        'Rank': row['Rank'],
                        'RF': row['RF'],
                        'LTDD': row['LTDD'],
                        'CFR': row['CFR'],
                        'Automation_Score': row.get('Automation_Score', 0)
                    })
        
        # Badge Statistics FIRST
        st.markdown("<h3 style='color:white; margin-bottom:20px;'>📊 Badge Statistics</h3>", unsafe_allow_html=True)
        
        badge_configs = [
            ('Release Champion', '🏆', 'rgba(255,215,0,0.15)', 'RF'),
            ('High Velocity', '⚡', 'rgba(6,182,212,0.15)', 'RF'),
            ('Flow Master', '💨', 'rgba(96,165,250,0.15)', 'LTDD'),
            ('Stability Shield', '🛡️', 'rgba(249,115,22,0.15)', 'CFR'),
            ('Automation Pro', '🤖', 'rgba(16,185,129,0.15)', 'Automation_Score')
        ]
        
        # Display badge statistics first
        stat_cols = st.columns(5)
        for idx, (badge_name, icon, _, _) in enumerate(badge_configs):
            count = len(badge_groups[badge_name])
            with stat_cols[idx]:
                st.markdown(f"""
                <div class='metric-card'>
                    <div style='font-size:36px; margin-bottom:10px;'>{icon}</div>
                    <div class='metric-value' style='font-size:32px;'>{count}</div>
                    <div class='metric-label' style='font-size:11px;'>{badge_name}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Badge Winners BELOW statistics
        st.markdown("<h3 style='color:white; margin-top:40px;'>🏆 Badge Winners</h3>", unsafe_allow_html=True)
        
        for badge_name, icon, bg_color, metric_key in badge_configs:
            teams = badge_groups[badge_name]
            
            if teams:
                # Sort teams by the relevant metric
                if metric_key == 'LTDD':
                    teams_sorted = sorted(teams, key=lambda x: x[metric_key])  # Lower is better
                else:
                    teams_sorted = sorted(teams, key=lambda x: x[metric_key], reverse=True)  # Higher is better
                
                with st.expander(f"{icon} {badge_name} ({len(teams)} teams)", expanded=False):
                    # Display in a grid
                    cols = st.columns(3)
                    for idx, team_data in enumerate(teams_sorted):
                        with cols[idx % 3]:
                            metric_display = ''
                            if metric_key == 'RF':
                                metric_display = f"RF: {team_data['RF']:.0f}"
                            elif metric_key == 'LTDD':
                                metric_display = f"LTDD: {team_data['LTDD']:.1f} days"
                            elif metric_key == 'CFR':
                                metric_display = f"CFR: {team_data['CFR']*100:.1f}%"
                            elif metric_key == 'Automation_Score':
                                metric_display = f"Auto Score: {team_data['Automation_Score']:.0f}/20"
                            
                            st.markdown(f"""
                            <div class='team-card' style='background:{bg_color}; margin-bottom:15px; border: 1px solid rgba(255,255,255,0.1);'>
                                <div style='text-align:center;'>
                                    <div style='font-size:28px; margin-bottom:8px;'>{icon}</div>
                                    <div style='font-size:16px; font-weight:700; margin-bottom:5px; color:white;'>{team_data['Team']}</div>
                                    <div style='font-size:14px; color:rgba(255,255,255,0.8);'>{metric_display}</div>
                                    <div style='font-size:12px; margin-top:5px; color:rgba(255,255,255,0.6);'>DPI: {team_data['DPI']:.1f} | Rank #{team_data['Rank']}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                with st.expander(f"{icon} {badge_name} (0 teams)", expanded=False):
                    st.markdown(f"""
                    <div style='text-align:center; color:rgba(255,255,255,0.6); padding:20px;'>
                        {icon} No teams earned this badge yet
                    </div>
                    """, unsafe_allow_html=True)

 

with tab4:

    st.markdown("<h2 style='color:white; text-align:center; margin-bottom:30px;'>👥 Team Deep Dive</h2>", unsafe_allow_html=True)

    # Natural sort for team numbers
    def natural_sort_key(team_name):
        return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', str(team_name))]
    
    teams_for_detail = sorted(display_history['Team'].unique(), key=natural_sort_key)

    team = st.selectbox('🔍 Select Team for Detailed Analysis', options=teams_for_detail, key='team_detail')

    t_latest = display_latest_df[display_latest_df['Team']==team].iloc[0]

 

    # Top row: left = tier + badges + DPI, right = trend chart

    r1c1, r1c2 = st.columns([2,3])

    with r1c1:
        st.markdown(f"""
        <div class='achievement-card' style='background: linear-gradient(135deg, {COLOR_MAP.get(t_latest['Tier'], '#6b7280')}, {COLOR_MAP.get(t_latest['Tier'], '#6b7280')});'>
            <div class='achievement-icon'>🏆</div>
            <div style='text-align:center;'>
                <div style='font-size:32px; font-weight:800; margin-bottom:10px;'>{t_latest['Tier']}</div>
                <div style='font-size:20px;'>DPI Score: <span style='font-weight:800; color:#ffd700;'>{t_latest['DPI']:.1f}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if t_latest['Badges']:

            st.markdown("<div style='margin-top:20px; text-align:center;'><div style='color:white; font-weight:600; margin-bottom:10px;'>🎖️ Earned Badges</div>" + ' '.join([badge_html(b) for b in t_latest['Badges']]) + '</div>', unsafe_allow_html=True)

    with r1c2:

        st.markdown("<h3 style='color:white;'>📈 Performance Trend (Last 5 Weeks)</h3>", unsafe_allow_html=True)

        team_tr = spark_hist.get(team, pd.Series()).dropna() if isinstance(spark_hist, pd.DataFrame) else pd.Series()

        if not team_tr.empty:

            st.line_chart(team_tr, width='stretch')

        else:

            st.markdown("""
            <div class='achievement-card' style='background: linear-gradient(135deg, #6b7280, #4b5563);'>
                <div style='text-align:center;'>ℹ️ No trend data available</div>
            </div>
            """, unsafe_allow_html=True)

 

    # Second row: left = scores breakdown, right = week-over-week deltas

    r2c1, r2c2 = st.columns([2,2])

    with r2c1:

        st.markdown("<h3 style='color:white; margin-top:30px;'>📊 Detailed Score Breakdown</h3>", unsafe_allow_html=True)

        scores_data = [
            ('⚡ RF Score', t_latest['RF_Score'], 35, '#06b6d4'),
            ('💨 Flow Score', t_latest['Flow_Score'], 25, '#60a5fa'),
            ('🛡️ CFR Score', t_latest['CFR_Score'], 7, '#f97316'),
            ('⏱️ MTTR Score', t_latest['MTTR_Score'], 7, '#f59e0b'),
            ('🔒 Priv Score', t_latest['Priv_Score'], 6, '#8b5cf6'),
            ('🔐 Stability Score', t_latest['Stability_Score'], 20, '#ec4899'),
            ('🤖 Automation Score', t_latest['Automation_Score'], 20, '#10b981')
        ]
        
        for metric, value, max_val, color in scores_data:
            pct = int((value/max_val)*100) if not pd.isna(value) else 0
            st.markdown(f"""
            <div style='margin-bottom:15px;'>
                <div style='display:flex; justify-content:space-between; color:white; font-weight:600; margin-bottom:5px;'>
                    <span>{metric}</span>
                    <span>{value:.1f} / {max_val}</span>
                </div>
                <div class='metric-bar'>
                    <div class='metric-fill' style='width:{pct}%; background:{color};'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with r2c2:

        st.markdown("<h3 style='color:white; margin-top:30px;'>📊 Week-over-Week Changes</h3>", unsafe_allow_html=True)

        if display_prev_week is not None:

            prev_row = display_history[(display_history['Team']==team) & (display_history['Week_Start']==display_prev_week)].iloc[0]

            deltas = {

                '⚡ RF': t_latest['RF'] - prev_row['RF'],

                '⏱️ LTDD': prev_row['LTDD'] - t_latest['LTDD'],

                '🛡️ CFR': prev_row['CFR'] - t_latest['CFR'],

                '⏰ MTTR': prev_row['MTTR'] - t_latest['MTTR'],

                '🎯 DPI': t_latest['DPI'] - prev_row['DPI']

            }

            for metric, delta in deltas.items():
                delta_color = '#10b981' if delta > 0 else '#ef4444' if delta < 0 else '#6b7280'
                delta_icon = '↑' if delta > 0 else '↓' if delta < 0 else '→'
                st.markdown(f"""
                <div class='team-card' style='margin-bottom:10px;'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <span style='color:white; font-weight:600;'>{metric}</span>
                        <span style='color:{delta_color}; font-size:20px; font-weight:800;'>{delta_icon} {abs(delta):.1f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        else:

            st.markdown("""
            <div class='achievement-card' style='background: linear-gradient(135deg, #6b7280, #4b5563);'>
                <div style='text-align:center;'>ℹ️ No previous week data to compare</div>
            </div>
            """, unsafe_allow_html=True)

 

with tab5:

    st.markdown("<h2 style='color:white; text-align:center; margin-bottom:30px;'>📘 Documentation & Guide</h2>", unsafe_allow_html=True)

    col1,col2,col3 = st.columns(3)

    with col1:

        st.markdown("""
        <div class='achievement-card' style='background: linear-gradient(135deg, #3b82f6, #2563eb);'>
            <div class='achievement-icon'>📤</div>
            <div style='text-align:center;'>
                <div style='font-size:20px; font-weight:700; margin-bottom:10px;'>How to Use</div>
                <div style='font-size:14px; opacity:0.9;'>Upload weekly CSV, validate, and publish to add to history. Use BU selector to scope views.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown("""
        <div class='achievement-card' style='background: linear-gradient(135deg, #8b5cf6, #7c3aed);'>
            <div class='achievement-icon'>📊</div>
            <div style='text-align:center;'>
                <div style='font-size:20px; font-weight:700; margin-bottom:10px;'>Scoring Rules</div>
                <div style='font-size:14px; opacity:0.9;'>Open the scoring card at the top for quick rules. Check the expander for detailed scoring breakdown.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:

        st.markdown("""
        <div class='achievement-card' style='background: linear-gradient(135deg, #10b981, #059669);'>
            <div class='achievement-icon'>🎖️</div>
            <div style='text-align:center;'>
                <div style='font-size:20px; font-weight:700; margin-bottom:10px;'>Badges & Tiers</div>
                <div style='font-size:14px; opacity:0.9;'>Badges are awarded based on RF, LTDD, CFR and automation. Tiers reflect overall DPI performance.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

 
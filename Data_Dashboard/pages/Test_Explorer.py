import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
import plotly.graph_objects as go
from itertools import accumulate
import pandas as pd
import io

st.set_page_config(
    page_title="A Page", 
    page_icon="📊"
)

st.title("The Page")

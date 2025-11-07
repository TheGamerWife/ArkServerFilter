import streamlit as st
import requests
import pandas as pd
import time

st.title("ARK Server Monitor")

# Input for session name substring
session_substring = st.text_input("Enter session name substring:", value="TheIsland")

# Fetch server list
url = "https://cdn2.arkdedicated.com/servers/asa/officialserverlist.json"
try:
    all_servers = requests.get(url).json()
except:
    all_servers = []

# Map filter dropdown
map_options = sorted(list({s["MapName"] for s in all_servers}))
selected_map = st.selectbox("Filter by Map", ["All"] + map_options)

# Cluster dropdown depends on map
if selected_map == "All":
    cluster_options = sorted(list({s["ClusterId"] for s in all_servers}))
else:
    cluster_options = sorted(list({s["ClusterId"] for s in all_servers if s["MapName"] == selected_map}))

# Default cluster = PVPCrossplay if available
default_cluster_index = cluster_options.index("PVPCrossplay") if "PVPCrossplay" in cluster_options else 0
selected_cluster = st.selectbox("Filter by Cluster", ["All"] + cluster_options, index=default_cluster_index)

# Start/Stop auto-refresh
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = False

if st.button("Start / Stop Auto Refresh"):
    st.session_state.auto_refresh = not st.session_state.auto_refresh

# Show status
if st.session_state.auto_refresh:
    st.write("🔄 Updating every 10 seconds...")
else:
    st.write("⏸ Auto-refresh paused.")

# Filter servers
matched = [s for s in all_servers if session_substring.lower() in s["Name"].lower()]
if selected_map != "All":
    matched = [s for s in matched if s["MapName"] == selected_map]
if selected_cluster != "All":
    matched = [s for s in matched if s["ClusterId"] == selected_cluster]

# Display results
if matched:
    df = pd.DataFrame(matched)[["Name", "MapName", "ClusterId", "NumPlayers", "IP", "Port"]]
    st.table(df)
    st.write(f"Players Online: {sum(s['NumPlayers'] for s in matched)}")
else:
    st.write("No servers match your filters.")

# Auto rerun every 10 seconds
if st.session_state.auto_refresh:
    time.sleep(10)
    st.rerun()

import streamlit as st
from sgp4.api import Satrec, jday
from datetime import datetime, timezone, timedelta
import requests 
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import base64
import random

st.set_page_config(page_title="Astroshield - Satellite Collision Predictor",layout="wide")

#CSS styling with animation
st.markdown("""
<style>[data-testid="stSidebar"]{
            animation: slideIn 1s ease-in-out;
            }
            @keyframes slideIn{
            from{transform: translateX(-300px); opacity:0;}
            to{tranform:translateX(0); opacity:1;}
            }
            .animation-alert{
            animation:fadeInOut 5s ease-in-out forwards;
            background-color: #ffcccc;
            padding: 1rem;
            margin: 1rem 0;
            border: 1px solid #a94442;
            border-radius: 10px;
            font-weight: bold;
            text-align: center;
            }
            @keyframes fadeInOut{
            0% {opacity:0;}
            10% {opacity:1;}
            90% {opacity:1;}
            100% {opacity:0;}
            }
            .fade-in{
            animation: fadeIn 1.5s ease-in-out
            }
            @keyframes fadeIn{
            from {opacity:0;}
            to {opacity:1;}
            }
            </style>
 """, unsafe_allow_html=True)

#Title and Sidebar 
st.markdown("<h1 style='text-align:center;'>Satellite Collision Predicition</h1",unsafe_allow_html=True)
with st.sidebar:
    st.markdown("<h1 style='color:#4B9CD3;'>Configuration</h3>",unsafe_allow_html=True)
    data_mode= st.radio("Data Mode:",["Live Data","Demo (Simulated Collision)"])
    threshold_km= st.slider("Collision Threshold (km):",1,100,25)
    tle_sources={"GPS-OPS":"https://celestrak.org/NORAD/elements/gp.php?GROUP=gps-ops&FORMAT=tle","Kuiper":"https://celestrak.org/NORAD/elements/gp.php?GROUP=kuiper&FORMAT=tle","OneWeb":"https://celestrak.org/NORAD/elements/gp.php?GROUP=oneweb&FORMAT=tle", "Starlink":"https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle"}
    if data_mode=="Live Data":
        tle_type=st.selectbox("Satellite Group:",list(tle_sources.keys()))
    st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)

#TLE Fetch
def fetch_tle():
    try:
        response = requests.get(tle_sources[tle_type])
        response.raise_for_status()
        tle_lines = response.text.strip().split("\n")
        num_sats = len(tle_lines) // 3
        sample_size = min(25, num_sats)
        random_satellites = random.sample(range(0, num_sats), sample_size)
        return [tle_lines[i * 3:(i + 1) * 3] for i in random_satellites]
    except Exception as e:
        st.error(f"Error fetching TLE: {e}")
        st.stop()

    
#Demo data
def load_demo_tle():
    return [
        ["SAT-A", 
         "1 99991U 24001A   24123.50000000  .00000000  00000-0  00000-0 0  9991",
         "2 99991  51.6000  0.0000 0001000  0.0000  0.0000 15.00000000    01"],
        
        ["SAT-B", 
         "1 99992U 24001B   24123.50000000  .00000000  00000-0  00000-0 0  9992",
         "2 99992  51.6000  0.0000 0001000  0.0005  0.0000 15.00000000    02"],

        ["SAT-C", 
         "1 99993U 24001C   24123.50000000  .00000000  00000-0  00000-0 0  9993",
         "2 99993  51.6000  0.0100 0001000  0.0002  0.0000 15.00000000    03"],

        ["SAT-D", 
         "1 99994U 24001D   24123.50000000  .00000000  00000-0  00000-0 0  9994",
         "2 99994  55.0000  10.0000 0001000  0.0000  0.0000 14.90000000    04"]
    ]


#Orbit propagation function
def propagate(satrec,minutes=90,step=1):
    now=datetime.now()
    coords=[]
    for minute in range(0,minutes,step):
        dt=now + timedelta(minutes=minute)
        jd,fr=jday(dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second)
        e,r,_ = satrec.sgp4(jd,fr)
        if e==0:
            coords.append(r)
    return np.array(coords)

#load TLEs
tle_data=fetch_tle() if data_mode=="Live Data" else load_demo_tle()
sats=[(entry[0],entry[1],entry[2]) for entry in tle_data]

#Collision logic
def detect_collisions(sats,threshold_km):
    collision_events=[]
    now=datetime.now()
    jd,fr=jday(now.year,now.month,now.day,now.hour,now.minute,now.second)
    for i in range(len(sats)):
        for j in range(i+1,len(sats)):
            s1=Satrec.twoline2rv(sats[i][1],sats[i][2])
            s2=Satrec.twoline2rv(sats[j][1],sats[j][2])
            e1,r1,v1=s1.sgp4(jd,fr)
            e2,r2,v2=s2.sgp4(jd,fr)
            dist=np.linalg.norm(np.array(r2)-np.array(r1))
            if e1==0 and e2==0:
                r1_arr=np.array(r1)
                r2_arr=np.array(r2)
                dist=np.linalg.norm(r1_arr - r2_arr)
                if dist<0.001 or np.allclose(r1_arr,r2_arr,atol=1e-3):
                    continue
                rel_pos=r2_arr - r1_arr
                rel_vel=np.array(v2)-np.array(v1)
                t_ca=-np.dot(rel_pos,rel_vel)/np.dot(rel_vel,rel_vel)
                if dist<threshold_km:
                    collision_events.append((sats[i][0], sats[j][0], dist, max(0, t_ca), r1, v1, r2, v2))
    return collision_events

#Maneuver suggestion 
def suggest_manuever(sat_name,pos,vel):
    vel=np.array(vel)
    maneuver_vector=np.cross(vel,[0,0,1])
    maneuver_unit=maneuver_vector/np.linalg.norm(maneuver_vector)
    delta_v=0.01*maneuver_unit
    return delta_v 

#Secondary collision detection
def secondary_collision_check(primary_sat,delta_v,all_sats,threshold_km):
    now=datetime.now()
    jd,fr=jday(now.year,now.month,now.day,now.hour,now.minute,now.second)
    s1=Satrec.twoline2rv(primary_sat[1],primary_sat[2])
    _,r1,v1=s1.sgp4(jd,fr)
    new_v1=np.array(v1) + delta_v
    for sat in all_sats:
        if sat[0]==primary_sat[0]:
            continue
        s2=Satrec.twoline2rv(sat[1],sat[2])
        _,r2,v2=s2.sgp4(jd,fr)
        dist=np.linalg.norm(np.array(r1)-np.array(r2))
        rel_pos=np.array(r2)-np.array(r1)
        rel_vel=np.array(v2)-new_v1
        t_ca=-np.dot(rel_pos,rel_vel)/np.dot(rel_vel,rel_vel)
        if dist<threshold_km and t_ca>0:
            return True
        return False

#Tabs
tab1, tab2= st.tabs(["3D Orbit Visualization","Collision Reports"])

with tab1:
    st.markdown("### Satellite Orbits")
    fig=go.Figure()
    for entry in tle_data:
        name,l1,l2=entry
        sat=Satrec.twoline2rv(l1,l2)
        orbit=propagate(sat)
        if orbit.size>0:
            fig.add_trace(go.Scatter3d(x=orbit[:,0],y=orbit[:,1],z=orbit[:,2],mode='lines',name=name,line=dict(width=2)))
            fig.update_layout(scene=dict(xaxis_title='X',yaxis_title='Y',zaxis_title='Z'), height=700, margin=dict(l=20,r=20,b=50,t=20),showlegend=True,paper_bgcolor='white',plot_bgcolor='white')
            st.plotly_chart(fig,use_container_width=True)

with tab2:
    st.markdown("### Detected Collisions")
    collisions=detect_collisions(sats,threshold_km)
    if collisions:
        for c in collisions:
            st.warning(f"**Collision Risk** between {c[0]} and {c[1]} | Distance: {c[2]:.2f} km | Closest Approach in {c[3]:.1f} seconds")
            #Maneuver suggestion 
            delta_v=suggest_manuever(c[0],c[4],c[5])
            risky=secondary_collision_check((c[0],*[s[1:] for s in sats if s[0] == c[0]][0]),delta_v,sats,threshold_km)
            if risky:
                st.error(f"Suggested maneuver for {c[0]} may cause secondary collision. Choose alternative strategy.")
            else:
                st.info(f"Maneuver Suggestion for {c[0]}: Apply delta v={delta_v.round(5).tolist()} km/s to avoid collision.")
    else:
        st.success("No potential collisions detected at this moment.")
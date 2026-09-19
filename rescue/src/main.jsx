import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity, AlertTriangle, Battery, Check, ChevronRight, CircleUserRound,
  Crosshair, LocateFixed, MapPinned, Navigation, Radio, ShieldCheck,
  Siren, Target, Users, Wifi, X, Zap
} from "lucide-react";
import "./styles.css";

const survivors = [
  { id: "SURV-004", priority: "HIGH", score: 0.87, lat: "13.08241", lon: "80.27731", distance: "420 m", drone: "D2", thermal: true, hazard: "UNKNOWN", status: "NEW" },
  { id: "SURV-003", priority: "MEDIUM", score: 0.76, lat: "13.08122", lon: "80.28142", distance: "760 m", drone: "D1", thermal: true, hazard: "LOW", status: "ASSIGNED" },
  { id: "SURV-002", priority: "LOW", score: 0.68, lat: "13.07994", lon: "80.27488", distance: "1.1 km", drone: "D3", thermal: false, hazard: "UNKNOWN", status: "PENDING" }
];

function App() {
  const [selected, setSelected] = useState(survivors[0]);
  const [alertOpen, setAlertOpen] = useState(true);
  const [missionAccepted, setMissionAccepted] = useState(false);
  const [rescueStatus, setRescueStatus] = useState("STANDBY");
  const [navMode, setNavMode] = useState(false);

  const acceptMission = () => {
    setMissionAccepted(true);
    setAlertOpen(false);
    setRescueStatus("EN ROUTE");
  };

  const markArrived = () => setRescueStatus("ON SCENE");
  const markRescued = () => setRescueStatus("RESCUED");

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark"><Crosshair size={19} /></div>
          <div>
            <div className="brand-name">AEROCUE</div>
            <div className="brand-sub">RESCUE OPERATIONS</div>
          </div>
        </div>
        <div className="connection"><span className="live-dot" /> GCS LINKED</div>
      </header>

      <main>
        <section className="mission-strip">
          <div>
            <div className="eyebrow">ACTIVE OPERATION</div>
            <h1>CHENNAI SEARCH ZONE A</h1>
          </div>
          <div className="mission-stats">
            <span><Radio size={14}/> SWARM 3/3</span>
            <span><Users size={14}/> TEAM 01</span>
            <span><Activity size={14}/> LIVE</span>
          </div>
        </section>

        <section className="map-card">
          <div className="map-toolbar">
            <div><MapPinned size={15}/> LIVE TACTICAL MAP</div>
            <div className="map-status"><span className="live-dot"/> GCS SYNCED</div>
          </div>
          <div className="map">
            <div className="map-grid"/>
            <div className="road r1"/><div className="road r2"/><div className="road r3"/>
            <div className="zone-label z1">SEARCH ZONE A</div>

            <div className="map-marker drone d1"><Zap size={14}/><span>D1</span></div>
            <div className="map-marker drone d2"><Zap size={14}/><span>D2</span></div>
            <div className="map-marker drone d3"><Zap size={14}/><span>D3</span></div>
            <div className="map-marker team"><Navigation size={15}/><span>YOU</span></div>

            {survivors.map((s, i) => (
              <button
                key={s.id}
                className={`map-marker survivor ${selected.id === s.id ? "selected" : ""} p${i}`}
                onClick={() => { setSelected(s); setAlertOpen(s.status === "NEW"); }}
              >
                <Target size={16}/><span>{i + 2}</span>
              </button>
            ))}

            <div className="map-scale">500 m</div>
            <div className="north">N</div>
          </div>
        </section>

        <section className="alert-card">
          <div className="alert-icon"><Siren size={23}/></div>
          <div className="alert-content">
            <div className="alert-title">SURVIVOR DETECTED</div>
            <div className="alert-meta">{selected.id} • DETECTED BY {selected.drone}</div>
          </div>
          <div className="priority">{selected.priority} PRIORITY</div>
        </section>

        <section className="survivor-card">
          <div className="card-head">
            <div>
              <div className="eyebrow">SELECTED CASUALTY</div>
              <h2>{selected.id}</h2>
            </div>
            <div className={`status-pill ${rescueStatus === "RESCUED" ? "safe" : ""}`}>
              {rescueStatus}
            </div>
          </div>

          <div className="metrics">
            <Metric label="AI SCORE" value={`${Math.round(selected.score * 100)}%`} />
            <Metric label="DISTANCE" value={selected.distance} />
            <Metric label="DETECTED BY" value={selected.drone} />
            <Metric label="THERMAL" value={selected.thermal ? "CONFIRMED" : "NO"} />
          </div>

          <div className="location-row">
            <div className="location-icon"><LocateFixed size={18}/></div>
            <div>
              <div className="eyebrow">GPS LOCATION</div>
              <strong>{selected.lat}, {selected.lon}</strong>
            </div>
            <button className="icon-btn" onClick={() => setNavMode(!navMode)} title="Navigation">
              <Navigation size={18}/>
            </button>
          </div>

          <div className="hazard">
            <AlertTriangle size={16}/>
            <span>HAZARD: <strong>{selected.hazard}</strong></span>
            <span className="hazard-note">VERIFY ON SCENE</span>
          </div>

          {!missionAccepted ? (
            <div className="actions">
              <button className="primary-btn" onClick={acceptMission}>
                <Check size={18}/> ACCEPT RESCUE
              </button>
              <button className="secondary-btn" onClick={() => setAlertOpen(false)}>
                DISMISS
              </button>
            </div>
          ) : (
            <div className="workflow">
              <div className="workflow-track">
                {["EN ROUTE", "ON SCENE", "RESCUED"].map((step, i) => (
                  <div key={step} className={`step ${rescueStatus === step ? "current" : ""} ${
                    ["EN ROUTE","ON SCENE","RESCUED"].indexOf(rescueStatus) > i ? "done" : ""
                  }`}>
                    <div className="step-dot">{i + 1}</div><span>{step}</span>
                  </div>
                ))}
              </div>
              {rescueStatus === "EN ROUTE" && (
                <button className="primary-btn" onClick={markArrived}><MapPinned size={18}/> MARK ON SCENE</button>
              )}
              {rescueStatus === "ON SCENE" && (
                <button className="primary-btn rescue-btn" onClick={markRescued}><ShieldCheck size={18}/> MARK RESCUED</button>
              )}
              {rescueStatus === "RESCUED" && (
                <div className="complete"><ShieldCheck size={20}/> RESCUE COMPLETED <ChevronRight size={17}/></div>
              )}
            </div>
          )}
        </section>

        <section className="section-title">
          <div><span className="eyebrow">ALL DETECTIONS</span><h2>Survivor Queue</h2></div>
          <span className="count">{survivors.length}</span>
        </section>

        <section className="queue">
          {survivors.map(s => (
            <button className={`queue-item ${selected.id === s.id ? "active" : ""}`} key={s.id}
              onClick={() => { setSelected(s); setMissionAccepted(s.status === "ASSIGNED"); setRescueStatus(s.status === "ASSIGNED" ? "EN ROUTE" : "STANDBY"); }}>
              <div className={`queue-dot ${s.priority.toLowerCase()}`} />
              <div className="queue-main">
                <strong>{s.id}</strong>
                <span>{s.drone} • {s.distance} • {s.lat}, {s.lon}</span>
              </div>
              <div className="queue-score">{Math.round(s.score * 100)}%</div>
              <ChevronRight size={17}/>
            </button>
          ))}
        </section>

        <section className="team-card">
          <div className="team-avatar"><CircleUserRound size={24}/></div>
          <div className="team-main">
            <div className="eyebrow">RESCUE TEAM</div>
            <strong>TEAM 01 • ALPHA</strong>
            <span><Wifi size={12}/> Local GCS network connected</span>
          </div>
          <div className="battery"><Battery size={15}/> 86%</div>
        </section>
      </main>

      {alertOpen && (
        <div className="alert-overlay">
          <div className="urgent-modal">
            <button className="close" onClick={() => setAlertOpen(false)}><X size={18}/></button>
            <div className="pulse"><Siren size={30}/></div>
            <div className="modal-kicker">NEW PRIORITY ALERT</div>
            <h2>SURVIVOR DETECTED</h2>
            <div className="modal-id">{selected.id}</div>
            <div className="modal-grid">
              <div><span>AI SCORE</span><b>{Math.round(selected.score * 100)}%</b></div>
              <div><span>DISTANCE</span><b>{selected.distance}</b></div>
              <div><span>DRONE</span><b>{selected.drone}</b></div>
              <div><span>THERMAL</span><b>{selected.thermal ? "YES" : "NO"}</b></div>
            </div>
            <button className="primary-btn big" onClick={acceptMission}><Navigation size={19}/> ACCEPT & NAVIGATE</button>
            <button className="ghost-btn" onClick={() => setAlertOpen(false)}>VIEW DETAILS FIRST</button>
          </div>
        </div>
      )}

      {navMode && (
        <div className="nav-banner">
          <Navigation size={18}/>
          <div><strong>NAVIGATION ACTIVE</strong><span>Heading toward {selected.id} • {selected.distance} remaining</span></div>
          <button onClick={() => setNavMode(false)}><X size={16}/></button>
        </div>
      )}
    </div>
  );
}

function Metric({label, value}) {
  return <div className="metric"><span>{label}</span><strong>{value}</strong></div>;
}

createRoot(document.getElementById("root")).render(<App />);

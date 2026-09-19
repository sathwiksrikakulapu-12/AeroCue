import {
  Battery,
  Gauge,
  Navigation,
  Satellite,
  Signal,
  Wifi,
} from "lucide-react";

import "./TelemetryPanel.css";

function TelemetryPanel({ drones }) {
  return (
    <section className="telemetry-panel">
      <div className="telemetry-header">
        <div>
          <div className="telemetry-title-row">
            <Satellite size={18} />
            <h2>GPS & TELEMETRY</h2>
          </div>

          <p>Live swarm telemetry</p>
        </div>

        <div className="telemetry-live">
          <span className="live-dot"></span>
          LIVE
        </div>
      </div>

      <div className="telemetry-grid">
        {drones.map((drone) => (
          <div
            className="drone-telemetry-card"
            key={drone.id}
          >
            <div className="drone-card-header">
              <div>
                <span className="drone-label">
                  {drone.shortId}
                </span>

                <h3>{drone.id}</h3>
              </div>

              <div className="connected-status">
                <span></span>
                CONNECTED
              </div>
            </div>

            <div className="telemetry-main">
              <div className="gps-location">
                <Satellite size={15} />

                <div>
                  <span>LATITUDE</span>

                  <strong>
                    {drone.latitude.toFixed(5)}° N
                  </strong>
                </div>
              </div>

              <div className="gps-location">
                <Navigation size={15} />

                <div>
                  <span>LONGITUDE</span>

                  <strong>
                    {drone.longitude.toFixed(5)}° E
                  </strong>
                </div>
              </div>
            </div>

            <div className="telemetry-stats">
              <div className="telemetry-stat">
                <Gauge size={16} />

                <div>
                  <span>ALTITUDE</span>

                  <strong>
                    {drone.altitude.toFixed(1)} m
                  </strong>
                </div>
              </div>

              <div className="telemetry-stat">
                <Navigation size={16} />

                <div>
                  <span>SPEED</span>

                  <strong>
                    {drone.speed.toFixed(1)} m/s
                  </strong>
                </div>
              </div>

              <div className="telemetry-stat">
                <Signal size={16} />

                <div>
                  <span>HEADING</span>

                  <strong>
                    {drone.heading.toFixed(0)}°
                  </strong>
                </div>
              </div>

              <div className="telemetry-stat">
                <Battery size={16} />

                <div>
                  <span>BATTERY</span>

                  <strong>
                    {drone.battery.toFixed(0)}%
                  </strong>
                </div>
              </div>
            </div>

            <div className="telemetry-footer">
              <div>
                <Wifi size={14} />
                NETWORK LINK
              </div>

              <span>STABLE</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

export default TelemetryPanel;
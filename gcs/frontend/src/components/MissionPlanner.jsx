import { useState } from "react";
import {
  MapPinned,
  Route,
  Plane,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";

import {
  generateSearchMission,
} from "../missionPlanner";

import "./MissionPlanner.css";

function MissionPlanner({ onMissionGenerated }) {
  const [area, setArea] = useState({
    north: "13.0865",
    south: "13.0785",
    west: "80.2700",
    east: "80.2850",
  });

  const [droneCount, setDroneCount] = useState(3);
  const [pointsPerStrip, setPointsPerStrip] = useState(6);

  const [mission, setMission] = useState(null);
  const [error, setError] = useState("");

  const handleChange = (field, value) => {
    setArea((previous) => ({
      ...previous,
      [field]: value,
    }));
  };

  const handleGenerate = () => {
    setError("");

    try {
      const numericArea = {
        north: Number(area.north),
        south: Number(area.south),
        west: Number(area.west),
        east: Number(area.east),
      };

      const generatedMission =
        generateSearchMission(
          numericArea,
          Number(droneCount),
          Number(pointsPerStrip)
        );

      setMission(generatedMission);

      if (onMissionGenerated) {
        onMissionGenerated(generatedMission);
      }
    } catch (err) {
      setMission(null);
      setError(err.message);
    }
  };

  return (
    <section className="mission-planner">

      {/* HEADER */}
      <div className="mission-planner-header">

        <div>
          <div className="mission-planner-title">
            <MapPinned size={18} />
            <h2>MISSION PLANNER</h2>
          </div>

          <p>
            Define search area and generate
            synchronized drone search strips.
          </p>
        </div>

        <div className="planner-status">
          <span
            className={
              mission
                ? "planner-dot ready"
                : "planner-dot"
            }
          ></span>

          {mission
            ? "MISSION READY"
            : "PLANNING"}
        </div>

      </div>


      {/* INPUT AREA */}
      <div className="planner-input-area">

        <div className="coordinate-section">

          <div className="section-heading">
            <MapPinned size={15} />
            SEARCH AREA
          </div>

          <div className="coordinate-grid">

            <label>
              <span>NORTH LATITUDE</span>

              <input
                type="number"
                step="0.0001"
                value={area.north}
                onChange={(e) =>
                  handleChange(
                    "north",
                    e.target.value
                  )
                }
              />
            </label>

            <label>
              <span>SOUTH LATITUDE</span>

              <input
                type="number"
                step="0.0001"
                value={area.south}
                onChange={(e) =>
                  handleChange(
                    "south",
                    e.target.value
                  )
                }
              />
            </label>

            <label>
              <span>WEST LONGITUDE</span>

              <input
                type="number"
                step="0.0001"
                value={area.west}
                onChange={(e) =>
                  handleChange(
                    "west",
                    e.target.value
                  )
                }
              />
            </label>

            <label>
              <span>EAST LONGITUDE</span>

              <input
                type="number"
                step="0.0001"
                value={area.east}
                onChange={(e) =>
                  handleChange(
                    "east",
                    e.target.value
                  )
                }
              />
            </label>

          </div>

        </div>


        {/* MISSION SETTINGS */}
        <div className="mission-settings">

          <div className="section-heading">
            <Route size={15} />
            MISSION SETTINGS
          </div>

          <div className="settings-grid">

            <label>
              <span>ACTIVE DRONES</span>

              <select
                value={droneCount}
                onChange={(e) =>
                  setDroneCount(
                    Number(e.target.value)
                  )
                }
              >
                <option value={1}>1 DRONE</option>
                <option value={2}>2 DRONES</option>
                <option value={3}>3 DRONES</option>
              </select>
            </label>

            <label>
              <span>WAYPOINTS / STRIP</span>

              <select
                value={pointsPerStrip}
                onChange={(e) =>
                  setPointsPerStrip(
                    Number(e.target.value)
                  )
                }
              >
                <option value={4}>4</option>
                <option value={6}>6</option>
                <option value={8}>8</option>
                <option value={10}>10</option>
                <option value={12}>12</option>
              </select>
            </label>

          </div>

        </div>

      </div>


      {/* GENERATE BUTTON */}
      <button
        className="generate-mission-button"
        onClick={handleGenerate}
      >
        <Route size={17} />
        GENERATE SEARCH MISSION
      </button>


      {/* ERROR */}
      {error && (
        <div className="planner-error">
          <AlertTriangle size={16} />
          {error}
        </div>
      )}


      {/* GENERATED MISSION */}
      {mission && (
        <div className="generated-mission">

          <div className="generated-header">

            <div>
              <span>MISSION PLAN</span>

              <strong>
                {mission.totalWaypoints} WAYPOINTS
              </strong>
            </div>

            <div className="mission-ready">
              <CheckCircle2 size={16} />
              READY
            </div>

          </div>


          {/* DRONE ASSIGNMENTS */}
          <div className="strip-list">

            {mission.strips.map(
              (strip) => (
                <div
                  className="strip-row"
                  key={strip.stripId}
                >

                  <div className="strip-drone">

                    <div className="strip-icon">
                      <Plane size={16} />
                    </div>

                    <div>
                      <strong>
                        {strip.droneId}
                      </strong>

                      <span>
                        {strip.stripId}
                      </span>
                    </div>

                  </div>


                  <div className="strip-direction">

                    <span>
                      SEARCH DIRECTION
                    </span>

                    <strong>
                      {strip.waypoints[0]
                        .longitude <
                      strip.waypoints[
                        strip.waypoints.length - 1
                      ].longitude
                        ? "WEST → EAST"
                        : "EAST → WEST"}
                    </strong>

                  </div>


                  <div className="strip-waypoints">

                    <span>
                      WAYPOINTS
                    </span>

                    <strong>
                      {strip.waypoints.length}
                    </strong>

                  </div>

                </div>
              )
            )}

          </div>


          {/* WAYPOINT PREVIEW */}
          <div className="waypoint-preview">

            <div className="section-heading">
              <Route size={15} />
              WAYPOINT PREVIEW
            </div>

            <div className="waypoint-table">

              <div className="waypoint-table-header">
                <span>DRONE</span>
                <span>WP</span>
                <span>LATITUDE</span>
                <span>LONGITUDE</span>
              </div>

              {mission.strips.flatMap(
                (strip) =>
                  strip.waypoints.map(
                    (waypoint) => (
                      <div
                        className="waypoint-row"
                        key={`${strip.droneId}-${waypoint.waypoint}`}
                      >
                        <span>
                          {strip.droneId}
                        </span>

                        <span>
                          WP-{waypoint.waypoint}
                        </span>

                        <span>
                          {waypoint.latitude.toFixed(
                            6
                          )}
                        </span>

                        <span>
                          {waypoint.longitude.toFixed(
                            6
                          )}
                        </span>
                      </div>
                    )
                  )
              )}

            </div>

          </div>

        </div>
      )}

    </section>
  );
}

export default MissionPlanner;
import React from "react";

function MissionPaths({ mission }) {
  if (!mission || !mission.strips) {
    return null;
  }

  const mapWidth = 1000;
  const mapHeight = 500;

  /*
   * Responsive padding.
   * Coordinates are kept away from the edges
   * so WP1, WP6 and labels remain visible.
   */
  const paddingX = 65;
  const paddingY = 55;

  const minLatitude = 13.0785;
  const maxLatitude = 13.0865;

  const minLongitude = 80.2700;
  const maxLongitude = 80.2850;

  function gpsToSvgPoint(latitude, longitude) {
    const usableWidth =
      mapWidth - paddingX * 2;

    const usableHeight =
      mapHeight - paddingY * 2;

    const x =
      paddingX +
      ((longitude - minLongitude) /
        (maxLongitude - minLongitude)) *
        usableWidth;

    const y =
      paddingY +
      ((maxLatitude - latitude) /
        (maxLatitude - minLatitude)) *
        usableHeight;

    return {
      x,
      y,
    };
  }

  return (
    <svg
      className="mission-path-overlay"
      viewBox={`0 0 ${mapWidth} ${mapHeight}`}
      preserveAspectRatio="xMidYMid meet"
      width="100%"
      height="100%"
      style={{
        display: "block",
        width: "100%",
        height: "100%",
      }}
    >
      {mission.strips.map((strip) => {
        const points =
          strip.waypoints.map(
            (waypoint) =>
              gpsToSvgPoint(
                waypoint.latitude,
                waypoint.longitude
              )
          );

        const pointString =
          points
            .map(
              (point) =>
                `${point.x},${point.y}`
            )
            .join(" ");

        const firstPoint =
          points[0];

        const lastPoint =
          points[points.length - 1];

        return (
          <g
            key={strip.stripId}
          >

            {/* SEARCH PATH */}

            <polyline
              points={pointString}
              fill="none"
              stroke="rgba(55, 160, 255, 0.75)"
              strokeWidth="2"
              vectorEffect="non-scaling-stroke"
            />

            {/* WAYPOINTS */}

            {points.map(
              (
                point,
                waypointIndex
              ) => (
                <g
                  key={`${strip.stripId}-wp-${waypointIndex}`}
                >
                  <circle
                    cx={point.x}
                    cy={point.y}
                    r="5"
                    fill="rgba(55, 160, 255, 0.95)"
                    stroke="rgba(255,255,255,0.9)"
                    strokeWidth="1"
                    vectorEffect="non-scaling-stroke"
                  />

                  <text
                    x={point.x}
                    y={point.y - 10}
                    textAnchor="middle"
                    className="mission-waypoint-label"
                  >
                    WP{waypointIndex + 1}
                  </text>
                </g>
              )
            )}

            {/* DRONE LABEL */}

            {firstPoint && (
              <text
                x={firstPoint.x}
                y={firstPoint.y + 25}
                className="mission-strip-label"
              >
                {strip.droneId}
              </text>
            )}

            {/* SEARCH DIRECTION */}

            {firstPoint &&
              lastPoint && (
                <text
                  x={
                    firstPoint.x +
                    (lastPoint.x -
                      firstPoint.x) /
                      2
                  }
                  y={
                    firstPoint.y - 18
                  }
                  textAnchor="middle"
                  className="mission-direction-label"
                >
                  {lastPoint.x >
                  firstPoint.x
                    ? "→"
                    : "←"}
                </text>
              )}

          </g>
        );
      })}
    </svg>
  );
}

export default MissionPaths;
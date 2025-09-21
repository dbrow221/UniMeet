// frontend/src/components/CampusBuildings.jsx
import React, { useState } from "react";
import { GeoJSON } from "react-leaflet";
import * as turf from "@turf/turf";

const CampusBuildings = ({ geojsonData }) => {
  const [highlightedLayer, setHighlightedLayer] = useState(null);

  const buildingStyle = {
    color: "#006400", // default border
    weight: 2,
    fillColor: "#66bb6a",
    fillOpacity: 0.4,
  };

  const onEachFeature = (feature, layer) => {
    if (feature.properties && feature.properties.name) {
      layer.bindPopup(`<b>${feature.properties.name}</b>`);

      layer.on({
        click: () => {
          // Remove previous highlight
          if (highlightedLayer) {
            highlightedLayer.setStyle(buildingStyle);
          }

          // Highlight clicked building
          layer.setStyle({
            color: "blue",
            fillColor: "#3399FF",
            fillOpacity: 0.6,
            weight: 3,
          });
          setHighlightedLayer(layer);

          // Get centroid of building
          const centroid = turf.centroid(feature);
          const [lng, lat] = centroid.geometry.coordinates;

          // Send to backend
          fetch("/api/locations/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              name: feature.properties.name,
              latitude: lat,
              longitude: lng,
            }),
          })
            .then((res) => res.json())
            .then((data) => console.log("Saved location:", data));
        },
        mouseover: (e) => {
          e.target.setStyle({ fillOpacity: 0.7 });
        },
        mouseout: (e) => {
          if (layer !== highlightedLayer) {
            layer.setStyle(buildingStyle);
          }
        },
      });
    }
  };

  return <GeoJSON data={geojsonData} style={buildingStyle} onEachFeature={onEachFeature} />;
};

export default CampusBuildings;

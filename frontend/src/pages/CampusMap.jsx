// frontend/src/components/CampusMap.jsx
import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, GeoJSON } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "../styles/CampusMap.css";

// Helper to calculate centroid of a polygon
const getCentroid = (coords) => {
  let latSum = 0;
  let lngSum = 0;
  let count = 0;

  coords[0].forEach(([lng, lat]) => {
    latSum += lat;
    lngSum += lng;
    count++;
  });

  return {
    lat: latSum / count,
    lng: lngSum / count,
  };
};

const CampusMap = () => {
  const [geoData, setGeoData] = useState(null);
  const [selected, setSelected] = useState(null);
  const [highlightedLayer, setHighlightedLayer] = useState(null);

  // Load campus buildings GeoJSON from public folder
  useEffect(() => {
  fetch("/data/campus-buildings.geojson")
    .then((res) => {
      console.log("Fetch response status:", res.status); // 200 = OK
      console.log("Fetch response headers:", res.headers);
      return res.text(); // first get raw text
    })
    .then((text) => {
      console.log("Raw fetch text:", text.substring(0, 500)); // log first 500 chars
      try {
        const data = JSON.parse(text); // try parsing JSON manually
        console.log("Parsed GeoJSON data:", data);
        setGeoData(data);
      } catch (err) {
        console.error("Failed to parse GeoJSON:", err);
      }
    })
    .catch((err) => console.error("Error loading GeoJSON:", err));
}, []);

  // Default style for buildings
  const buildingStyle = {
    color: "#006400",
    weight: 2,
    fillColor: "#66bb6a",
    fillOpacity: 0.4,
  };

  // Handle clicks on each building
  const onEachFeature = (feature, layer) => {
    layer.on({
      click: () => {
        // Reset previous highlight
        if (highlightedLayer) {
          highlightedLayer.setStyle(buildingStyle);
        }

        // Highlight clicked building
        layer.setStyle({
          color: "#ff0000",
          weight: 3,
          fillColor: "#ff6666",
          fillOpacity: 0.5,
        });

        setHighlightedLayer(layer);

        // Compute centroid for polygon or multipolygon
        let centroid = { lat: null, lng: null };
        if (feature.geometry.type === "Polygon") {
          centroid = getCentroid(feature.geometry.coordinates);
        } else if (feature.geometry.type === "MultiPolygon") {
          centroid = getCentroid(feature.geometry.coordinates[0]);
        }

        // Create building object
        const building = {
          name: feature.properties.name || "Unnamed Building",
          latitude: centroid.lat,
          longitude: centroid.lng,
        };

        // Update local selection
        setSelected(building);

        // POST to backend
        fetch("/api/locations/create/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(building),
        })
          .then((res) => res.json())
          .then((data) => console.log("Saved location:", data))
          .catch((err) => console.error("Error saving location:", err));
      },
    });

    // Bind popup showing building name
    if (feature.properties && feature.properties.name) {
      layer.bindPopup(`<b>${feature.properties.name}</b>`);
    }
  };

  return (
    <div className="map-wrapper">
      <h1>Select a Campus Building</h1>
      <MapContainer center={[35.3076, -80.733]} zoom={16} className="campus-map">
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />

        {geoData && (
          <GeoJSON
            data={geoData}
            style={buildingStyle}
            onEachFeature={onEachFeature}
          />
        )}
      </MapContainer>

      {selected && (
        <div className="selection-info">
          <p>
            ✅ Selected: <b>{selected.name}</b> ({selected.latitude.toFixed(5)}, {selected.longitude.toFixed(5)})
          </p>
        </div>
      )}
    </div>
  );
};

export default CampusMap;

// frontend/src/components/CampusMap.jsx
import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, GeoJSON, Marker, Popup } from "react-leaflet";
import { useNavigate } from "react-router-dom";
import "leaflet/dist/leaflet.css";
import "../styles/CampusMap.css";
import L from "leaflet";

import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import { ACCESS_TOKEN } from "../constants";

const DefaultIcon = L.icon({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});
L.Marker.prototype.options.icon = DefaultIcon;

// Helper to calculate centroid
const getCentroid = (coords) => {
  let latSum = 0, lngSum = 0, count = 0;
  coords[0].forEach(([lng, lat]) => {
    latSum += lat;
    lngSum += lng;
    count++;
  });
  return { lat: latSum / count, lng: lngSum / count };
};

const CampusMap = () => {
  const [geoData, setGeoData] = useState(null);
  const [selected, setSelected] = useState(null);
  const [highlightedLayer, setHighlightedLayer] = useState(null);
  const [events, setEvents] = useState([]);
  const navigate = useNavigate();

  // Load campus buildings
  useEffect(() => {
    fetch("/data/campus-buildings.geojson")
      .then(res => res.json())
      .then(setGeoData)
      .catch(err => console.error("Error loading GeoJSON:", err));
  }, []);

  // Load events
  useEffect(() => {
    const token = localStorage.getItem(ACCESS_TOKEN);
    if (!token) return console.warn("No access token. Cannot load events.");

    fetch("http://127.0.0.1:8000/api/events/", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(async (res) => {
        if (!res.ok) throw new Error(await res.text());
        return res.json();
      })
      .then((data) => setEvents(Array.isArray(data) ? data.filter(e => e.is_public) : []))
      .catch(err => console.error("Error loading events:", err));
  }, []);

  const buildingStyle = {
    color: "#006400",
    weight: 2,
    fillColor: "#66bb6a",
    fillOpacity: 0.4,
  };

  const onEachFeature = (feature, layer) => {
    layer.on({
      click: async () => {
        if (highlightedLayer) highlightedLayer.setStyle(buildingStyle);

        layer.setStyle({
          color: "#ff0000",
          weight: 3,
          fillColor: "#ff6666",
          fillOpacity: 0.5,
        });

        setHighlightedLayer(layer);

        let centroid = { lat: null, lng: null };
        if (feature.geometry.type === "Polygon") centroid = getCentroid(feature.geometry.coordinates);
        else if (feature.geometry.type === "MultiPolygon") centroid = getCentroid(feature.geometry.coordinates[0]);

        const building = {
          name: feature.properties.name || "Unnamed Building",
          latitude: centroid.lat,
          longitude: centroid.lng,
        };

        // POST location and get ID
        const token = localStorage.getItem(ACCESS_TOKEN);
        if (token) {
          try {
            const response = await fetch("http://127.0.0.1:8000/api/locations/create/", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
              },
              body: JSON.stringify(building),
            });

            if (response.ok) {
              const savedLocation = await response.json(); // includes id
              setSelected(savedLocation); // pass location with ID to CreateEvent
            } else {
              console.error("Failed to save location:", await response.text());
              setSelected(building); // fallback
            }
          } catch (err) {
            console.error("Network error saving location:", err);
            setSelected(building); // fallback
          }
        } else {
          setSelected(building); // fallback if no token
        }
      },
    });

    if (feature.properties?.name) {
      layer.bindPopup(`<b>${feature.properties.name}</b>`);
    }
  };

  return (
    <div className="map-wrapper">
      <h1>Campus Map</h1>
      <MapContainer center={[35.3076, -80.733]} zoom={16} className="campus-map">
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />
        {geoData && <GeoJSON data={geoData} style={buildingStyle} onEachFeature={onEachFeature} />}
        {events.map(event => (
          <Marker
            key={event.id}
            position={[event.location.latitude, event.location.longitude]}
          >
            <Popup>
              <b>{event.name}</b><br/>
              {event.details}<br/>
              📍 {event.location.name}
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {selected && (
        <div className="selection-info">
          <p>
            ✅ Selected: <b>{selected.name}</b> (
            {selected.latitude != null ? selected.latitude.toFixed(5) : "N/A"}, 
            {selected.longitude != null ? selected.longitude.toFixed(5) : "N/A"})
          </p>
          <button
            className="select-location-btn"
            onClick={() => navigate("/create-event", { state: { location: selected } })}
          >
            Select Location
          </button>
        </div>
      )}
    </div>
  );
};

export default CampusMap;

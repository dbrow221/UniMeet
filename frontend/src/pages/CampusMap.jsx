// frontend/src/components/CampusMap.jsx
import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "../styles/CampusMap.css";
import CampusBuildings from "./CampusBuldings";

const CampusMap = () => {
  const [locations, setLocations] = useState([]);
  const [geoData, setGeoData] = useState(null);
  const [selected, setSelected] = useState(null);
  const [customMarker, setCustomMarker] = useState(null);
  const [highlightedLayer, setHighlightedLayer] = useState(null);

  // Load saved locations from backend
  useEffect(() => {
    fetch("/api/locations/")
      .then((res) => res.json())
      .then((data) => setLocations(data));
  }, []);

  // Load campus buildings GeoJSON from public folder
  useEffect(() => {
    fetch("/data/campus-buildings.geojson")
      .then((res) => res.json())
      .then((data) => setGeoData(data));
  }, []);

  const handleSelect = (location) => {
    setSelected(location);
    console.log("Selected location:", location);
  };

  // Custom click marker component
  const LocationMarker = () => {
    useMapEvents({
      click(e) {
        const { lat, lng } = e.latlng;

        // Remove building highlight if any
        if (highlightedLayer) {
          highlightedLayer.setStyle({
            color: "#006400",
            fillColor: "#66bb6a",
            fillOpacity: 0.4,
            weight: 2,
          });
          setHighlightedLayer(null);
        }

        // Set custom marker
        setCustomMarker([lat, lng]);

        // Mark as selected
        handleSelect({ name: "Custom Spot", lat, lng });

        // Optional: POST to backend
        fetch("/api/locations/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: "Custom Spot", latitude: lat, longitude: lng }),
        })
          .then((res) => res.json())
          .then((data) => console.log("Saved location:", data));
      },
    });

    return customMarker ? (
      <Marker position={customMarker}>
        <Popup>
          <b>Selected Location</b>
          <br />
          Lat: {customMarker[0].toFixed(5)}, Lng: {customMarker[1].toFixed(5)}
        </Popup>
      </Marker>
    ) : null;
  };

  return (
    <div className="map-wrapper">
      <MapContainer center={[35.3076, -80.733]} zoom={16} className="campus-map">
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />

        {/* Existing saved locations */}
        {locations.map((loc) => (
          <Marker key={loc.id} position={[loc.latitude, loc.longitude]}>
            <Popup>
              <b>{loc.name}</b>
              <br />
              {loc.address}
            </Popup>
          </Marker>
        ))}

        {/* GeoJSON campus buildings */}
        {geoData && (
          <CampusBuildings
            geojsonData={geoData}
            highlightedLayer={highlightedLayer}
            setHighlightedLayer={setHighlightedLayer}
            handleSelect={handleSelect}
          />
        )}

        {/* Custom click marker */}
        <LocationMarker />
      </MapContainer>

      {selected && (
        <div className="selection-info">
          <p>
            ✅ Selected: <b>{selected.name}</b>{" "}
            {selected.lat && selected.lng
              ? `(${selected.lat.toFixed(5)}, ${selected.lng.toFixed(5)})`
              : ""}
          </p>
        </div>
      )}
    </div>
  );
};

export default CampusMap;

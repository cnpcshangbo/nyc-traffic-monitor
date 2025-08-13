import { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default markers in React Leaflet
delete (L.Icon.Default.prototype as unknown as { _getIconUrl?: unknown })._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

interface Location {
  id: string;
  name: string;
  coordinates: [number, number];
  videoPath: string;
}

interface MapViewProps {
  locations: Location[];
  onLocationSelect: (location: Location) => void;
  selectedLocation: Location | null;
}

const MapView: React.FC<MapViewProps> = ({ locations, onLocationSelect, selectedLocation }) => {
  const mapRef = useRef<L.Map | null>(null);

  useEffect(() => {
    if (selectedLocation && mapRef.current) {
      mapRef.current.flyTo(selectedLocation.coordinates, 16, {
        duration: 1
      });
    }
  }, [selectedLocation]);

  useEffect(() => {
    if (mapRef.current && locations.length > 0 && !selectedLocation) {
      // Calculate bounds to fit all locations
      const bounds = L.latLngBounds(locations.map(loc => loc.coordinates));
      mapRef.current.fitBounds(bounds, { 
        padding: [20, 20],
        maxZoom: 12
      });
    }
  }, [locations, selectedLocation]);

  const handleHomeClick = () => {
    if (mapRef.current && locations.length > 0) {
      const bounds = L.latLngBounds(locations.map(loc => loc.coordinates));
      mapRef.current.flyToBounds(bounds, { 
        padding: [20, 20],
        maxZoom: 12,
        duration: 1
      });
    }
  };

  const selectedIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  });

  const defaultIcon = new L.Icon({
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  });

  return (
    <div style={{ position: 'relative' }}>
      <MapContainer
        center={[40.7200, -74.0000]}
        zoom={10}
        style={{ height: '500px', width: '100%' }}
        whenReady={(map) => {
          mapRef.current = map.target;
        }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {locations.map((location) => (
          <Marker
            key={location.id}
            position={location.coordinates}
            icon={selectedLocation?.id === location.id ? selectedIcon : defaultIcon}
            eventHandlers={{
              click: () => onLocationSelect(location),
            }}
          >
            <Popup>
              <div style={{ textAlign: 'center' }}>
                <strong>{location.name}</strong>
                <br />
                <button
                  onClick={() => onLocationSelect(location)}
                  style={{
                    marginTop: '8px',
                    padding: '4px 8px',
                    backgroundColor: '#007bff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  View Traffic Data
                </button>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
      
      <button
        onClick={handleHomeClick}
        style={{
          position: 'absolute',
          top: '10px',
          right: '10px',
          zIndex: 1000,
          padding: '8px 12px',
          backgroundColor: '#fff',
          border: '2px solid rgba(0,0,0,0.2)',
          borderRadius: '6px',
          boxShadow: '0 1px 5px rgba(0,0,0,0.4)',
          cursor: 'pointer',
          fontSize: '14px',
          fontWeight: 'bold',
          color: '#333',
          display: 'flex',
          alignItems: 'center',
          gap: '4px',
          transition: 'all 0.2s ease'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = '#f8f9fa';
          e.currentTarget.style.transform = 'scale(1.05)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = '#fff';
          e.currentTarget.style.transform = 'scale(1)';
        }}
        title="Zoom to show all locations"
      >
        🏠 Home
      </button>
    </div>
  );
};

export default MapView;
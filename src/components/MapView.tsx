import { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default markers in React Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
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
    <MapContainer
      center={[40.7831, -73.9778]}
      zoom={14}
      style={{ height: '500px', width: '100%' }}
      ref={mapRef}
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
  );
};

export default MapView;
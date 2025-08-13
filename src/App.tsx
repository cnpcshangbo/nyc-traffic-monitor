import { useState, useRef } from 'react';
import MapView from './components/MapView';
import VideoPlayerEnhanced from './components/VideoPlayerEnhanced';
import TrafficChart from './components/TrafficChart';
import SchemaSelector from './components/SchemaSelector';
import CustomSchemaDialog from './components/CustomSchemaDialog';
import VideoUploader from './components/VideoUploader';
import { Detection, ObjectDetectionService } from './services/objectDetection';
import { ClassificationSchema, predefinedSchemas } from './config/schemas';
import './App.css';

interface Location {
  id: string;
  name: string;
  coordinates: [number, number];
  videoPath: string;
}

const locations: Location[] = [
  {
    id: '74th-amsterdam-columbus',
    name: 'Richmond Hill Rd & Edinboro Rd, Staten Island',
    coordinates: [40.5761, -74.1412],
    videoPath: '../74th-Amsterdam-Columbus/2025-02-13_06-00-04.mp4'
  },
  {
    id: 'amsterdam-80th',
    name: 'Arthur Kill Rd & Storer Ave, Staten Island',
    coordinates: [40.5338, -74.2369],
    videoPath: '../Amsterdam-80th/2025-02-13_06-00-04.mp4'
  },
  {
    id: 'columbus-86th',
    name: 'Katonah Ave & East 241st St, Bronx',
    coordinates: [40.9030, -73.8500],
    videoPath: '../Columbus-86th/2025-02-13_06-00-06.mp4'
  }
];

function App() {
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [currentDetections, setCurrentDetections] = useState<Detection[]>([]);
  const [selectedSchema, setSelectedSchema] = useState<ClassificationSchema | null>(predefinedSchemas[0]);
  const [customSchemas, setCustomSchemas] = useState<ClassificationSchema[]>([]);
  const [showCustomDialog, setShowCustomDialog] = useState(false);
  const [uploadedLocations, setUploadedLocations] = useState<Location[]>([]);
  const [allLocations, setAllLocations] = useState<Location[]>(locations);
  const detectionServiceRef = useRef(new ObjectDetectionService());

  const handleLocationSelect = (location: Location) => {
    setSelectedLocation(location);
    setCurrentTime(0);
    detectionServiceRef.current.clearHistory();
  };

  const handleTimeUpdate = (time: number) => {
    setCurrentTime(time);
  };

  const handleDetections = (detections: Detection[]) => {
    setCurrentDetections(detections);
  };

  const handleExportCSV = (aggregationLevel: string) => {
    const aggregationMap: { [key: string]: number } = {
      '15s': 15,
      '30s': 30,
      '5min': 300,
      '15min': 900
    };
    
    const aggregationSeconds = aggregationMap[aggregationLevel];
    if (aggregationSeconds) {
      const csv = detectionServiceRef.current.exportToCSV(aggregationSeconds);
      
      // Create a download link
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `traffic_data_${selectedLocation?.id}_${selectedSchema?.id}_${aggregationLevel}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    }
  };

  const handleAddCustomSchema = (schema: ClassificationSchema) => {
    setCustomSchemas([...customSchemas, schema]);
    setSelectedSchema(schema);
  };

  const handleVideoUpload = (file: File, customLocation: string) => {
    // Create a blob URL for the uploaded video
    const videoUrl = URL.createObjectURL(file);
    
    // Create a new location for the uploaded video
    const newLocation: Location = {
      id: `uploaded-${Date.now()}`,
      name: customLocation,
      coordinates: [40.7831, -73.9778], // Default coordinates (can be updated later)
      videoPath: videoUrl
    };

    // Add to uploaded locations and all locations
    const updatedUploaded = [...uploadedLocations, newLocation];
    const updatedAll = [...allLocations, newLocation];
    
    setUploadedLocations(updatedUploaded);
    setAllLocations(updatedAll);
    
    // Automatically select the uploaded video
    setSelectedLocation(newLocation);
    setCurrentTime(0);
    detectionServiceRef.current.clearHistory();
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Urban Mobility Data Living Laboratory (UMDL2)</h1>
      </header>
      
      <div className="main-content">
        <div className="left-panel">
          <SchemaSelector 
            selectedSchema={selectedSchema}
            onSchemaSelect={setSelectedSchema}
            onAddCustomSchema={() => setShowCustomDialog(true)}
          />
          
          <div className="map-section">
            <MapView 
              locations={locations} 
              onLocationSelect={handleLocationSelect}
              selectedLocation={selectedLocation}
            />
          </div>
        </div>
        
        {selectedLocation && (
          <div className="details-section">
            <div className="location-header">
              <h2>{selectedLocation.name}</h2>
              {selectedSchema && (
                <div className="selected-schema-badge">
                  <span className="schema-label">Schema:</span>
                  <span className="schema-name">{selectedSchema.name}</span>
                </div>
              )}
            </div>
            
            <div className="video-section">
              <VideoPlayerEnhanced
                videoPath={selectedLocation.videoPath}
                locationId={selectedLocation.name}
                onTimeUpdate={handleTimeUpdate}
                onDetections={handleDetections}
              />
            </div>
            
            <div className="chart-section">
              <TrafficChart
                locationId={selectedLocation.id}
                currentTime={currentTime}
                detections={currentDetections}
                detectionService={detectionServiceRef.current}
              />
            </div>
            
            <div className="export-section">
              <h3>Export Data</h3>
              <select 
                onChange={(e) => handleExportCSV(e.target.value)}
                defaultValue=""
              >
                <option value="" disabled>Select aggregation level</option>
                <option value="15s">15 seconds</option>
                <option value="30s">30 seconds</option>
                <option value="5min">5 minutes</option>
                <option value="15min">15 minutes</option>
              </select>
            </div>
          </div>
        )}
      </div>
      
      <CustomSchemaDialog
        isOpen={showCustomDialog}
        onClose={() => setShowCustomDialog(false)}
        onSave={handleAddCustomSchema}
      />
    </div>
  );
}

export default App;
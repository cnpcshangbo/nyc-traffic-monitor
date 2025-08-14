import { useState, useRef, useEffect } from 'react';
import MapView from './components/MapView';
import VideoPlayerEnhanced from './components/VideoPlayerEnhanced';
import TrafficChart from './components/TrafficChart';
import SchemaSelector from './components/SchemaSelector';
import CustomSchemaDialog from './components/CustomSchemaDialog';
import VideoUploader from './components/VideoUploader';
import ProcessingProgress from './components/ProcessingProgress';
import { Detection, ObjectDetectionService } from './services/objectDetection';
import { ClassificationSchema, predefinedSchemas } from './config/schemas';
import { getApiBaseUrl } from './config/api';
import './App.css';

interface Location {
  id: string;
  name: string;
  coordinates: [number, number];
  videoPath: string;
}

// Default location coordinates (will be fetched from backend)
const defaultCoordinates: { [key: string]: [number, number] } = {
  '74th-Amsterdam-Columbus': [40.5761, -74.1412],
  'Amsterdam-80th': [40.5338, -74.2369],
  'Columbus-86th': [40.9030, -73.8500]
};

function App() {
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [currentDetections, setCurrentDetections] = useState<Detection[]>([]);
  const [selectedSchema, setSelectedSchema] = useState<ClassificationSchema | null>(predefinedSchemas[0]);
  const [customSchemas, setCustomSchemas] = useState<ClassificationSchema[]>([]);
  const [showCustomDialog, setShowCustomDialog] = useState(false);
  const [uploadedLocations, setUploadedLocations] = useState<Location[]>([]);
  const [allLocations, setAllLocations] = useState<Location[]>([]);
  const [isLoadingLocations, setIsLoadingLocations] = useState(true);
  const detectionServiceRef = useRef(new ObjectDetectionService());

  // Fetch locations from backend on component mount
  useEffect(() => {
    const fetchLocations = async () => {
      try {
        const response = await fetch(`${getApiBaseUrl()}/locations`);
        if (response.ok) {
          const data = await response.json();
          const backendLocations: Location[] = data.locations.map((loc: any) => ({
            id: loc.id,
            name: loc.name,
            coordinates: defaultCoordinates[loc.id] || [40.7831, -73.9778], // Default NYC coordinates
            videoPath: loc.original_video_url ? `${getApiBaseUrl()}${loc.original_video_url}` : ''
          }));
          setAllLocations(backendLocations);
        } else {
          console.error('Failed to fetch locations from backend');
          // Fall back to empty array if backend is not available
          setAllLocations([]);
        }
      } catch (error) {
        console.error('Error fetching locations:', error);
        setAllLocations([]);
      } finally {
        setIsLoadingLocations(false);
      }
    };

    fetchLocations();
  }, []);

  const handleLocationSelect = (location: Location) => {
    setSelectedLocation(location);
    setCurrentTime(0);
    detectionServiceRef.current.clearHistory();
    
    // Auto-scroll to video section after a short delay to allow state update
    setTimeout(() => {
      const videoSection = document.querySelector('.details-section');
      if (videoSection) {
        videoSection.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'start',
          inline: 'nearest'
        });
      }
    }, 150); // Slightly increased delay for layout changes
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

  const handleStartProcessing = (locationId: string) => {
    console.log(`Starting YOLOv8 processing for location: ${locationId}`);
    // This would trigger the backend processing
    // For now, just log the action
    // In a real implementation, you'd call:
    // fetch('/api/process', { method: 'POST', body: JSON.stringify({ locationId }) })
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
          
          <VideoUploader onVideoUpload={handleVideoUpload} />
          
          <ProcessingProgress 
            onStartProcessing={handleStartProcessing}
            availableLocations={allLocations.map(loc => ({ id: loc.id, name: loc.name }))}
          />
          
          <div className="map-section">
            {isLoadingLocations ? (
              <div style={{ padding: '20px', textAlign: 'center' }}>
                <p>Loading locations...</p>
              </div>
            ) : (
              <MapView 
                locations={allLocations} 
                onLocationSelect={handleLocationSelect}
                selectedLocation={selectedLocation}
              />
            )}
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
                locationId={selectedLocation.id}
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
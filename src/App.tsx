import { useState, useRef, useEffect } from 'react';
import MapView from './components/MapView';
import VideoPlayerEnhanced from './components/VideoPlayerEnhanced';
import TrafficChart from './components/TrafficChart';
import TrafficVolumeChart from './components/TrafficVolumeChart';
import LiveTrafficChart from './components/LiveTrafficChart';
import SchemaSelector from './components/SchemaSelector';
import CustomSchemaDialog from './components/CustomSchemaDialog';
import VideoUploader from './components/VideoUploader';
import ProcessingProgress from './components/ProcessingProgress';
import { Detection, ObjectDetectionService } from './services/objectDetection';
import { ClassificationSchema, predefinedSchemas } from './config/schemas';
import { cdnService, Location } from './services/cdnService';
import labLogo from './assets/lab_logo.png';
import './App.css';

interface AppLocation {
  id: string;
  name: string;
  coordinates: [number, number];
  videoPath: string;
}

function App() {
  const [selectedLocation, setSelectedLocation] = useState<AppLocation | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [currentDetections, setCurrentDetections] = useState<Detection[]>([]);
  const [selectedSchema, setSelectedSchema] = useState<ClassificationSchema | null>(predefinedSchemas[0]);
  const [customSchemas, setCustomSchemas] = useState<ClassificationSchema[]>([]);
  const [showCustomDialog, setShowCustomDialog] = useState(false);
  const [uploadedLocations, setUploadedLocations] = useState<AppLocation[]>([]);
  const [allLocations, setAllLocations] = useState<AppLocation[]>([]);
  const [isLoadingLocations, setIsLoadingLocations] = useState(true);
  const detectionServiceRef = useRef(new ObjectDetectionService());

  // Fetch locations from CDN on component mount
  useEffect(() => {
    const fetchLocations = async () => {
      try {
        const locations: Location[] = await cdnService.fetchLocations();
        
        // Convert to app format and get video URLs
        const appLocations: AppLocation[] = await Promise.all(
          locations.map(async (loc) => {
            const videoPath = await cdnService.getBestVideoUrl(loc);
            
            return {
              id: loc.id,
              name: loc.name,
              coordinates: loc.coordinates || [40.7831, -73.9778],
              videoPath: videoPath || '' // Ensure it's always a string, never undefined
            };
          })
        );
        
        setAllLocations(appLocations);
      } catch (error) {
        console.error('Error fetching locations:', error);
        setAllLocations([]);
      } finally {
        setIsLoadingLocations(false);
      }
    };

    fetchLocations();
  }, []);

  const handleLocationSelect = (location: AppLocation) => {
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
    }, 150);
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
      a.download = `traffic_data_${selectedLocation?.id || 'unknown'}_${selectedSchema?.id || 'default'}_${aggregationLevel}.csv`;
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
    const newLocation: AppLocation = {
      id: `uploaded-${Date.now()}`,
      name: customLocation,
      coordinates: [40.7831, -73.9778], // Default coordinates
      videoPath: videoUrl
    };
    
    setUploadedLocations([...uploadedLocations, newLocation]);
    setSelectedLocation(newLocation);
  };

  const combinedLocations = [...allLocations, ...uploadedLocations];

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <img src={labLogo} alt="Lab Logo" className="lab-logo" />
          <div className="header-text">
            <h1>Urban Mobility Data Living Laboratory (UMDL2)</h1>
            <p className="subtitle">AI & Mobility Research Lab at CUNY City College of New York</p>
          </div>
        </div>
      </header>

      <main className="app-main">
        {/* Map Section */}
        <section className="map-section">
          <div className="section-content">
            <MapView 
              locations={combinedLocations}
              selectedLocation={selectedLocation}
              onLocationSelect={handleLocationSelect}
              isLoading={isLoadingLocations}
            />
          </div>
        </section>

        {/* Video Upload Section */}
        <section className="upload-section">
          <div className="section-content">
            <VideoUploader onVideoUpload={handleVideoUpload} />
          </div>
        </section>

        {/* Video and Analysis Section */}
        {selectedLocation && (
          <section className="details-section">
            <div className="section-content">
              <h2>{selectedLocation.name}</h2>
              
              {/* Schema Selector */}
              <div className="controls-section">
                <SchemaSelector
                  schemas={[...predefinedSchemas, ...customSchemas]}
                  selectedSchema={selectedSchema}
                  onSchemaChange={setSelectedSchema}
                  onCustomSchemaClick={() => setShowCustomDialog(true)}
                />
              </div>

              <div className="details-grid">
                <div className="video-container">
                  {selectedLocation.videoPath && selectedLocation.videoPath.trim() !== '' ? (
                    <VideoPlayerEnhanced
                      videoPath={selectedLocation.videoPath}
                      locationId={selectedLocation.id}
                      onTimeUpdate={handleTimeUpdate}
                      onDetections={handleDetections}
                    />
                  ) : (
                    <div className="no-video-message">
                      <p>🎥 Video not available</p>
                      <p className="help-text">
                        Videos are available when running locally or on non-GitHub Pages deployments
                      </p>
                    </div>
                  )}
                  
                  {/* Processing Progress for server-processed videos */}
                  <ProcessingProgress locationId={selectedLocation.id} />
                </div>

                <div className="charts-container">
                  {/* Current detections and export controls */}
                  <div className="detection-summary">
                    <h3>Current Detections: {currentDetections.length}</h3>
                    <div className="export-controls">
                      <label>Export Level:</label>
                      {['15s', '30s', '5min', '15min'].map(level => (
                        <button
                          key={level}
                          className="export-btn"
                          onClick={() => handleExportCSV(level)}
                        >
                          {level}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Real-time traffic chart */}
                  <TrafficChart
                    detections={currentDetections}
                    currentTime={currentTime}
                    schema={selectedSchema}
                  />

                  {/* Volume chart for processed videos */}
                  <TrafficVolumeChart locationId={selectedLocation.id} />

                  {/* Live traffic distribution chart */}
                  <LiveTrafficChart locationId={selectedLocation.id} />
                </div>
              </div>
            </div>
          </section>
        )}
      </main>

      {/* Custom Schema Dialog */}
      {showCustomDialog && (
        <CustomSchemaDialog
          onSave={handleAddCustomSchema}
          onCancel={() => setShowCustomDialog(false)}
        />
      )}
    </div>
  );
}

export default App;
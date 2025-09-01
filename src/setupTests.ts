import '@testing-library/jest-dom';

// Mock Leaflet to prevent errors in JSDOM environment
// This is a basic mock; more complex interactions might need a more detailed mock
vi.mock('leaflet', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    Map: vi.fn(() => ({
      setView: vi.fn(),
      remove: vi.fn(),
      on: vi.fn(),
      off: vi.fn(),
    })),
    tileLayer: vi.fn(() => ({
      addTo: vi.fn(),
    })),
    marker: vi.fn(() => ({
      addTo: vi.fn(),
    })),
    icon: vi.fn(() => ({})),
    // Mock the global L object and its properties
    L: {
      ...actual.L,
      Icon: {
        Default: {
          prototype: {
            _getIconUrl: vi.fn(),
            mergeOptions: vi.fn(),
          },
        },
      },
    },
  };
});

// Mock react-leaflet components
const MockMapContainer = ({ children }) => `<div>${children}</div>`;
const MockTileLayer = () => null;
const MockMarker = () => null;
const MockPopup = () => null;

vi.mock('react-leaflet', () => ({
  MapContainer: MockMapContainer,
  TileLayer: MockTileLayer,
  Marker: MockMarker,
  Popup: MockPopup,
}));

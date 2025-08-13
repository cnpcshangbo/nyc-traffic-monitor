export interface ClassificationSchema {
  id: string;
  name: string;
  description: string;
  categories: SchemaCategory[];
  isCustom?: boolean;
}

export interface SchemaCategory {
  id: string;
  name: string;
  color: string;
  icon?: string;
}

export const predefinedSchemas: ClassificationSchema[] = [
  {
    id: 'mta',
    name: 'MTA',
    description: 'Metropolitan Transportation Authority Classification',
    categories: [
      { id: 'bus', name: 'Bus', color: '#3B82F6' },
      { id: 'subway_vehicle', name: 'Subway Service Vehicle', color: '#8B5CF6' },
      { id: 'passenger_car', name: 'Passenger Car', color: '#10B981' },
      { id: 'taxi', name: 'Taxi/For-Hire', color: '#F59E0B' },
      { id: 'truck', name: 'Truck', color: '#EF4444' },
      { id: 'motorcycle', name: 'Motorcycle', color: '#06B6D4' },
      { id: 'bicycle', name: 'Bicycle', color: '#84CC16' },
      { id: 'pedestrian', name: 'Pedestrian', color: '#EC4899' },
    ]
  },
  {
    id: 'fhwa',
    name: 'FHWA Axle-based (PANYNJ)',
    description: 'Federal Highway Administration / Port Authority Classification',
    categories: [
      { id: 'class1', name: 'Class 1: Motorcycles', color: '#06B6D4' },
      { id: 'class2', name: 'Class 2: Passenger Cars', color: '#10B981' },
      { id: 'class3', name: 'Class 3: Light Trucks (2 Axles, 4 Tires)', color: '#84CC16' },
      { id: 'class4', name: 'Class 4: Buses', color: '#3B82F6' },
      { id: 'class5', name: 'Class 5: Single Unit Trucks (2 Axles, 6 Tires)', color: '#F59E0B' },
      { id: 'class6', name: 'Class 6: Single Unit Trucks (3 Axles)', color: '#FB923C' },
      { id: 'class7', name: 'Class 7: Single Unit Trucks (4+ Axles)', color: '#F87171' },
      { id: 'class8', name: 'Class 8: Single Trailer Trucks (3-4 Axles)', color: '#EF4444' },
      { id: 'class9', name: 'Class 9: Single Trailer Trucks (5 Axles)', color: '#DC2626' },
      { id: 'class10', name: 'Class 10: Single Trailer Trucks (6+ Axles)', color: '#B91C1C' },
      { id: 'class11', name: 'Class 11: Multi-Trailer Trucks (5-6 Axles)', color: '#991B1B' },
      { id: 'class12', name: 'Class 12: Multi-Trailer Trucks (6+ Axles)', color: '#7F1D1D' },
      { id: 'class13', name: 'Class 13: Multi-Trailer Trucks (7+ Axles)', color: '#450A0A' },
    ]
  },
  {
    id: 'gvwr',
    name: 'GVWR',
    description: 'Gross Vehicle Weight Rating Classification',
    categories: [
      { id: 'class1', name: 'Class 1: ≤ 6,000 lbs', color: '#DBEAFE' },
      { id: 'class2a', name: 'Class 2a: 6,001-8,500 lbs', color: '#BFDBFE' },
      { id: 'class2b', name: 'Class 2b: 8,501-10,000 lbs', color: '#93C5FD' },
      { id: 'class3', name: 'Class 3: 10,001-14,000 lbs', color: '#60A5FA' },
      { id: 'class4', name: 'Class 4: 14,001-16,000 lbs', color: '#3B82F6' },
      { id: 'class5', name: 'Class 5: 16,001-19,500 lbs', color: '#2563EB' },
      { id: 'class6', name: 'Class 6: 19,501-26,000 lbs', color: '#1D4ED8' },
      { id: 'class7', name: 'Class 7: 26,001-33,000 lbs', color: '#1E40AF' },
      { id: 'class8', name: 'Class 8: > 33,000 lbs', color: '#1E3A8A' },
    ]
  }
];

export const getSchemaById = (id: string): ClassificationSchema | undefined => {
  return predefinedSchemas.find(schema => schema.id === id);
};
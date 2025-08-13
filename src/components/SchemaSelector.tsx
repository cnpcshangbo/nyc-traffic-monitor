import React from 'react';
import { ClassificationSchema, predefinedSchemas } from '../config/schemas';

interface SchemaSelectorProps {
  selectedSchema: ClassificationSchema | null;
  onSchemaSelect: (schema: ClassificationSchema) => void;
  onAddCustomSchema: () => void;
}

const SchemaSelector: React.FC<SchemaSelectorProps> = ({
  selectedSchema,
  onSchemaSelect,
  onAddCustomSchema
}) => {

  return (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      padding: '20px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      marginBottom: '20px'
    }}>
      <h2 style={{
        margin: '0 0 15px 0',
        fontSize: '18px',
        fontWeight: '600',
        color: '#1f2937'
      }}>
        Classification Schema
      </h2>
      
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '12px'
      }}>
        {predefinedSchemas.map(schema => (
          <button
            key={schema.id}
            onClick={() => onSchemaSelect(schema)}
            style={{
              padding: '16px',
              border: selectedSchema?.id === schema.id 
                ? '2px solid #3B82F6' 
                : '2px solid #E5E7EB',
              borderRadius: '8px',
              background: selectedSchema?.id === schema.id 
                ? '#EFF6FF' 
                : 'white',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'all 0.2s',
              position: 'relative'
            }}
            onMouseEnter={(e) => {
              if (selectedSchema?.id !== schema.id) {
                e.currentTarget.style.borderColor = '#93C5FD';
                e.currentTarget.style.background = '#F9FAFB';
              }
            }}
            onMouseLeave={(e) => {
              if (selectedSchema?.id !== schema.id) {
                e.currentTarget.style.borderColor = '#E5E7EB';
                e.currentTarget.style.background = 'white';
              }
            }}
          >
            {selectedSchema?.id === schema.id && (
              <div style={{
                position: 'absolute',
                top: '8px',
                right: '8px',
                width: '20px',
                height: '20px',
                borderRadius: '50%',
                background: '#3B82F6',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                  <path d="M2 6L5 9L10 3" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
            )}
            
            <div style={{
              fontSize: '16px',
              fontWeight: '600',
              color: '#1f2937',
              marginBottom: '4px'
            }}>
              {schema.name}
            </div>
            
            <div style={{
              fontSize: '13px',
              color: '#6B7280',
              lineHeight: '1.4'
            }}>
              {schema.description}
            </div>
            
            <div style={{
              marginTop: '8px',
              fontSize: '12px',
              color: '#9CA3AF'
            }}>
              {schema.categories.length} categories
            </div>
          </button>
        ))}
        
        <button
          onClick={onAddCustomSchema}
          style={{
            padding: '16px',
            border: '2px dashed #D1D5DB',
            borderRadius: '8px',
            background: 'white',
            cursor: 'pointer',
            textAlign: 'center',
            transition: 'all 0.2s',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = '#93C5FD';
            e.currentTarget.style.background = '#F9FAFB';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = '#D1D5DB';
            e.currentTarget.style.background = 'white';
          }}
        >
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <rect x="1" y="1" width="30" height="30" rx="7" stroke="#9CA3AF" strokeWidth="2" strokeDasharray="4 4"/>
            <path d="M16 10V22M10 16H22" stroke="#9CA3AF" strokeWidth="2" strokeLinecap="round"/>
          </svg>
          
          <div style={{
            fontSize: '16px',
            fontWeight: '600',
            color: '#6B7280'
          }}>
            Add Custom Schema
          </div>
          
          <div style={{
            fontSize: '13px',
            color: '#9CA3AF'
          }}>
            Create your own classification
          </div>
        </button>
      </div>
      
      {selectedSchema && (
        <div style={{
          marginTop: '20px',
          padding: '16px',
          background: '#F9FAFB',
          borderRadius: '8px',
          border: '1px solid #E5E7EB'
        }}>
          <div style={{
            fontSize: '14px',
            fontWeight: '600',
            color: '#4B5563',
            marginBottom: '12px'
          }}>
            Categories in {selectedSchema.name}:
          </div>
          
          <div style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '8px'
          }}>
            {selectedSchema.categories.map(category => (
              <div
                key={category.id}
                style={{
                  padding: '6px 12px',
                  borderRadius: '6px',
                  background: category.color + '20',
                  border: `1px solid ${category.color}40`,
                  fontSize: '13px',
                  color: '#1f2937',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                <div
                  style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    background: category.color
                  }}
                />
                {category.name}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SchemaSelector;
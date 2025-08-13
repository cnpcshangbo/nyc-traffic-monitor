import React, { useState } from 'react';
import { ClassificationSchema, SchemaCategory } from '../config/schemas';

interface CustomSchemaDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (schema: ClassificationSchema) => void;
}

const CustomSchemaDialog: React.FC<CustomSchemaDialogProps> = ({
  isOpen,
  onClose,
  onSave
}) => {
  const [schemaName, setSchemaName] = useState('');
  const [schemaDescription, setSchemaDescription] = useState('');
  const [categories, setCategories] = useState<SchemaCategory[]>([
    { id: '1', name: '', color: '#3B82F6' }
  ]);

  const predefinedColors = [
    '#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6',
    '#EC4899', '#06B6D4', '#84CC16', '#F97316', '#6366F1'
  ];

  const addCategory = () => {
    const newId = (categories.length + 1).toString();
    setCategories([...categories, { 
      id: newId, 
      name: '', 
      color: predefinedColors[categories.length % predefinedColors.length] 
    }]);
  };

  const updateCategory = (index: number, field: keyof SchemaCategory, value: string) => {
    const updated = [...categories];
    updated[index] = { ...updated[index], [field]: value };
    setCategories(updated);
  };

  const removeCategory = (index: number) => {
    setCategories(categories.filter((_, i) => i !== index));
  };

  const handleSave = () => {
    if (!schemaName || categories.some(c => !c.name)) {
      alert('Please fill in all required fields');
      return;
    }

    const newSchema: ClassificationSchema = {
      id: `custom_${Date.now()}`,
      name: schemaName,
      description: schemaDescription,
      categories: categories.map((c, i) => ({
        ...c,
        id: `cat_${i}`
      })),
      isCustom: true
    };

    onSave(newSchema);
    handleClose();
  };

  const handleClose = () => {
    setSchemaName('');
    setSchemaDescription('');
    setCategories([{ id: '1', name: '', color: '#3B82F6' }]);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div style={{
        background: 'white',
        borderRadius: '12px',
        padding: '24px',
        maxWidth: '600px',
        width: '90%',
        maxHeight: '80vh',
        overflow: 'auto',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '20px'
        }}>
          <h2 style={{
            margin: 0,
            fontSize: '20px',
            fontWeight: '600',
            color: '#1f2937'
          }}>
            Create Custom Classification Schema
          </h2>
          
          <button
            onClick={handleClose}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '4px'
            }}
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M6 6L18 18M6 18L18 6" stroke="#6B7280" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </button>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{
            display: 'block',
            marginBottom: '6px',
            fontSize: '14px',
            fontWeight: '500',
            color: '#374151'
          }}>
            Schema Name *
          </label>
          <input
            type="text"
            value={schemaName}
            onChange={(e) => setSchemaName(e.target.value)}
            placeholder="e.g., Custom Traffic Classification"
            style={{
              width: '100%',
              padding: '10px 12px',
              border: '1px solid #D1D5DB',
              borderRadius: '6px',
              fontSize: '14px',
              outline: 'none'
            }}
          />
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{
            display: 'block',
            marginBottom: '6px',
            fontSize: '14px',
            fontWeight: '500',
            color: '#374151'
          }}>
            Description
          </label>
          <textarea
            value={schemaDescription}
            onChange={(e) => setSchemaDescription(e.target.value)}
            placeholder="Describe your classification schema..."
            rows={3}
            style={{
              width: '100%',
              padding: '10px 12px',
              border: '1px solid #D1D5DB',
              borderRadius: '6px',
              fontSize: '14px',
              outline: 'none',
              resize: 'vertical'
            }}
          />
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{
            display: 'block',
            marginBottom: '12px',
            fontSize: '14px',
            fontWeight: '500',
            color: '#374151'
          }}>
            Categories *
          </label>
          
          {categories.map((category, index) => (
            <div key={index} style={{
              display: 'flex',
              gap: '8px',
              marginBottom: '8px',
              alignItems: 'center'
            }}>
              <input
                type="text"
                value={category.name}
                onChange={(e) => updateCategory(index, 'name', e.target.value)}
                placeholder="Category name"
                style={{
                  flex: 1,
                  padding: '8px 12px',
                  border: '1px solid #D1D5DB',
                  borderRadius: '6px',
                  fontSize: '14px',
                  outline: 'none'
                }}
              />
              
              <input
                type="color"
                value={category.color}
                onChange={(e) => updateCategory(index, 'color', e.target.value)}
                style={{
                  width: '50px',
                  height: '38px',
                  border: '1px solid #D1D5DB',
                  borderRadius: '6px',
                  cursor: 'pointer'
                }}
              />
              
              {categories.length > 1 && (
                <button
                  onClick={() => removeCategory(index)}
                  style={{
                    padding: '8px',
                    background: '#FEE2E2',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="#EF4444">
                    <path d="M4 4L12 12M4 12L12 4" stroke="#EF4444" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                </button>
              )}
            </div>
          ))}
          
          <button
            onClick={addCategory}
            style={{
              marginTop: '8px',
              padding: '8px 16px',
              background: '#EFF6FF',
              border: '1px solid #3B82F6',
              borderRadius: '6px',
              color: '#3B82F6',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M8 4V12M4 8H12" stroke="#3B82F6" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            Add Category
          </button>
        </div>

        <div style={{
          display: 'flex',
          gap: '12px',
          justifyContent: 'flex-end',
          paddingTop: '16px',
          borderTop: '1px solid #E5E7EB'
        }}>
          <button
            onClick={handleClose}
            style={{
              padding: '10px 20px',
              background: 'white',
              border: '1px solid #D1D5DB',
              borderRadius: '6px',
              color: '#374151',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer'
            }}
          >
            Cancel
          </button>
          
          <button
            onClick={handleSave}
            style={{
              padding: '10px 20px',
              background: '#3B82F6',
              border: 'none',
              borderRadius: '6px',
              color: 'white',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer'
            }}
          >
            Create Schema
          </button>
        </div>
      </div>
    </div>
  );
};

export default CustomSchemaDialog;
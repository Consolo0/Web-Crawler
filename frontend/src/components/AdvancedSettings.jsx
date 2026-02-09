import React, { useState } from 'react';

const AdvancedSettings = ({ restrictions, onChange }) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleChange = (category, field, value) => {
    const newRestrictions = { ...restrictions };
    
    if (!newRestrictions[category]) {
      newRestrictions[category] = {};
    }
    
    newRestrictions[category][field] = value;
    onChange(newRestrictions);
  };

  return (
    <div className="advanced-settings">
      <button
        type="button"
        className="toggle-button"
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? '▼' : '▶'} Advanced Settings
      </button>

      {isOpen && (
        <div className="settings-content">
          {/* Stop Criteria */}
          <div className="setting-group">
            <h3>Stop Criteria</h3>
            <div className="setting-item">
              <label htmlFor="maximum_errors">Maximum Errors:</label>
              <input
                id="maximum_errors"
                type="number"
                min="1"
                value={restrictions.stop_criteria?.maximum_errors || 5}
                onChange={(e) =>
                  handleChange('stop_criteria', 'maximum_errors', parseInt(e.target.value))
                }
              />
            </div>
          </div>

          {/* Navigation Strategy */}
          <div className="setting-group">
            <h3>Navigation Strategy</h3>
            
            <div className="setting-item">
              <label htmlFor="type">Strategy Type:</label>
              <select
                id="type"
                value={restrictions.navigation_strategy?.type || 'BFS'}
                onChange={(e) =>
                  handleChange('navigation_strategy', 'type', e.target.value)
                }
              >
                <option value="BFS">BFS (Breadth-First Search)</option>
                <option value="DFS">DFS (Depth-First Search)</option>
              </select>
            </div>

            <div className="setting-item">
              <label htmlFor="maximum_depth">Maximum Depth:</label>
              <input
                id="maximum_depth"
                type="number"
                min="1"
                value={restrictions.navigation_strategy?.maximum_depth || 5}
                onChange={(e) =>
                  handleChange('navigation_strategy', 'maximum_depth', parseInt(e.target.value))
                }
              />
            </div>

            <div className="setting-item">
              <label htmlFor="maximum_products_per_source">Max Products per Source:</label>
              <input
                id="maximum_products_per_source"
                type="number"
                min="1"
                value={restrictions.navigation_strategy?.maximum_products_per_source || 10}
                onChange={(e) =>
                  handleChange('navigation_strategy', 'maximum_products_per_source', parseInt(e.target.value))
                }
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdvancedSettings;
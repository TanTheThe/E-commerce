import React, { useState, useEffect } from 'react';
import { ChevronDown, ChevronRight, X } from 'lucide-react';

const HierarchicalCategorySelect = ({ 
  categories = [], 
  selectedCategoryIds = [], 
  onSelectionChange,
  label = "Chọn danh mục",
  placeholder = "Tất cả danh mục"
}) => {
  const [expandedParents, setExpandedParents] = useState(new Set());
  const [isOpen, setIsOpen] = useState(false);

  const organizeCategories = () => {
    const parentCategories = categories.filter(cat => !cat.parent_id);
    const childCategories = categories.filter(cat => cat.parent_id);
    
    return parentCategories.map(parent => ({
      ...parent,
      children: childCategories.filter(child => child.parent_id === parent.id)
    }));
  };

  const hierarchicalCategories = organizeCategories();

  const toggleParentExpansion = (parentId, e) => {
    e.stopPropagation();
    const newExpanded = new Set(expandedParents);
    if (newExpanded.has(parentId)) {
      newExpanded.delete(parentId);
    } else {
      newExpanded.add(parentId);
    }
    setExpandedParents(newExpanded);
  };

  const handleChildSelection = (childId, e) => {
    e.stopPropagation();
    let newSelected = [...selectedCategoryIds];
    if (newSelected.includes(childId)) {
      newSelected = newSelected.filter(id => id !== childId);
    } else {
      newSelected.push(childId);
    }
    onSelectionChange(newSelected);
  };

  const getSelectedCategoryNames = () => {
    return categories
      .filter(cat => selectedCategoryIds.includes(cat.id))
      .map(cat => cat.name);
  };

  const selectedNames = getSelectedCategoryNames();

  const getDisplayText = () => {
    if (selectedNames.length === 0) {
      return placeholder;
    }
    
    if (selectedNames.length <= 2) {
      return selectedNames.join(', ');
    }
    
    return `${selectedNames.slice(0, 2).join(', ')} và ${selectedNames.length - 2} mục khác`;
  };

  const removeCategory = (categoryId, e) => {
    e.stopPropagation();
    const newSelected = selectedCategoryIds.filter(id => id !== categoryId);
    onSelectionChange(newSelected);
  };

  return (
    <div className="relative w-full mb-5">
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {label}
      </label>

      <div
        className="relative border border-gray-300 rounded-md px-3 py-2 bg-white cursor-pointer hover:border-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center justify-between">
          <span className={`text-sm ${selectedNames.length === 0 ? 'text-gray-400' : 'text-gray-900'}`}>
            {getDisplayText()}
          </span>
          <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
        </div>
      </div>

      {isOpen && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-80 overflow-y-auto">
          {hierarchicalCategories.map((parent) => (
            <div key={parent.id}>
              <div
                className="flex items-center justify-between px-3 py-2 bg-gray-50 border-b border-gray-200 cursor-pointer hover:bg-gray-100 font-medium text-gray-800"
                onClick={(e) => toggleParentExpansion(parent.id, e)}
              >
                <span className="text-sm">{parent.name}</span>
                {expandedParents.has(parent.id) ? 
                  <ChevronDown className="w-4 h-4 text-gray-600" /> : 
                  <ChevronRight className="w-4 h-4 text-gray-600" />
                }
              </div>

              {expandedParents.has(parent.id) && (
                <div>
                  {parent.children.map((child) => (
                    <div
                      key={child.id}
                      className="flex items-center px-6 py-2 cursor-pointer hover:bg-blue-50 border-b border-gray-100"
                      onClick={(e) => handleChildSelection(child.id, e)}
                    >
                      <input
                        type="checkbox"
                        checked={selectedCategoryIds.includes(child.id)}
                        onChange={() => {}}
                        className="mr-3 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <span className="text-sm text-gray-700">{child.name}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
          
          {hierarchicalCategories.length === 0 && (
            <div className="px-3 py-4 text-center text-gray-500 text-sm">
              Không có danh mục nào
            </div>
          )}
        </div>
      )}

      {selectedNames.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-2">
          {selectedNames.map((name, index) => {
            const categoryId = categories.find(cat => cat.name === name)?.id;
            return (
              <div
                key={index}
                className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full"
              >
                <span>{name}</span>
                <button
                  onClick={(e) => removeCategory(categoryId, e)}
                  className="ml-1 hover:bg-blue-200 rounded-full p-0.5 transition-colors"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            );
          })}
        </div>
      )}

      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default HierarchicalCategorySelect;
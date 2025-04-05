import React, { useState } from 'react';
import styled from 'styled-components';
import { FaChevronDown, FaChevronUp } from 'react-icons/fa';

const SelectContainer = styled.div`
  width: 100%;
  max-width: 400px;
  margin: 1rem auto;
  position: relative;
`;

const SelectedOption = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background-color: var(--secondary-bg);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  cursor: pointer;
  
  &:hover {
    background-color: var(--highlight-bg);
  }
`;

const DropdownList = styled.ul`
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin: 0.25rem 0 0;
  padding: 0;
  background-color: var(--secondary-bg);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  list-style: none;
  max-height: 300px;
  overflow-y: auto;
  z-index: 10;
`;

const DropdownItem = styled.li`
  padding: 0.75rem 1rem;
  cursor: pointer;
  
  &:hover {
    background-color: var(--highlight-bg);
  }
  
  ${props => props.selected && `
    background-color: var(--primary-color);
    color: white;
    
    &:hover {
      background-color: var(--primary-color);
    }
  `}
`;

const Label = styled.div`
  margin-bottom: 0.5rem;
  font-weight: 500;
`;

function ModelSelector({ models, selectedModel, onSelect }) {
  const [isOpen, setIsOpen] = useState(false);
  
  const toggleDropdown = () => {
    setIsOpen(!isOpen);
  };
  
  const handleSelect = (model) => {
    onSelect(model);
    setIsOpen(false);
  };
  
  return (
    <SelectContainer>
      <Label>Select a model:</Label>
      <SelectedOption onClick={toggleDropdown}>
        <span>{selectedModel || 'Select a model'}</span>
        {isOpen ? <FaChevronUp /> : <FaChevronDown />}
      </SelectedOption>
      
      {isOpen && (
        <DropdownList>
          {models.map((model) => (
            <DropdownItem
              key={model}
              selected={model === selectedModel}
              onClick={() => handleSelect(model)}
            >
              {model}
            </DropdownItem>
          ))}
        </DropdownList>
      )}
    </SelectContainer>
  );
}

export default ModelSelector; 
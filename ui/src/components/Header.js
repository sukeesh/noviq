import React from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';
import { FaSync, FaStar, FaExternalLinkAlt } from 'react-icons/fa';

const HeaderContainer = styled.header`
  display: flex;
  align-items: center;
  background-color: var(--secondary-bg);
  border-bottom: 1px solid var(--border-color);
  padding: 0.5rem 1rem;
  height: 48px;
`;

const Logo = styled(Link)`
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-light);
  text-decoration: none;
  margin-right: 1rem;
  
  &:hover {
    text-decoration: none;
  }
`;

const URLBar = styled.div`
  flex: 1;
  background-color: var(--highlight-bg);
  border-radius: 4px;
  display: flex;
  align-items: center;
  padding: 0.4rem 0.8rem;
  font-size: 0.9rem;
  color: var(--text-secondary);
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
`;

const ActionButton = styled.button`
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 1rem;
  cursor: pointer;
  margin-left: 1rem;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  
  &:hover {
    color: var(--text-light);
    background-color: var(--highlight-bg);
  }
`;

function Header() {
  return (
    <HeaderContainer>
      <Logo to="/">Noviq</Logo>
      <URLBar>noviq.research/session</URLBar>
      <ActionButton title="Refresh">
        <FaSync />
      </ActionButton>
      <ActionButton title="Bookmark">
        <FaStar />
      </ActionButton>
      <ActionButton title="Open in new window">
        <FaExternalLinkAlt />
      </ActionButton>
    </HeaderContainer>
  );
}

export default Header; 
// Sidebar.js
import React, { useState } from 'react';
import { Sidebar as ProSidebar, Menu, MenuItem } from 'react-pro-sidebar';
import { Home } from '@mui/icons-material';

const Sidebar = () => {
  const [collapsed, setCollapsed] = useState(false);

  const handleToggleSidebar = () => {
    setCollapsed(!collapsed);
  };

  return (
    <div>
    <p>hello goose</p>
    </div>
  );
};

export default Sidebar;

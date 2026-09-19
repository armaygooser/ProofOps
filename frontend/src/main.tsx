import React from 'react';
import ReactDOM from 'react-dom/client';
import { App as AntApp, ConfigProvider, theme } from 'antd';
import { ProofOpsApp } from './App';
import './styles/global.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorPrimary: '#20d9ff',
          colorInfo: '#20d9ff',
          colorSuccess: '#2ee6a6',
          colorWarning: '#ffba43',
          colorError: '#ff6b57',
          colorBgBase: '#061423',
          borderRadius: 8,
          fontFamily: 'Inter, "Microsoft YaHei", system-ui, sans-serif',
        },
      }}
    >
      <AntApp>
        <ProofOpsApp />
      </AntApp>
    </ConfigProvider>
  </React.StrictMode>,
);

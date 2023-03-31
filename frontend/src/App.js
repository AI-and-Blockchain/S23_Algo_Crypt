import './App.css';
import axios from 'axios';
import  'bootstrap/dist/css/bootstrap.min.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Auth from './Auth';
import React, {useState, useEffect} from 'react';


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/auth" element={<Auth />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App;
import React from 'react'
import {BrowserRouter, Routes, Route, Navigate} from "react-router-dom"
import Login from './pages/login'
import Register from "./pages/Register"
import Home from "./pages/Home"
import NotFound from "./pages/NotFound"
import ProtectedRoute from "./components/ProtectedRoute"
import CampusMap from './pages/CampusMap'
import CreateEvent from './pages/CreateEvent'
import EventView from './pages/EventView'
import { Events } from 'leaflet'

function Logout() {
  localStorage.clear()
  return <Navigate to="/login" /> 
}

function RegisterAndLogout() {
  React.useEffect(() => {
    localStorage.clear();
  }, []);

  return <Register />;
}




function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Protected routes */}
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<Home />} />
          <Route path="/logout" element={<Logout />} />
        </Route>

        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<RegisterAndLogout />} />
        <Route path="/map" element={<CampusMap />} />
        <Route path='/create-event' element={<CreateEvent/>}/>
        <Route path='/events' element={<EventView/>}/>

        {/* Catch-all */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}
export default App

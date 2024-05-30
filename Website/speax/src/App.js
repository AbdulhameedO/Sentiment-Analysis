import logo from './logo.svg';
import './App.css';
import Homepage from './Components/Homepage/Homepage';
import NavBar from './Components/NavBar/NavBar';
import { Component } from 'react';
import Profile from './Components/Profile/Profile';
import Files from './Components/My_files/Files';
import {Route,Routes} from "react-router-dom"
import Login from './Components/Login/Login';
function App() {

  return (
    <div className='ancestor'> 
      <NavBar/> 
    <div className='container'>
      <Routes>
        <Route path="/" element={<Homepage/>}/>
        <Route path="/profile" element={<Profile/>}/>
        <Route path="/files" element={<Files/>}/>
        <Route path="/login" element={<Login/>}/>
      </Routes>      
     </div> 
     </div>
    
  )

}
export default App;

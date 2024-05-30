import React from 'react'
import { useState } from 'react'
import './Homepage.css'
import AudioPlay from '../AudioPlayer/audioPl'
import ProgressBar from '../player/Barpl'
const Homepage = () => {
  const [inputText, setInputText] = useState('');
  const handleInputChange = (event) => {
    setInputText(event.target.value);
  };
  const handleSubmit = (event) => {
    event.preventDefault();
    alert(`Input value submitted: ${inputText}`);
  };

  return (
    <div className='body'>
    <div className='Imgdiv'>
    <img src="/Logo.png" alt="Logo" />
   
    </div>
    <div className='Formdiv'>
       <form onSubmit={handleSubmit} >
        <textarea
          type="text"
          value={inputText}
          onChange={handleInputChange}
          placeholder="Type something..."
          className='largeText'
        />
        <ProgressBar/>
        <div className='btns'>
        <button type="submit" >Repeat</button>
        <button type="submit" className='subBtn'>Play</button>
        <button type="submit" className='subBtn'>Upload</button>
        </div>
       
      </form>
    </div>
    </div>
  )
}

export default Homepage

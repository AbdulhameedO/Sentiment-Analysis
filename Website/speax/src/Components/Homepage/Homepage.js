import React from 'react'
import { useState } from 'react'
import './Homepage.css'
import AudioPlay from '../AudioPlayer/audioPl'
import ProgressBar from '../player/Barpl'
import { getAudio } from '../../Apiservice'
import axios from 'axios';
const Homepage = () => {
  const [inputText, setInputText] = useState('');
  const handleInputChange = (event) => {
    setInputText(event.target.value);
  };
  const handleSubmit = (event) => {
    event.preventDefault();
    alert(`Input value submitted: ${inputText}`);
  };
  const handleGetAudio = async () => {
    try {
        const response = await getAudio();
        console.log(response.data);
    } catch (error) {
        console.error(error);
    }
};

const posttts = async () => {
  const temp= "yarab fok eldeka"

  try{
    const response=await axios.post(`http://localhost:8000/audio/tts?text=${temp}`)
    console.log(response.data)
  }
  catch (error) {
    console.error(error);
  }
}

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
        <button  onClick={posttts} className='subBtn'>Play</button>
        <button type="submit" className='subBtn'>Upload</button>
        </div>
       
      </form>
    </div>
    </div>
  )
}

export default Homepage

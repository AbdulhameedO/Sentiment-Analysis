import React from 'react'
import "./Barpl.css"
const ProgressBar = () => {
  return (
    <body>
    <div className='wrapper'>
        <div className='bookDetails'>
            <p className='name'>Alice in wonderland</p>

        </div>
        <div className='progressArea'>
            <div className='progress-bar'>
            </div>
            <div className='timer'>
                <span className='current'>0:20</span>
                <span className='current'>2:40</span>
            </div>
        </div>
      
    </div>
    </body>
  )
} 

export default ProgressBar

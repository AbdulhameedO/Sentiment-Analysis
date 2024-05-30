import React from 'react'
import "./Login.css"
import { useState } from 'react'
const Login = () => {
    const [show,setShow]=useState(true)
  
  return (
   
    <body>
        
        <div className='form-popup'>
             
            <div className='form-box login'>
                <div className='form-details'>

                </div>
                <div className='form-content'>
                    <h2>LOGIN</h2>
                    <form action='#'>
                        <div className='input-field'>
                            <input type="text" required></input>
                            <label>Email</label>
                        </div>
                        <div className='input-field'>
                            <input type="password" required></input>
                            <label>Password</label>
                        </div>
                        <a href='#' className='forgot-pass'>Forgot password</a>
                        <button type="submit" >Log In</button>
                    </form>
                    <div className='bottom-link'>
                        Don't have an account
                        <button >Sign up</button>
                    </div>
                </div>
            </div> 
            
            <div className='form-box signup'>
                <div className='form-details'>

                </div>
                <div className='form-content'>
                    <h2>SIGNUP</h2>
                    <form action='#'>
                        <div className='input-field'>
                            <input type="text" required></input>
                            <label>Enter your email</label>
                        </div>
                        <div className='input-field'>
                            <input type="password" required></input>
                            <label>Create a password</label>
                        </div>

                        <button type="submit">Sign Uح</button>
                    </form>
                    <div className='bottom-link'>
                        Already Have an account
                        <button >Log In</button>
                    </div>
                </div>
            </div>
            
        </div>
    </body>
  )
}

export default Login

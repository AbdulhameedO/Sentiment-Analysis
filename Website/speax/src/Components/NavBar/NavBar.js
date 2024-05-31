import React from 'react'
import "./NavBar.css"
import { Link } from 'react-router-dom'
const NavBar = () => {
  return (
   <nav className='fathernav'>
    <Link to="/" className="site-title">Speax</Link>
    <ul className="normalul">
      <CustomLink to="/profile">Profile</CustomLink>     
      <CustomLink to="/files">My Files</CustomLink> 
      <Link to="/login" className="loginbtn">Log in</Link>    
    </ul>
   
   </nav> 
  )
}

 function CustomLink ({to,children,...props}){
  const path = window.location.pathname
  return (
    <li className={path === to ? "active" : ""}>
      <Link to={to} {...props}>{children}</Link>
    </li>
  )
 }
export default NavBar

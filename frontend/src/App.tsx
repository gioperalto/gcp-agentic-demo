import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Header } from './components/Header'
import { Home } from './pages/Home'
import { Login } from './pages/Login'
import { Cards } from './pages/Cards'
import { Benefits } from './pages/Benefits'
import { Account } from './pages/Account'
import { Apply } from './pages/Apply'
import { Concierge } from './pages/Concierge'
import { Accommodations } from './pages/Accommodations'
import { Experiences } from './pages/Experiences'
import { Flights } from './pages/Flights'
import { Restaurants } from './pages/Restaurants'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <Header />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/cards" element={<Cards />} />
          <Route path="/benefits" element={<Benefits />} />
          <Route path="/account" element={<Account />} />
          <Route path="/apply" element={<Apply />} />
          <Route path="/concierge" element={<Concierge />} />
          <Route path="/accommodations" element={<Accommodations />} />
          <Route path="/experiences" element={<Experiences />} />
          <Route path="/flights" element={<Flights />} />
          <Route path="/restaurants" element={<Restaurants />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Header } from './components/Header'
import { Home } from './pages/Home'
import { Login } from './pages/Login'
import { Cards } from './pages/Cards'
import { Benefits } from './pages/Benefits'
import { Account } from './pages/Account'
import { Apply } from './pages/Apply'
import { Chat } from './components/Chat'
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
          <Route path="/chat" element={<Chat />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App

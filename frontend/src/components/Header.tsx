import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getCachedUser, logout } from '../utils/auth';
import './Header.css';

export const Header = () => {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [benefitsDropdownOpen, setBenefitsDropdownOpen] = useState(false);
  const user = getCachedUser();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    setDropdownOpen(false);
    navigate('/');
    window.location.reload(); // Refresh to update auth state
  };

  const handleLogin = () => { navigate('/login'); };

  return (
    <header className="header">
      <div className="header-container">
        <Link to="/" className="logo">
          Meridian
        </Link>

        <nav className="nav">
          <Link to="/" className="nav-link">Home</Link>
          <Link to="/cards" className="nav-link">Cards</Link>

          <div
            className="nav-dropdown"
            onMouseEnter={() => setBenefitsDropdownOpen(true)}
            onMouseLeave={() => setBenefitsDropdownOpen(false)}
          >
            <Link to="/benefits" className="nav-link">
              Benefits ▼
            </Link>

            {benefitsDropdownOpen && (
              <div className="nav-dropdown-menu">
                <Link
                  to="/benefits#travel-insurance"
                  className="nav-dropdown-item cursor-pointer"
                  onClick={() => setBenefitsDropdownOpen(false)}
                >
                  Travel Insurance
                </Link>
                <Link
                  to="/benefits#concierge"
                  className="nav-dropdown-item cursor-pointer"
                  onClick={() => setBenefitsDropdownOpen(false)}
                >
                  Concierge Services
                </Link>
                <Link
                  to="/benefits#lounge"
                  className="nav-dropdown-item cursor-pointer"
                  onClick={() => setBenefitsDropdownOpen(false)}
                >
                  Tribune Lounge
                </Link>
                <Link
                  to="/benefits#dining"
                  className="nav-dropdown-item cursor-pointer"
                  onClick={() => setBenefitsDropdownOpen(false)}
                >
                  Tribune Dining
                </Link>
                <Link
                  to="/benefits#jet-share"
                  className="nav-dropdown-item cursor-pointer"
                  onClick={() => setBenefitsDropdownOpen(false)}
                >
                  Tribune Private Jet
                </Link>
              </div>
            )}
          </div>
        </nav>

        <div className="user-menu">
          {user ? (
            <div className="dropdown">
              <button
                className="dropdown-toggle"
                onClick={() => setDropdownOpen(!dropdownOpen)}
              >
                {user.username} ▼
              </button>

              {dropdownOpen && (
                <div className="dropdown-menu">
                  <Link
                    to="/account"
                    className="dropdown-item"
                    onClick={() => setDropdownOpen(false)}
                  >
                    Profile
                  </Link>
                  <button
                    className="dropdown-item"
                    onClick={handleLogout}
                  >
                    Logout
                  </button>
                </div>
              )}
            </div>
          ) : (
            <button className="login-button" onClick={handleLogin}>
              Login
            </button>
          )}
        </div>
      </div>
    </header>
  );
};

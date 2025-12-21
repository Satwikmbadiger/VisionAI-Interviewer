import './Styles/App.css'
import { Routes, Route } from 'react-router-dom';
import Dashboard from './pages/UserDashBoard.jsx';
import RegisterationForm from './pages/RegisterationForm';
import Login from './pages/Login';
import Hero from './pages/Hero';
import InterViewSetupPage from "./pages/InterViewSetupPage.jsx";
import InterViewPage from "./pages/InterviewPage.jsx";
const App = () => {
   return (
      <>
         <Routes>
            <Route path='/' element={<Hero/>}/>
             <Route path='/users/:userId' element={<Dashboard/>}/>
            <Route path='/users/new' element={<RegisterationForm/>}/>
            <Route path='/users/login' element={<Login/>}/>
             <Route path='/Interview/:userId' element={<InterViewSetupPage/>}/>
             <Route path='/Interview/sessionId' element={<InterViewPage/>}/>
         </Routes>
      </>
   );
};


export default App

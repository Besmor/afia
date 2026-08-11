import { Route, Routes } from 'react-router-dom';
import { Landing } from './pages/Landing';
import { Results } from './pages/Results';
import { PharmacyDetail } from './pages/PharmacyDetail';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/results" element={<Results />} />
      <Route path="/pharmacy/:pharmacyId" element={<PharmacyDetail />} />
    </Routes>
  );
}

export default App;

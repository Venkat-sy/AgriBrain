import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import DigitalTwin from '../DigitalTwin.jsx';

// Mock the fetch API used within DigitalTwin
global.fetch = jest.fn();

const mockDistricts = [
  { id: 1, name: 'District A', state: 'State X' },
  { id: 2, name: 'District B', state: 'State Y' },
];

const mockCrops = [
  { id: 10, name: 'Wheat' },
  { id: 11, name: 'Rice' },
];

const mockSimulationResponse = {
  total_cost_inr: 50000,
  estimated_yield_tons: 12.34,
  market_value_inr: 75000,
  net_profit_inr: 25000,
  roi_percentage: 50,
  risk_level: 'low',
  cost_breakdown: [{ activity: 'Seeds', unit: 'kg', unit_cost: 100, quantity: 5, total_cost: 500 }],
};

beforeEach(() => {
  fetch.mockReset();
});

test('renders dropdowns with fetched data', async () => {
  // Mock the two initial fetch calls for districts and crops.
  fetch
    .mockResolvedValueOnce({ json: () => Promise.resolve(mockDistricts) })
    .mockResolvedValueOnce({ json: () => Promise.resolve(mockCrops) });

  render(<DigitalTwin />);

  // Wait for the component to finish loading the dropdown data.
  await waitFor(() => expect(fetch).toHaveBeenCalledTimes(2));

  // Verify that at least one district and one crop appear in the UI after async loading.
  await waitFor(() => expect(screen.getByText(/District A/)).toBeInTheDocument());
  await waitFor(() => expect(screen.getByText(/Wheat/)).toBeInTheDocument());
});

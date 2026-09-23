describe('AgriSim Digital Twin End-to-End Flow', () => {
  beforeEach(() => {
    // Intercept API calls to use mock data for deterministic testing
    cy.intercept('GET', '**/api/v1/map/districts', {
      statusCode: 200,
      body: [
        { id: 1, name: 'District A', state: 'State X' },
        { id: 2, name: 'District B', state: 'State Y' },
      ],
    }).as('getDistricts');

    cy.intercept('GET', '**/api/v1/crop/profiles', {
      statusCode: 200,
      body: [
        { id: 10, name: 'Wheat', category: 'Cereal', season: 'Rabi', ideal_temperature_c: 20, ideal_rainfall_mm: 350, optimal_soil_type: 'Loam' },
        { id: 11, name: 'Rice', category: 'Cereal', season: 'Kharif', ideal_temperature_c: 27, ideal_rainfall_mm: 1200, optimal_soil_type: 'Clay' },
      ],
    }).as('getCrops');

    cy.intercept('POST', '**/api/v1/simulation/run', {
      statusCode: 200,
      body: {
        total_cost_inr: 50000,
        estimated_yield_tons: 12.34,
        market_value_inr: 75000,
        net_profit_inr: 25000,
        roi_percentage: 50,
        risk_level: 'low',
        cost_breakdown: [{ activity: 'Seeds', unit: 'kg', unit_cost: 100, quantity: 5, total_cost: 500 }],
      },
    }).as('runSimulation');
    cy.visit('http://localhost:5173'); // Vite dev server default port
  });

  it('loads dropdowns, submits simulation and displays results', () => {
    cy.wait('@getDistricts');
    cy.wait('@getCrops');

    // Select district
    cy.get('select').first().select('1');
    // Select crop
    cy.get('select').eq(1).select('Wheat');
    // Fill inputs
    cy.get('input[placeholder="Land Area (ha)"]').type('2');
    cy.get('input[placeholder="Budget (INR)"]').type('50000');
    // Run simulation
    cy.contains('Run Simulation').click();
    cy.wait('@runSimulation');
    // Verify result cards appear
    cy.contains('Total Cost').should('exist');
    cy.contains('Estimated Yield').should('exist');
  });
});

import { render, screen } from '@testing-library/react';
import App from './App';
import '@testing-library/jest-dom';

describe('App', () => {
  it('renders the main heading', () => {
    render(<App />);
    expect(screen.getByText('Urban Mobility Data Living Laboratory (UMDL2)')).toBeInTheDocument();
  });
});

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import JobSubmissionForm from './JobSubmissionForm';
import { v4 as uuidv4 } from 'uuid';

// Mock the uuid library
jest.mock('uuid', () => ({
  v4: jest.fn(),
}));

describe('JobSubmissionForm', () => {
  let mockOnJobSubmitted;
  let fetchSpy;
  let alertSpy;

  beforeEach(() => {
    mockOnJobSubmitted = jest.fn();
    // Spy on window.fetch
    fetchSpy = jest.spyOn(window, 'fetch');
    // Spy on window.alert
    alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {}); // Mock alert to prevent dialogs
    // Reset uuid mock for each test if needed, or set a default
    uuidv4.mockReturnValue('default-uuid-1234');
  });

  afterEach(() => {
    jest.restoreAllMocks(); // Restores all spies and mocks
  });

  test('renders form inputs and submit button', () => {
    render(<JobSubmissionForm onJobSubmitted={mockOnJobSubmitted} />);
    expect(screen.getByLabelText(/job name/i)).toBeInTheDocument();
    // Label text updated in component
    expect(screen.getByLabelText(/job configuration \(not submitted\)/i)).toBeInTheDocument(); 
    expect(screen.getByRole('button', { name: /submit job/i })).toBeInTheDocument();
  });

  test('successful form submission with job name', async () => {
    fetchSpy.mockResolvedValueOnce({
      ok: true,
      status: 202,
      json: async () => ({ taskId: 'task123', session_id: 'session456' }),
    });

    render(<JobSubmissionForm onJobSubmitted={mockOnJobSubmitted} />);
    
    const jobNameInput = screen.getByLabelText(/job name/i);
    const submitButton = screen.getByRole('button', { name: /submit job/i });

    fireEvent.change(jobNameInput, { target: { value: 'Test Job' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(fetchSpy).toHaveBeenCalledWith('http://search:8000/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: 'Test Job' }),
      });
    });

    await waitFor(() => {
      expect(mockOnJobSubmitted).toHaveBeenCalledWith({
        taskId: 'task123',
        sessionId: 'session456',
        jobName: 'Test Job',
      });
    });
    expect(jobNameInput.value).toBe(''); // Form should clear on success
  });

  test('successful form submission without job name (uses uuid)', async () => {
    uuidv4.mockReturnValue('generated-uuid-for-test'); // Specific UUID for this test
    fetchSpy.mockResolvedValueOnce({
      ok: true,
      status: 202,
      json: async () => ({ taskId: 'task789', session_id: 'generated-uuid-for-test' }), // API returns the generated ID
    });

    render(<JobSubmissionForm onJobSubmitted={mockOnJobSubmitted} />);
    
    const jobNameInput = screen.getByLabelText(/job name/i); // Keep it empty
    const submitButton = screen.getByRole('button', { name: /submit job/i });

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(fetchSpy).toHaveBeenCalledWith('http://search:8000/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: 'generated-uuid-for-test' }),
      });
    });

    await waitFor(() => {
      expect(mockOnJobSubmitted).toHaveBeenCalledWith({
        taskId: 'task789',
        sessionId: 'generated-uuid-for-test', 
        jobName: 'generated-uuid-for-test', // jobName becomes the uuid
      });
    });
     expect(jobNameInput.value).toBe('');
  });

  test('form submission failure (server error 500)', async () => {
    fetchSpy.mockResolvedValueOnce({
      ok: false,
      status: 500,
      text: async () => 'Internal Server Error',
    });

    render(<JobSubmissionForm onJobSubmitted={mockOnJobSubmitted} />);
    
    fireEvent.change(screen.getByLabelText(/job name/i), { target: { value: 'Error Job' } });
    fireEvent.click(screen.getByRole('button', { name: /submit job/i }));

    await waitFor(() => {
      expect(fetchSpy).toHaveBeenCalled();
    });
    
    await waitFor(() => {
       expect(alertSpy).toHaveBeenCalledWith('Error submitting job: 500 - Internal Server Error');
    });
    expect(mockOnJobSubmitted).not.toHaveBeenCalled();
  });

  test('form submission failure (network error)', async () => {
    fetchSpy.mockRejectedValueOnce(new TypeError('Network failed'));

    render(<JobSubmissionForm onJobSubmitted={mockOnJobSubmitted} />);
    
    fireEvent.change(screen.getByLabelText(/job name/i), { target: { value: 'Network Error Job' } });
    fireEvent.click(screen.getByRole('button', { name: /submit job/i }));

    await waitFor(() => {
      expect(fetchSpy).toHaveBeenCalled();
    });

    await waitFor(() => {
        expect(alertSpy).toHaveBeenCalledWith('Network error submitting job: Network failed');
    });
    expect(mockOnJobSubmitted).not.toHaveBeenCalled();
  });
});

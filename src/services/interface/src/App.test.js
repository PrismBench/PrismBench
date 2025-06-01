import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from './App';

// Mock child components. We want to test App.js's logic, not the children's rendering details here.
// However, for JobSubmissionForm, we need to be able to trigger its onJobSubmitted prop.
let mockOnJobSubmittedCallback;
jest.mock('./components/JobSubmissionForm', () => ({ onJobSubmitted }) => {
  mockOnJobSubmittedCallback = onJobSubmitted; // Capture the callback
  return <div data-testid="job-submission-form-mock">JobSubmissionForm</div>;
});

// For JobList, we can check the props it receives.
let jobListProps;
jest.mock('./components/JobList', () => (props) => {
  jobListProps = props; // Capture props
  return <div data-testid="job-list-mock">JobList Mock Content</div>;
});


describe('App', () => {
  let fetchSpy;
  let alertSpy;

  beforeEach(() => {
    fetchSpy = jest.spyOn(window, 'fetch');
    alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});
    jest.useFakeTimers(); // Use fake timers for polling
    jobListProps = null; // Reset captured props for each test
    mockOnJobSubmittedCallback = null; // Reset captured callback
  });

  afterEach(() => {
    jest.restoreAllMocks();
    jest.clearAllTimers(); // Clear all fake timers
  });

  test('initial render with correct header and components', () => {
    render(<App />);
    expect(screen.getByRole('heading', { name: /mcts job monitoring/i })).toBeInTheDocument();
    expect(screen.getByTestId('job-submission-form-mock')).toBeInTheDocument();
    expect(screen.getByTestId('job-list-mock')).toBeInTheDocument();
    expect(jobListProps.jobs).toEqual([]); // Initially, no jobs
  });

  test('job submission, initial polling, and data update', async () => {
    render(<App />);

    // 1. Simulate Job Submission
    const jobDetails = { taskId: 'task1', sessionId: 'session1', jobName: 'Test Job 1' };
    act(() => {
      if (mockOnJobSubmittedCallback) {
        mockOnJobSubmittedCallback(jobDetails);
      } else {
        throw new Error("mockOnJobSubmittedCallback was not captured from JobSubmissionForm mock");
      }
    });
    
    // Check if job is added to JobList (still with null treeData initially)
    expect(jobListProps.jobs).toHaveLength(1);
    expect(jobListProps.jobs[0]).toMatchObject({
      taskId: jobDetails.taskId,
      sessionId: jobDetails.sessionId,
      jobName: jobDetails.jobName,
      treeData: null, // Initially null
      status: "pending" // Initial overall status derived
    });

    // 2. Initial Polling
    // Mock /status response
    fetchSpy.mockResolvedValueOnce({ // For /status
      ok: true,
      json: async () => ({
        [jobDetails.taskId]: {
          task_id: jobDetails.taskId,
          session_id: jobDetails.sessionId,
          phases: {
            phase1: { status: 'running', path: [] },
            phase2: { status: 'pending', path: [] },
          },
        },
      }),
    });
    // Mock /tree/{sessionId} response
    fetchSpy.mockResolvedValueOnce({ // For /tree/session1
      ok: true,
      json: async () => ({
        nodes: [{ id: 'node1', ...jobDetails }], // Simplified tree data
        concepts: ['c1'],
        difficulties: ['d1'],
      }),
    });

    await act(async () => {
      jest.runOnlyPendingTimers(); // Advance timers to trigger fetch
    });
    
    await waitFor(() => {
      expect(fetchSpy).toHaveBeenCalledWith('http://search:8000/status');
    });
    await waitFor(() => {
      expect(fetchSpy).toHaveBeenCalledWith(`http://search:8000/tree/${jobDetails.sessionId}`);
    });
    
    // Check JobList props reflect fetched data
    await waitFor(() => {
      expect(jobListProps.jobs[0].statusInfo.phases.phase1.status).toBe('running');
      expect(jobListProps.jobs[0].treeData).toEqual({
        nodes: [{ id: 'node1', ...jobDetails }],
        concepts: ['c1'],
        difficulties: ['d1'],
      });
      expect(jobListProps.jobs[0].status).toBe('running'); // Overall status
    });


    // 3. Subsequent Polling Update
    // Mock new /status response
     fetchSpy.mockResolvedValueOnce({ // For /status
      ok: true,
      json: async () => ({
        [jobDetails.taskId]: {
          task_id: jobDetails.taskId,
          session_id: jobDetails.sessionId,
          phases: {
            phase1: { status: 'completed', path: [] },
            phase2: { status: 'running', path: [] },
          },
        },
      }),
    });
    // Mock new /tree/{sessionId} response (tree data might also change)
    fetchSpy.mockResolvedValueOnce({ // For /tree/session1
      ok: true,
      json: async () => ({
        nodes: [{ id: 'node1', status: 'updated' }, {id: 'node2'}], 
        concepts: ['c1', 'c2'],
        difficulties: ['d1', 'd2'],
      }),
    });

    await act(async () => {
      jest.runOnlyPendingTimers(); // Advance timers again
    });

    await waitFor(() => {
      // fetch should be called again for status and tree
      // Total calls: /status (initial), /tree (initial), /status (update), /tree (update)
      expect(fetchSpy).toHaveBeenCalledTimes(4); 
    });

    // Check JobList props reflect the *new* fetched data
    await waitFor(() => {
      expect(jobListProps.jobs[0].statusInfo.phases.phase1.status).toBe('completed');
      expect(jobListProps.jobs[0].statusInfo.phases.phase2.status).toBe('running');
      expect(jobListProps.jobs[0].treeData.nodes).toHaveLength(2);
      expect(jobListProps.jobs[0].treeData.concepts).toEqual(['c1', 'c2']);
      expect(jobListProps.jobs[0].status).toBe('running'); // Overall status still running due to phase2
    });
  });

  test('handles fetch error for /status', async () => {
    render(<App />);
     act(() => {
      if (mockOnJobSubmittedCallback) mockOnJobSubmittedCallback({ taskId: 't1', sessionId: 's1', jobName: 'J1' });
    });

    fetchSpy.mockRejectedValueOnce(new Error('Failed to fetch /status'));

    await act(async () => {
      jest.runOnlyPendingTimers();
    });

    await waitFor(() => {
      expect(screen.getByText(/global error: failed to fetch \/status/i)).toBeInTheDocument();
    });
  });

  test('handles fetch error for /tree/{sessionId}', async () => {
    render(<App />);
    const jobDetails = { taskId: 'task2', sessionId: 'session2', jobName: 'Test Job 2' };
    act(() => {
      if (mockOnJobSubmittedCallback) mockOnJobSubmittedCallback(jobDetails);
    });

    // First fetch for /status is OK
    fetchSpy.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        [jobDetails.taskId]: {
          task_id: jobDetails.taskId,
          session_id: jobDetails.sessionId,
          phases: { phase1: { status: 'running' }, phase2: { status: 'pending' } },
        },
      }),
    });
    // Second fetch for /tree fails
    fetchSpy.mockRejectedValueOnce(new Error('Failed to fetch tree data'));

    await act(async () => {
      jest.runOnlyPendingTimers();
    });

    // No global error is set in App.js for individual tree fetch errors (only console.error)
    // The job's treeData should remain null or as it was.
    await waitFor(() => {
      expect(jobListProps.jobs[0].treeData).toBeNull();
      // Check that a console.error occurred (optional, requires spyOn(console, 'error'))
    });
     expect(screen.queryByText(/global error:/i)).not.toBeInTheDocument(); // No global error
  });
});

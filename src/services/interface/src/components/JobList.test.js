import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import JobList from './JobList';

// Mock JobProgressTree to simplify testing JobList and inspect props
let mockJobProgressTreeProps = [];
jest.mock('./JobProgressTree', () => (props) => {
  mockJobProgressTreeProps.push(props);
  return (
    <div data-testid="job-progress-tree">
      <p>Job ID: {props.jobId}</p>
      <p>Job Name: {props.jobName}</p>
      <p>Status: {props.status}</p>
      <pre>Tree Data: {JSON.stringify(props.treeData, null, 2)}</pre>
    </div>
  );
});

describe('JobList', () => {
  beforeEach(() => {
    // Clear the captured props before each test
    mockJobProgressTreeProps = [];
  });

  test('renders "No jobs submitted yet." when jobs array is undefined or empty', () => {
    const { rerender } = render(<JobList jobs={undefined} />);
    expect(screen.getByText(/no jobs submitted yet/i)).toBeInTheDocument();

    rerender(<JobList jobs={[]} />);
    expect(screen.getByText(/no jobs submitted yet/i)).toBeInTheDocument();
  });

  test('renders a list of jobs with JobProgressTree components', () => {
    const mockJobsData = [
      { 
        sessionId: 'session1', 
        jobName: 'Job Alpha', 
        status: 'running', 
        treeData: { nodes: [{id: 'n1'}], concepts: ['a'], difficulties: ['e'] } 
      },
      { 
        sessionId: 'session2', 
        jobName: 'Job Beta', 
        status: 'completed', 
        treeData: { nodes: [{id: 'n2'}], concepts: ['b'], difficulties: ['m'] } 
      },
      { 
        sessionId: 'session3', 
        // jobName is optional, should fallback to sessionId
        status: 'pending', 
        treeData: null // Tree data might be null initially
      },
    ];

    render(<JobList jobs={mockJobsData} />);

    const jobTrees = screen.getAllByTestId('job-progress-tree');
    expect(jobTrees).toHaveLength(mockJobsData.length);

    // Check that JobProgressTree received the correct props for each job
    expect(mockJobProgressTreeProps).toHaveLength(mockJobsData.length);

    mockJobsData.forEach((job, index) => {
      const expectedProps = {
        jobId: job.sessionId,
        jobName: job.jobName || job.sessionId, // Component logic for fallback
        status: job.status,
        treeData: job.treeData,
      };
      expect(mockJobProgressTreeProps[index]).toMatchObject(expectedProps);
      
      // Also check rendered output from the mock
      expect(screen.getByText(`Job ID: ${job.sessionId}`)).toBeInTheDocument();
      expect(screen.getByText(`Job Name: ${job.jobName || job.sessionId}`)).toBeInTheDocument();
      expect(screen.getByText(`Status: ${job.status}`)).toBeInTheDocument();
    });
  });

  test('renders JobProgressTree with correct fallback for jobName', () => {
    const jobsWithoutName = [
      { sessionId: 's001', status: 'fetching', treeData: null },
    ];
    render(<JobList jobs={jobsWithoutName} />);
    expect(screen.getByTestId('job-progress-tree')).toBeInTheDocument();
    expect(mockJobProgressTreeProps[0].jobName).toBe(jobsWithoutName[0].sessionId);
    expect(screen.getByText(`Job Name: ${jobsWithoutName[0].sessionId}`)).toBeInTheDocument();

  });
});

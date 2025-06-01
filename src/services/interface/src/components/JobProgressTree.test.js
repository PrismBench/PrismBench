import React from 'react';
import { render, screen, within } from '@testing-library/react';
import '@testing-library/jest-dom';
import JobProgressTree from './JobProgressTree';

describe('JobProgressTree', () => {
  const baseProps = {
    jobId: 'session-123',
    jobName: 'My Test Job',
    status: 'running',
  };

  const mockFullTreeData = {
    nodes: [
      { 
        id: 'root1', 
        challenge_description: 'Root node 1 challenge', 
        difficulty: 'easy', 
        status: 'completed', 
        value: 0.9, 
        visits: 10, 
        phase: 1,
        parents: [], 
        children: ['child1'] 
      },
      { 
        id: 'child1', 
        challenge_description: 'Child node 1 challenge', 
        difficulty: 'medium', 
        status: 'in_progress', 
        value: 0.7, 
        visits: 5, 
        phase: 1,
        parents: ['root1'], 
        children: [] 
      },
      { 
        id: 'root2', // Another root node for testing multiple roots
        challenge_description: 'Root node 2 challenge', 
        difficulty: 'hard', 
        status: 'pending', 
        value: 0.0, 
        visits: 0, 
        phase: 2,
        parents: [], 
        children: [] 
      },
    ],
    concepts: ['conceptA', 'conceptB'],
    difficulties: ['easy', 'medium', 'hard'],
  };
  
  const mockTreeDataWithNoExplicitRoots = { // All nodes have parents, or complex structure
     nodes: [
      { id: 'n1', parents: ['n3'], children: ['n2'], challenge_description: 'Node 1', value:0, visits:0, phase:0, difficulty:'easy', status:'pending' },
      { id: 'n2', parents: ['n1'], children: ['n3'], challenge_description: 'Node 2', value:0, visits:0, phase:0, difficulty:'easy', status:'pending' },
      { id: 'n3', parents: ['n2'], children: ['n1'], challenge_description: 'Node 3', value:0, visits:0, phase:0, difficulty:'easy', status:'pending' }, // Cycle
    ],
    concepts: ['c1'],
    difficulties: ['d1']
  };


  test('renders basic job information when treeData is null', () => {
    render(<JobProgressTree {...baseProps} treeData={null} />);
    expect(screen.getByText(`Job: ${baseProps.jobName}`)).toBeInTheDocument();
    expect(screen.getByText(`Session ID: ${baseProps.jobId}`)).toBeInTheDocument();
    expect(screen.getByText(`Status: ${baseProps.status}`)).toBeInTheDocument();
    expect(screen.getByText(/Fetching tree data or tree data is not available.../i)).toBeInTheDocument();
  });

  test('renders basic job information and node count when treeData is present but nodes array is empty', () => {
    const emptyTreeData = { nodes: [], concepts: ['c1'], difficulties: ['d1'] };
    render(<JobProgressTree {...baseProps} treeData={emptyTreeData} />);
    expect(screen.getByText(`Node Count: 0`)).toBeInTheDocument();
    expect(screen.getByText(`Concepts: c1`)).toBeInTheDocument();
    expect(screen.getByText(`Difficulties: d1`)).toBeInTheDocument();
    expect(screen.getByText(/No root nodes identified for visualization, or tree is empty./i)).toBeInTheDocument();
  });

  test('renders full tree structure correctly', () => {
    render(<JobProgressTree {...baseProps} treeData={mockFullTreeData} />);

    // Check basic info
    expect(screen.getByText(`Node Count: ${mockFullTreeData.nodes.length}`)).toBeInTheDocument();
    expect(screen.getByText(`Concepts: ${mockFullTreeData.concepts.join(', ')}`)).toBeInTheDocument();
    expect(screen.getByText(`Difficulties: ${mockFullTreeData.difficulties.join(', ')}`)).toBeInTheDocument();

    // Check for root1 and its details
    const root1Element = screen.getByText('ID: root1').closest('li');
    expect(root1Element).toBeInTheDocument();
    expect(within(root1Element).getByText(/Description: Root node 1 challenge/i)).toBeInTheDocument();
    expect(within(root1Element).getByText(/Difficulty: easy/i)).toBeInTheDocument();
    expect(within(root1Element).getByText(/Status: completed/i)).toBeInTheDocument();
    expect(within(root1Element).getByText(/Value: 0.900/i)).toBeInTheDocument(); // toFixed(3)
    expect(within(root1Element).getByText(/Visits: 10/i)).toBeInTheDocument();
    expect(within(root1Element).getByText(/Phase: 1/i)).toBeInTheDocument();
    expect(within(root1Element).getByText(/Children IDs: child1/i)).toBeInTheDocument();
    
    // Check for child1 nested under root1
    const child1Element = within(root1Element).getByText('ID: child1').closest('li');
    expect(child1Element).toBeInTheDocument();
    expect(within(child1Element).getByText(/Description: Child node 1 challenge/i)).toBeInTheDocument();
    expect(within(child1Element).getByText(/Parents: root1/i)).toBeInTheDocument();
    expect(child1Element.style.marginLeft).toBe('20px'); // Indentation for level 1

    // Check for root2 (second root)
    const root2Element = screen.getByText('ID: root2').closest('li');
    expect(root2Element).toBeInTheDocument();
    expect(within(root2Element).getByText(/Description: Root node 2 challenge/i)).toBeInTheDocument();
    expect(root2Element.style.marginLeft).toBe('0px'); // No indentation for level 0
  });
  
  test('handles treeData with no explicit roots (all nodes are children or interconnected)', () => {
    // This test relies on the fallback root-finding logic (nodes not listed as children of others)
    // In mockTreeDataWithNoExplicitRoots, no node is truly a root by the "not a child" heuristic if they form a cycle.
    // The component logs a warning and potentially shows nothing or all nodes.
    // The current implementation of root finding would pick all nodes if no node has an empty parent list AND no node is "not a child".
    // Let's adjust mock to have one node that IS NOT a child of any other
     const mockTreeDataNoChildRoots = {
        nodes: [
            { id: 'n1', parents: ['n3'], children: ['n2'], challenge_description: 'Node 1', value:0, visits:0, phase:0, difficulty:'easy', status:'pending' },
            { id: 'n2', parents: ['n1'], children: ['n3'], challenge_description: 'Node 2', value:0, visits:0, phase:0, difficulty:'easy', status:'pending' },
            // n3 is not a child of n1 or n2 in this specific list (though its parents list says n2)
            // this is a bit of a broken graph, but tests the "not a child" heuristic
            { id: 'n3', parents: ['n2'], children: [], challenge_description: 'Node 3 (potential root by fallback)', value:0, visits:0, phase:0, difficulty:'easy', status:'pending' },
        ],
        concepts: ['c1'],
        difficulties: ['d1']
    };

    const consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});
    render(<JobProgressTree {...baseProps} treeData={mockTreeDataNoChildRoots} />);
    
    // Expect n3 to be identified as a root by the fallback logic
    const n3Element = screen.getByText('ID: n3').closest('li');
    expect(n3Element).toBeInTheDocument();
    expect(within(n3Element).getByText(/Description: Node 3 \(potential root by fallback\)/i)).toBeInTheDocument();

    // n1 and n2 should be children of something if the graph is drawn based on parent/child links
    // However, our root finding only finds n3. n1 is child of n3 (by ID), n2 child of n1.
    // The test here is mostly that it *doesn't crash* and *finds some root* if possible.
    // The console warning for "no roots by empty parents list or by child reference" might appear
    // if the graph is fully cyclic and the "not a child" heuristic also fails.
    // In the case of mockTreeDataWithNoExplicitRoots (original cyclic one), it would likely show "No root nodes..."
    // or all nodes if the heuristic is relaxed.
    // For the adjusted mockTreeDataNoChildRoots, n3 should be a root.

    // If the original truly cyclic mockTreeDataWithNoExplicitRoots was used:
    // render(<JobProgressTree {...baseProps} treeData={mockTreeDataWithNoExplicitRoots} />);
    // expect(screen.getByText(/No root nodes identified for visualization, or tree is empty./i)).toBeInTheDocument();
    // expect(consoleWarnSpy).toHaveBeenCalled(); 
    
    consoleWarnSpy.mockRestore();
  });

  test('node details are rendered correctly', () => {
    const singleNodeData = {
      nodes: [
        { 
          id: 'nodeA', 
          challenge_description: 'Challenge A', 
          difficulty: 'easy', 
          status: 'completed', 
          value: 0.9555, 
          visits: 15, 
          phase: 1,
          parents: ['parentX', 'parentY'], 
          children: ['childZ'] 
        }
      ],
      concepts: [],
      difficulties: []
    };
    render(<JobProgressTree {...baseProps} treeData={singleNodeData} />);
    
    const nodeAElement = screen.getByText('ID: nodeA').closest('li');
    expect(within(nodeAElement).getByText(/Description: Challenge A/i)).toBeInTheDocument();
    expect(within(nodeAElement).getByText(/Difficulty: easy/i)).toBeInTheDocument();
    expect(within(nodeAElement).getByText(/Status: completed/i)).toBeInTheDocument();
    expect(within(nodeAElement).getByText(/Value: 0.956/i)).toBeInTheDocument(); // toFixed(3)
    expect(within(nodeAElement).getByText(/Visits: 15/i)).toBeInTheDocument();
    expect(within(nodeAElement).getByText(/Phase: 1/i)).toBeInTheDocument();
    expect(within(nodeAElement).getByText(/Parents: parentX, parentY/i)).toBeInTheDocument();
    expect(within(nodeAElement).getByText(/Children IDs: childZ/i)).toBeInTheDocument();
  });
});

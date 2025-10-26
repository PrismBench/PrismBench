## 0.3.3 (2025-08-17)

### Fix

- **data_loader**: filter out phase nodes with phase value of 1
- **analysis/interface_client**: add InterfaceClient for LLM service interaction for the analysis service

### Refactor

- **analysis/main**: streamline metric collection and integrate async processing
- **analysis/error_metrics**: integrate async error analysis with LLM service
- **analysis/pattern_metrics**: update PatternMetricsAnalyzer to use InterfaceClient and enhance async processing

## 0.3.2 (2025-08-11)

### Refactor

- **interface_client**: simplify session initialization and remove unused task polling logic

## 0.3.1 (2025-08-04)

### Refactor

- **configs/agents**: changed the current system prompts and yaml templates for agents to work with dspy

## 0.3.0 (2025-08-04)

### Feat

- **search**: implement task resumption functionality in MCTS

### Fix

- **search/mcts**: fixed the bug where timeout did not trigger cancellation and the node delete bug where parent nodes were removed

### Refactor

- **environment**: enhance logging and error handling in coding challenge execution
- **analysis**: refactored the analysis module for integration with the new data schema we have

## 0.2.1 (2025-07-23)

### Refactor

- **llm_interface**: remove test script for LLM Interface API
- **llm_interface**: update type annotations for interaction templates and past messages
- **llm_interface**: enhance session repository and service for role management and history retrieval
- **llm_interface**: update domain models for session and role history

## 0.2.0 (2025-07-22)

### Feat

- **llm_interface**: add endpoint to retrieve active sessions and enhance session data retrieval

### Fix

- **llm_interface**: enhance session repository with role and message management

### Refactor

- **llm_interface**: update example input for InteractRequest
- **llm_interface**: update LLMInterface to manage past messages
- **llm_interface**: improve session service to return LLMInterface objects
- **llm_interface**: update endpoint dependencies and remove unused methods
- **llm_interface**: enhance session management by updating role handling and removing history features
- **llm_interface**: clean up router and dependencies by removing task-related components
- **llm_interface**: add role field to InteractRequest and remove task_id from InteractResponse
- **llm_interface**: removing the scripts for tasks

## 0.1.3 (2025-07-22)

### Fix

- **pre-commit**: set JSON pretty formatting to use 2 spaces for indentation
- **Makefile**: update docker-compose file extension from .yml to .yaml for consistency

## 0.1.2 (2025-07-21)

### Fix

- **egg-info**: getting rid of the damn egg info

## 0.1.1 (2025-07-21)

### Refactor

- **llm_interface**: Streamline dependencies in pyproject.toml
- **llm_interface**: Simplify interaction service and remove obsolete conversation history handling
- **llm_interface**: Update response handling and conversation history retrieval
- **llm_interface**: Move utility functions to a new module and remove obsolete tools
- **llm_interface**: Simplify LLMInterface structure and enhance agent interaction
- **challenge_designer**: Revise agent configuration structure and interaction templates
- **prompt_manager**: Enhance agent configuration validation and signature generation
- **prompt_manager**: Replace PromptManager class with standalone functions for loading agent config and creating agent signatures

## 0.1.0 (2025-07-20)

### Feat

- **gui**: Reintroduce GUI service configuration in docker-compose.yml
- **gui**: Add concept combinations feature to job performance summary
- **gui**: Enhance job management with tree visualization and job control features
- **gui**: Enhance job management with template storage and API integration
- **gui**: Refactor Dashboard for improved job management and UI clarity
- **service**: Refactor task creation to use configurable phase sequences
- **gui**: Integrate service health monitoring into Dashboard
- **api**: Update health check endpoint and response model
- **gui**: Refactor Dashboard and JobList components for improved job management
- **gui**: Implement automatic real-time polling and enhanced tree visualization
- **gui**: Enhance results page and tree data handling
- **gui**: Introduce live tree visualization and enhance job status component
- **gui**: Add new UI components for enhanced user interaction
- **gui**: Enhance job form and introduce job list and templates components
- **gui**: Enhance job management dashboard with new components and hooks
- **gui**: Initialize PrismBench GUI with essential configuration and structure
- **gui**: Add API integration and polling hook for job management
- **gui**: Implement job management components for PrismBench
- **gui**: Add initial layout and styling for PrismBench GUI
- **tree**: Remove deprecated tree.json file
- **config**: Enhance phase 3 configuration parameters
- **config**: Add environment configuration for coding challenges
- **mcts**: Enhance phase initialization and configuration parameters
- **mcts**: Implement timeout handling and node removal in BasePhase evaluation
- **tree**: Implement node removal functionality in Tree class
- **config**: Add task timeout parameter to PhaseParametersConfig
- **config**: Enhance configuration management with experiment settings
- **config**: Add default experiment and tree configurations
- **config**: Add phase and tree configuration files for enhanced modularity
- **mcts**: Add PhaseLoader class for dynamic phase module discovery and loading
- **environment**: Refactor application structure and consolidate main entry point
- **environment**: Add core configuration, dependencies, and exception handling
- **environment**: Implement environment services for coding challenges
- **environment**: Introduce models for challenge requests, results, and data trails
- **environment**: Restructure API endpoints for coding challenges and health checks
- **environment**: Enhance BaseEnvironment with improved documentation and structure
- **environment**: Introduce base and enhanced coding challenge environments
- **llm_interface**: Enhance task status endpoint with improved error handling and logging
- **llm_interface**: Enhance session management with improved error handling and response documentation
- **requests**: Enhance session_id field with example in SessionRequest model
- **llm_interface**: Add comprehensive test suite for LLM Interface API
- **llm_interface**: Implement main application module for LLM Interface API
- **llm_interface**: Remove LLMInterface and PromptManager classes
- **llm_interface**: Add LLM interface and prompt management functionality
- **llm_interface**: Introduce versioned API structure and new endpoints
- **llm_interface**: Implement interaction and session management services
- **llm_interface**: Implement session and task repositories for Redis management
- **llm_interface**: Add domain models and request/response structures
- **llm_interface**: Implement core configuration and dependency management
- **llm_interface**: Add initial structure for LLM interface service
- **health**: Add health check endpoint for service status verification
- **search**: Refactor API structure and introduce v1 endpoints
- **search**: Introduce session and task services with MCTS integration
- **search**: Implement session and task repositories with domain models
- **search**: Implement core service structure and configuration management
- **mcts**: Implement multi-phase MCTS framework with enhanced configurations
- **environment**: Enhance agent interactions and error handling in coding challenge environment
- **mcts**: Add error handling and logging for node operations
- **mcts**: Introduce Phase Three strategies for node selection, evaluation, and expansion
- **environment**: Introduce EnhancedEnvironmentClient for improved API interaction
- **mcts/phase_2**: Refactor node value updates and introduce evaluation strategy
- **mcts/phase_2**: Implement Phase Two strategies for node selection, evaluation, and expansion
- **tests**: Add initial test suite for search functionality
- **mcts/phase_1**: Implement Phase One strategies for node selection, evaluation, and expansion
- **base_phase**: Enhance logging and progress tracking in search algorithm
- **tree**: Enhance Tree class with logging and improved node management
- **mcts_phase_1**: Implement Phase One strategies for node selection, evaluation, and expansion
- Enhance BasePhase with strategy registration and execution
- Introduce Phase One of MCTS with asynchronous execution and node management
- Remove mcts.py file and associated Monte Carlo Tree Search logic
- Implement job cancellation feature and enhance job status handling
- Complete Phases 3 and 4 of the migration plan with advanced features and optimizations
- Refactor App and JobList components for improved job management and UI
- Add new UI components for enhanced user experience
- Implement migration plan for PrismSynth interface to shadcn/ui
- Update App component with enhanced UI and API integration
- Revamp Job List and Progress Tree components with enhanced UI and functionality
- Enhance interface service with Tailwind CSS integration and configuration files
- Add Nginx configuration for serving React app and proxying API calls
- Update Dockerfile and enhance NodeData schema in search service
- Add health check endpoint and improve session handling in search service
- Integrate interface service with search service for job processing
- **mcts**: implement phase management in MCTS execution
- **mcts**: implement phase-based MCTS with configurable parameters
- **mcts**: enhance node selection and expansion logic in MCTS algorithm
- **redis**: integrate Redis for session and task management in LLM interface
- **redis**: implement Redis storage helper for LLM interface
- **docker**: add Redis service and update llm-interface configuration
- **environment**: implement asynchronous script execution and process pool management
- **config**: add config_loader to load YAML configuration files
- **search**: load concepts and difficulties from config file
- **node**: add unique ID generation and ancestor ID retrieval method
- **github_fetcher**: improve documentation and fix initialization of repos list
- **dataset_builder**: implement dataset building functionality for GitHub repositories
- **schema**: enhance commit representation with detailed change tracking
- **github_fetcher**: implement caching for GitHub repository fetches
- **dataset**: add dataset service to docker-compose and update Dockerfile
- **schema**: add data models for GitHub repositories and commits
- **github_fetcher**: implement GitHub repository fetching functionality
- **dataset**: added the scaffolding for the dataset service
- **search**: enhance session management and task status retrieval in endpoints.py
- enhance session initialization and MCTS execution in endpoints.py
- improve error handling and logging in environment.py
- clean up capability_mcts.py
- update MCTS implementation in endpoints.py
- enhance MCTS algorithm and Dockerfile
- update response handling in EnvironmentClient
- enhance MCTS algorithm and update requirements
- improve tests in EnvironmentServiceTester
- refine endpoint responses and clean up MCTS expansion logic
- enhance schema definitions and improve code readability
- update requirements and improve test configuration
- add comprehensive tests for LLM interface endpoints
- add unit tests for PromptManager
- add unit tests for LLM schema validation
- add pytest fixtures for LLM interface testing
- update LLM interface configuration and improve code structure
- update requirements and improve provider configuration
- update configuration files and improve code structure
- clean up imports and improve code readability
- update configuration and clean up code
- update environment configuration and clean up code
- update configuration handling and environment variables
- update application module and session descriptions
- refactor LLM client integration and add InterfaceClient
- clean up imports and router configuration
- add health check endpoint and update service configurations
- update healthcheck URLs and refactor LLMInterface
- refactor environment client and update service configurations
- **search**: update search service and endpoints
- **mcts**: refactor environment client usage in MCTS classes
- **tree**: update tree module and add TreeExtractor utility
- **search**: add search service configuration and update environment settings
- **search**: remove EnvironmentClient and update imports
- **tree**: refactor learning rate configuration and import statement
- **search**: implement main application module and endpoints for LLM Interface API
- **mcts**: enhance MCTS module with EnvironmentClient integration
- update .gitignore and remove __pycache__ files
- **mcts**: update type imports in base.py
- **mcts**: refine node expansion logic in ConceptMCTS
- **search**: add Docker support and configuration files
- **search**: add new search service files and adjust imports
- **mcts**: enhance BaseMCTS class with abstract method and import adjustments
- **mcts**: enhance BaseMCTS with convergence parameters
- **tree**: simplify tree initialization and remove phase markers
- refactor imports and update response models
- **environment**: add EnvironmentClient for API interaction - src/services/search/src/environment_client.py: Implemented EnvironmentClient class to interact with the Environment Service API, including methods for running coding challenges.
- **mcts**: update MCTS module and add tree structure
- **mcts**: add CompMCTS class for comprehensive coding challenges
- **mcts**: implement ConceptMCTS class for challenging concept exploration
- **mcts**: add CapabilityMCTS class and initialize MCTS structure
- **llm**: Update agent configurations and improve code formatting
- **environment**: Add health check and challenge execution endpoints
- **app**: Enhance environment service API
- **llm_interface**: Enhance API endpoints with improved documentation and status handling
- **app**: Enhance LLM Interface API with improved documentation and metadata
- **docker-compose**: add environment service configuration
- **llm_interface**: implement FastAPI service for LLM interaction
- **docker**: add containerization for LLM interface service
- **llm_interface**: add prompt_manager module for configuration management
- **llm_interface**: major refactor of LLM interaction module

### Fix

- **makefile**: Enhance Makefile for improved setup and dependency management
- **gui**: Update phase sequence naming convention in JobForm and JobTemplates
- **llm_interface**: Update configuration file extensions from .yml to .yaml across multiple services
- **client**: Reduce default timeout in EnvironmentClient initialization from 300 to 60 seconds
- **config**: Update task timeout in PhaseParametersConfig to 90 seconds
- **config**: Update environment structure in phase_configs.yaml
- **environment**: Update health check URL and refactor Dockerfile command
- **llm_interface**: Enhance provider configuration handling in LLMInterface
- **llm_interface**: Update import paths for LLMInterface
- **search**: Update health check endpoint and application entry point
- **search**: Update model configuration and API response handling
- **tree**: Adjust node reuse logic based on phase
- Correct health check URL in docker-compose.yml
- **params**: increase convergence checks for improved algorithm stability
- **llm_interface**: add error handling for empty formatted output and update Redis error handling
- **mcts**: added waiting for running tasks once the convergence checks are finished
- **docker-compose**: Rename environment variable for clarity
- **environment**: Correct test case extraction logic in CodingChallengeEnvironment

### Refactor

- **gui**: use shared api client
- **gui**: Remove obsolete real-time polling documentation and GUI components
- **interface**: removing the old interface to begin working on a new one
- **test**: Remove outdated main function docstring
- **environment**: Update EnvironmentClient for coding challenge execution
- **config**: Standardize environment configuration formatting
- **config**: Revise environment configuration structure and loading
- **environment**: Remove EnhancedEnvironmentService and simplify dependencies
- **environment**: Enhance challenge execution with environment selection
- **environment**: Update ChallengeRequest model to streamline parameters
- **environment**: Simplify environment service and enhance challenge execution
- **environment**: Rename strategy to environment and enhance environment registration
- **mcts**: Improve node expansion logic and evaluation handling
- **config**: Consolidate configuration files and update parameter handling
- **search**: Simplify environment client initialization and update phase naming
- **BasePhase**: Update logging and file naming for tree saving
- **mcts**: Lazy import create_phase to avoid circular dependency
- **init**: Remove unused environment client imports from core initialization
- **dependencies**: Remove environment client dependencies from configuration
- **extracted_problems**: Remove JSON files for problems by combination, concept, and difficulty
- **mcts**: Rename strategy registration to phase method for clarity
- **mcts**: Remove unused import in BasePhase and streamline imports
- **mcts**: Update BasePhase to use phase_name and streamline parameter handling
- **search**: Update EnvironmentClient to use configuration dictionary
- **mcts**: Remove PhaseLoader class and integrate phase loading into PhaseRegistry
- **mcts**: Rename strategy_name to phase_name in create_phase function
- **config**: Remove unused import from PhaseParametersConfig
- **config**: Rename environment attribute to name in PhaseEnvironmentConfig
- **mcts**: Simplify MCTSService and enhance phase management
- **config**: Restructure phase configuration classes and update settings management
- **mcts**: Update import statements and streamline logging in MCTS phases
- **environment**: Update import statements for improved module structure
- **interface_client**: Simplify logging and API request formatting
- **environment**: Improve code documentation and consistency in coding challenge environments
- **llm_interface**: Simplify API router configuration
- **llm_interface**: Clean up import statements and enhance task status endpoint documentation
- **llm_interface**: Remove test files for LLM interface
- **llm_interface**: Remove endpoints and schema files
- **llm_interface**: Update LLMInterface initialization to use factory method
- **llm_interface**: Update configuration and dependency management
- **llm_interface**: Standardize endpoint tags and clean up code
- **search**: Update API metadata and clean up endpoint tags
- **search**: Standardize import order across endpoint modules
- **search**: Organize and standardize import statements in node and tree modules
- **search**: Standardize import order and clean up service files
- **search**: Clean up MCTS module by removing legacy imports and unused variables
- **search**: Organize imports and clean up response models
- Remove outdated interface and planning documents
- **mcts**: Rename temporary strategies to phase-specific names
- **mcts**: Remove Phase One, Two, and Three implementations
- **mcts**: Remove unused Phase One, Two, and Three files
- **tree**: Simplify difficulty adjustment logic in Tree class
- **base_phase**: Enhance configuration handling and parameter management
- **base_phase**: Improve node evaluation and expansion logic
- **base_phase**: Enhance BasePhase with asynchronous node management and convergence checks
- Restructure MCTS configuration and implementation
- **mcts**: standardize score calculation method and enhance node selection
- **mcts**: update convergence condition and improve score calculation
- **llm_interface**: improve error logging and streamline interaction process
- **environment**: improve agent initialization and response handling
- **interface_client**: update session initialization and role handling
- **llm_interface**: switch application server to gunicorn and update dependencies
- **llm_interface**: update session initialization and role management
- **llm_interface**: enhance LLMInterface for improved role management and content extraction
- **prompt_manager**: update PromptManager to handle agent configurations
- **environment**: switch from uvicorn to gunicorn for application server
- **mcts**: streamline initialization in CapabilityMCTS and CompMCTS
- **node**: update update_node_score method to include learning rate
- **mcts**: enhance BaseMCTS initialization and configuration handling
- **mcts**: enhance task management in BaseMCTS for improved node handling
- **mcts**: adjust max depth in CapabilityMCTS and update documentation
- **search**: streamline concepts and difficulties initialization in endpoints.py
- remove unused files and clean up codebase
- **tree**: reorganize imports and clean up code
- src/services/search/src/tree/tree.py: Adjusted import order and removed unnecessary imports for clarity.
- src/services/search/src/tree/tree_extractor.py: Reorganized imports and cleaned up code structure.
- src/services/search/src/tree/tree_viz_compact.py: Updated import order and removed redundant imports.
- **mcts**: created the base MCTS class and re-organized definitions
- **app**: Remove unused imports from FastAPI applications
- **environment**: Remove unused __init__.py file
- **environment**: Enhance challenge environment with improved initialization and file management
- **environment**: Implement structured challenge results tracking
- **llm_interface**: consolidate LLM interface and prompt management modules

# Implementation Plan

- [ ] 1. Enhance initial height calculation to accommodate menus
  - Modify the min_height calculation to include buffer space for dropdown menus
  - Add constant for menu buffer space (e.g., 200px) to ensure adequate room
  - Update height management logic to use enhanced minimum height
  - Test that menus fit within the calculated height without clipping
  - _Requirements: 2.1, 2.2_

- [ ] 2. Research and configure Milkdown Crepe menu positioning options
  - [ ] 2.1 Investigate Crepe toolbar menu configuration
    - Research Milkdown Crepe documentation for toolbar dropdown positioning options
    - Identify configuration options for menu placement (above/below, left/right alignment)
    - Test different toolbar configurations to understand available positioning controls
    - Document current menu behavior and identify positioning limitations
    - _Requirements: 1.1, 1.4_

  - [ ] 2.2 Research slash menu positioning configuration
    - Investigate Crepe slash menu (/) positioning and sizing options
    - Test slash menu behavior in constrained spaces
    - Identify configuration options for menu max-height and scrolling
    - Research options to position slash menu above cursor when space is limited
    - _Requirements: 1.1, 3.1_

  - [ ] 2.3 Research table editing menu configuration
    - Investigate table editing menu positioning options in Crepe
    - Test table menu behavior near iframe boundaries
    - Identify options for constraining table menu size and position
    - Research scrollable container options for table formatting menus
    - _Requirements: 1.1, 3.1_

- [ ] 3. Implement intelligent menu positioning within Crepe configuration
  - [ ] 3.1 Configure toolbar dropdowns for optimal positioning
    - Implement Crepe configuration to prefer upward positioning for toolbar menus
    - Add max-height constraints to toolbar dropdowns with internal scrolling
    - Configure menu alignment to stay within iframe boundaries
    - Test toolbar menu visibility in various editor heights
    - _Requirements: 1.1, 1.4, 3.1, 3.3_

  - [ ] 3.2 Configure slash menu for constrained spaces
    - Implement slash menu configuration with max-height and scrolling
    - Configure slash menu to position above cursor when insufficient space below
    - Add intelligent positioning based on cursor location within iframe
    - Ensure slash menu content remains accessible through scrolling
    - _Requirements: 1.1, 3.1, 3.3_

  - [ ] 3.3 Configure table editing menus for iframe constraints
    - Implement table menu positioning to respect iframe boundaries
    - Add scrollable containers for large table formatting options
    - Configure table menus to use compact layouts when space is limited
    - Ensure table editing remains functional in small iframe heights
    - _Requirements: 1.1, 3.1, 3.3_

- [ ] 4. Add CSS styling for menu constraint handling
  - [ ] 4.1 Implement scrollable menu container styles
    - Add CSS for max-height constraints on dropdown menus
    - Implement smooth scrolling for menu containers
    - Add visual indicators for scrollable menu content
    - Ensure scrollable menus work across different browsers
    - _Requirements: 3.3_

  - [ ] 4.2 Add responsive menu styling for different iframe sizes
    - Implement CSS media queries or container queries for menu sizing
    - Add compact menu layouts for small iframe heights
    - Ensure menu text and icons remain readable in constrained spaces
    - Test menu styling across different screen sizes and zoom levels
    - _Requirements: 3.1, 3.2, 3.4_

- [ ] 5. Implement boundary detection utilities (without dynamic resizing)
  - Create utilities to calculate available space around menu trigger elements
  - Implement iframe boundary detection for menu positioning decisions
  - Add functions to determine optimal menu position within available space
  - Create fallback positioning logic when preferred positions don't fit
  - _Requirements: 1.4, 3.1, 3.2_

- [ ] 6. Add comprehensive testing for menu visibility
  - [ ] 6.1 Create tests for menu positioning in various iframe heights
    - Test toolbar menus in minimum height configurations
    - Test slash menu visibility with different content lengths
    - Test table editing menus in constrained spaces
    - Verify all menus remain accessible and functional
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [ ] 6.2 Test menu behavior across different screen sizes
    - Test menu positioning on mobile viewports
    - Test menu behavior with different zoom levels
    - Verify menu scrolling works correctly on touch devices
    - Test multiple simultaneous menus without overlap issues
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 7. Update component parameters and documentation
  - Update min_height parameter documentation to explain menu accommodation
  - Add guidance on choosing appropriate min_height values for different use cases
  - Create examples showing menu behavior in different height configurations
  - Add troubleshooting guide for menu visibility issues
  - _Requirements: 2.1_
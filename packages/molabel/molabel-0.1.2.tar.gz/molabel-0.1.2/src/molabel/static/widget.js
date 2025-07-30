function render({ model, el }) {
  // Create the main container
  const container = document.createElement('div');
  container.className = 'molabel-container';
  container.tabIndex = 0; // Make container focusable via tab key only
  
  // Create header with status and settings
  const header = document.createElement('div');
  header.className = 'molabel-header';
  
  const status = document.createElement('div');
  status.className = 'molabel-status';
  
  header.appendChild(status);
  
  // Create example display
  const exampleContainer = document.createElement('div');
  exampleContainer.className = 'molabel-example';
  
  // Create controls
  const controls = document.createElement('div');
  controls.className = 'molabel-controls';
  
  const prevBtn = document.createElement('button');
  prevBtn.textContent = 'Previous';
  prevBtn.className = 'molabel-btn molabel-btn-prev';
  
  const yesBtn = document.createElement('button');
  yesBtn.textContent = 'Yes';
  yesBtn.className = 'molabel-btn molabel-btn-yes';
  
  const noBtn = document.createElement('button');
  noBtn.textContent = 'No';
  noBtn.className = 'molabel-btn molabel-btn-no';
  
  const skipBtn = document.createElement('button');
  skipBtn.textContent = 'Skip';
  skipBtn.className = 'molabel-btn molabel-btn-skip';
  
  controls.appendChild(prevBtn);
  controls.appendChild(yesBtn);
  controls.appendChild(noBtn);
  controls.appendChild(skipBtn);
  
  // Create notes field
  const notesContainer = document.createElement('div');
  notesContainer.className = 'molabel-notes-container';
  
  const notesLabelContainer = document.createElement('div');
  notesLabelContainer.className = 'molabel-notes-label-container';
  
  const notesLabel = document.createElement('label');
  notesLabel.textContent = 'Notes:';
  
  const micButton = document.createElement('button');
  micButton.className = 'molabel-mic-btn';
  micButton.innerHTML = '🎤';
  micButton.title = 'Click to record speech or hold Alt+6';
  micButton.type = 'button';
  
  const gamepadIndicator = document.createElement('span');
  gamepadIndicator.className = 'molabel-gamepad-indicator';
  gamepadIndicator.innerHTML = '🎮';
  gamepadIndicator.style.display = 'none';
  gamepadIndicator.title = 'Gamepad detected';
  
  const buttonContainer = document.createElement('div');
  buttonContainer.className = 'molabel-button-container';
  buttonContainer.appendChild(gamepadIndicator);
  buttonContainer.appendChild(micButton);
  
  notesLabelContainer.appendChild(notesLabel);
  notesLabelContainer.appendChild(buttonContainer);
  
  const notesField = document.createElement('textarea');
  notesField.className = 'molabel-notes';
  notesField.rows = 3;
  notesField.placeholder = 'Add any notes about this example...';
  
  notesContainer.appendChild(notesLabelContainer);
  notesContainer.appendChild(notesField);
  
  // Create progress bar
  const progressContainer = document.createElement('div');
  progressContainer.className = 'molabel-progress-container';
  const progressBar = document.createElement('div');
  progressBar.className = 'molabel-progress-bar';
  const progressFill = document.createElement('div');
  progressFill.className = 'molabel-progress-fill';
  progressBar.appendChild(progressFill);
  progressContainer.appendChild(progressBar);
  
  // Create shortcuts display
  const shortcutsInfo = document.createElement('div');
  shortcutsInfo.className = 'molabel-shortcuts';
  
  // Gamepad indicator is now part of notes label container
  
  // Gamepad state variables (declare early)
  let gamepadConnected = false;
  let lastGamepadEvent = '';
  let gamepadIndex = -1;
  let currentlyPressedButtons = new Set(); // Track all currently pressed buttons
  
  // Speech recognition variables
  let speechRecognition = null;
  let speechAvailable = false;
  let isRecording = false;
  let speechGamepadPressed = false;
  let originalNotesText = ''; // Store original text before speech session
  
  
  // Assemble the widget
  container.appendChild(header);
  container.appendChild(progressContainer);
  container.appendChild(exampleContainer);
  container.appendChild(controls);
  container.appendChild(notesContainer);
  container.appendChild(shortcutsInfo);
  el.appendChild(container);
  
  // Helper function to render examples
  function renderExample(example) {
    // Default rendering
    if (typeof example === 'object') {
      return JSON.stringify(example, null, 2);
    }
    return String(example);
  }
  
  // Update display function
  function updateDisplay() {
    console.log('🔄 updateDisplay called');
    const examples = model.get('examples');
    const currentIndex = model.get('current_index');
    const showNotes = model.get('notes');
    const shortcuts = model.get('shortcuts');
    
    // Update status
    status.textContent = `Example ${currentIndex + 1} of ${examples.length}`;
    
    // Update example display
    if (examples.length > 0 && currentIndex < examples.length) {
      const currentExample = examples[currentIndex];
      // Use _html key if available, otherwise use default rendering
      if (currentExample._html) {
        exampleContainer.innerHTML = currentExample._html;
      } else {
        const rendered = renderExample(currentExample);
        exampleContainer.textContent = rendered;
      }
    } else {
      exampleContainer.textContent = 'No examples to display';
    }
    
    // Update notes field with existing annotation if available
    const annotations = model.get('annotations');
    const existingAnnotation = annotations.find(ann => ann.index === currentIndex);
    const newNotesValue = existingAnnotation ? existingAnnotation._notes || '' : '';
    
    // Only update notes field if we're not currently recording speech
    if (!isRecording) {
      notesField.value = newNotesValue;
      console.log('📝 updateDisplay set notes field to:', newNotesValue);
    } else {
      console.log('🚫 updateDisplay skipped notes update because currently recording speech');
    }
    
    // Show/hide notes
    notesContainer.style.display = showNotes ? 'block' : 'none';
    
    // Update progress bar based on current position
    const progress = examples.length > 0 ? (currentIndex / examples.length) * 100 : 0;
    progressFill.style.width = `${progress}%`;
    
    // Shortcuts display with table
    const gamepadShortcuts = model.get('gamepad_shortcuts');
    const hasShortcuts = (shortcuts && Object.keys(shortcuts).length > 0) || 
                        (gamepadShortcuts && Object.keys(gamepadShortcuts).length > 0);
    
    let shortcutsText = '';
    if (hasShortcuts) {
      shortcutsText = `
        <details class="shortcuts-details">
          <summary>Shortcuts</summary>
          <table class="shortcuts-table">
            <thead>
              <tr>
                <th>Action</th>
                <th>Keyboard</th>
                <th>Gamepad</th>
              </tr>
            </thead>
            <tbody>`;
      
      // Create unified action list
      const allActions = new Set();
      Object.values(shortcuts).forEach(action => allActions.add(action));
      Object.values(gamepadShortcuts || {}).forEach(action => allActions.add(action));
      
      const actionOrder = ['prev', 'yes', 'no', 'skip', 'focus_notes', 'speech_notes'];
      const sortedActions = actionOrder.filter(action => allActions.has(action));
      
      sortedActions.forEach(action => {
        const keyboardKey = Object.keys(shortcuts).find(key => shortcuts[key] === action) || '';
        const gamepadKey = Object.keys(gamepadShortcuts || {}).find(key => gamepadShortcuts[key] === action) || '';
        
        shortcutsText += `
          <tr>
            <td class="action-name">${action}</td>
            <td>${keyboardKey ? `<span class="shortcut-key">${keyboardKey}</span>` : '-'}</td>
            <td>${gamepadKey ? `<span class="shortcut-key">${gamepadKey}</span>` : '-'}</td>
          </tr>`;
      });
      
      shortcutsText += `
            </tbody>
          </table>
        </details>`;
    }
    
    shortcutsInfo.innerHTML = shortcutsText;
    
    // Disable/enable buttons
    prevBtn.disabled = currentIndex === 0;
    // Check if we're at the last example
    const isLastExample = currentIndex >= examples.length - 1;
    const noMoreExamples = currentIndex >= examples.length;
    
    // Only disable action buttons if we've gone past all examples
    yesBtn.disabled = noMoreExamples;
    noBtn.disabled = noMoreExamples;
    skipBtn.disabled = noMoreExamples;
    
    if (isLastExample && currentIndex < examples.length) {
      // We're on the last example but haven't annotated it yet
      status.textContent = `Example ${currentIndex + 1} of ${examples.length} (Last example)`;
    } else if (noMoreExamples) {
      status.textContent = 'All examples annotated!';
    }
  }
  
  // Annotation function
  function annotate(label) {
    const examples = model.get('examples');
    const currentIndex = model.get('current_index');
    const annotations = model.get('annotations');
    const showNotes = model.get('notes');
    
    if (currentIndex >= examples.length) return;
    
    const annotation = {
      index: currentIndex,
      example: examples[currentIndex],
      _label: label,
      _notes: showNotes ? notesField.value : '',
      _timestamp: new Date().toISOString()
    };
    
    // Add visual feedback to buttons
    const feedbackClass = label === 'yes' ? 'success-feedback' : 
                         label === 'no' ? 'error-feedback' : 
                         'skip-feedback';
    
    const button = label === 'yes' ? yesBtn : 
                  label === 'no' ? noBtn : 
                  skipBtn;
                  
    button.classList.add(feedbackClass);
    
    // Remove feedback class after animation
    setTimeout(() => {
      button.classList.remove(feedbackClass);
    }, 300);
    
    // Replace existing annotation for this index or add new one
    const newAnnotations = annotations.filter(ann => ann.index !== currentIndex);
    newAnnotations.push(annotation);
    model.set('annotations', newAnnotations);
    
    // Move to next example (even if it's past the end)
    model.set('current_index', currentIndex + 1);
    model.save_changes();
  }
  
  // Navigation function
  function navigate(direction) {
    const currentIndex = model.get('current_index');
    if (direction === 'prev' && currentIndex > 0) {
      // Add visual feedback to previous button
      prevBtn.classList.add('prev-feedback');
      
      // Remove feedback class after animation
      setTimeout(() => {
        prevBtn.classList.remove('prev-feedback');
      }, 300);
      
      model.set('current_index', currentIndex - 1);
      model.save_changes();
    }
  }
  
  // Button event listeners
  prevBtn.addEventListener('click', () => navigate('prev'));
  yesBtn.addEventListener('click', () => annotate('yes'));
  noBtn.addEventListener('click', () => annotate('no'));
  skipBtn.addEventListener('click', () => annotate('skip'));
  
  // Microphone button event listener
  micButton.addEventListener('click', () => {
    console.log('🎤 Microphone button clicked - isRecording:', isRecording);
    if (isRecording) {
      console.log('🎤 Button click stopping recording');
      stopSpeechRecognition();
    } else {
      console.log('🎤 Button click starting recording');
      startSpeechRecognition();
    }
  });
  
  
  // Helper function to parse keyboard shortcuts with modifiers
  function parseShortcut(event) {
    const modifiers = [];
    if (event.ctrlKey) modifiers.push('Ctrl');
    if (event.altKey) modifiers.push('Alt');
    if (event.shiftKey) modifiers.push('Shift');
    if (event.metaKey) modifiers.push('Meta');
    
    // Use event.code for consistent key identification
    let key = event.code;
    
    // Filter out modifier keys themselves
    const modifierCodes = ['ControlLeft', 'ControlRight', 'AltLeft', 'AltRight', 
                          'ShiftLeft', 'ShiftRight', 'MetaLeft', 'MetaRight'];
    if (modifierCodes.includes(key)) {
      return ''; // Don't capture just modifier keys
    }
    
    // Clean up the key code to make it more readable
    key = key.replace('Key', '').replace('Digit', ''); // KeyA → A, Digit1 → 1
    
    return modifiers.length > 0 ? `${modifiers.join('+')}+${key}` : key;
  }
  
  // Helper function to handle shortcut actions
  function handleAction(action) {
    switch(action) {
      case 'prev':
        navigate('prev');
        break;
      case 'yes':
        annotate('yes');
        break;
      case 'no':
        annotate('no');
        break;
      case 'skip':
        annotate('skip');
        break;
      case 'focus_notes':
        notesField.focus();
        break;
      case 'speech_notes':
        if (isRecording) {
          stopSpeechRecognition();
        } else {
          startSpeechRecognition();
        }
        break;
    }
  }
  
  // Keyboard shortcuts - attach to container instead of document
  container.addEventListener('keydown', (e) => {
    const shortcuts = model.get('shortcuts');
    const shortcutString = parseShortcut(e);
    
    console.log('🎹 Keydown event - shortcut:', shortcutString);
    
    // Handle speech toggle (same as mouse click)
    if (shortcuts[shortcutString] === 'speech_notes') {
      console.log('🎹 Keyboard speech key pressed - toggling recording');
      e.preventDefault();
      e.stopPropagation();
      handleAction('speech_notes');
      return;
    }
    
    if (shortcuts[shortcutString]) {
      // console.log('Executing action:', shortcuts[shortcutString]);
      e.preventDefault();
      e.stopPropagation();
      handleAction(shortcuts[shortcutString]);
    }
  });
  
  // No keyup listener needed - keyboard shortcut now works as toggle
  
  // Click handler removed to prevent autofocus in Marimo
  
  // Listen for model changes
  model.on('change:current_index', updateDisplay);
  model.on('change:examples', updateDisplay);
  model.on('change:notes', updateDisplay);
  model.on('change:shortcuts', updateDisplay);
  model.on('change:gamepad_shortcuts', updateDisplay);
  
  // Initialize speech recognition
  function initSpeechRecognition() {
    console.log('🔧 Initializing speech recognition...');
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (SpeechRecognition) {
      console.log('✅ Speech Recognition API found');
      speechRecognition = new SpeechRecognition();
      speechRecognition.continuous = true;
      speechRecognition.interimResults = true;
      speechRecognition.lang = 'en-US';
      
      speechRecognition.onstart = () => {
        console.log('🎤 Speech recognition started');
        isRecording = true;
        originalNotesText = notesField.value; // Store original text
        console.log('📝 Original notes text stored:', originalNotesText);
        updateRecordingUI();
      };
      
      speechRecognition.onresult = (event) => {
        console.log('📢 Speech result event - resultIndex:', event.resultIndex, 'total results:', event.results.length);
        let newFinalTranscript = '';
        let newInterimTranscript = '';
        
        // Only process NEW results from resultIndex onwards (prevents duplication)
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          const isFinal = event.results[i].isFinal;
          console.log(`  Result ${i}: "${transcript}" (final: ${isFinal})`);
          
          if (isFinal) {
            newFinalTranscript += transcript;
          } else {
            newInterimTranscript += transcript;
          }
        }
        
        console.log('✅ New final transcript:', newFinalTranscript);
        console.log('⏳ New interim transcript:', newInterimTranscript);
        
        // Add any new final text to our stored text
        if (newFinalTranscript) {
          const oldStoredText = originalNotesText;
          const separator = originalNotesText ? ' ' : '';
          originalNotesText = originalNotesText + separator + newFinalTranscript;
          console.log('💾 Updated stored text from:', oldStoredText, 'to:', originalNotesText);
        }
        
        // Show live results: stored final text + current interim text
        if (newInterimTranscript) {
          const separator = originalNotesText ? ' ' : '';
          const displayText = originalNotesText + separator + newInterimTranscript;
          console.log('👁️ Showing live text:', displayText);
          notesField.value = displayText;
          console.log('🔍 After setting value, notesField.value is now:', notesField.value);
        } else {
          // No interim text, just show the stored final text
          console.log('📋 Showing final text only:', originalNotesText);
          notesField.value = originalNotesText;
          console.log('🔍 After setting final value, notesField.value is now:', notesField.value);
        }
      };
      
      speechRecognition.onend = () => {
        console.log('🛑 Speech recognition ended. Final stored text:', originalNotesText);
        isRecording = false;
        
        // Ensure final text is preserved
        notesField.value = originalNotesText;
        console.log('📝 Set notes field to final text on end');
        updateRecordingUI();
      };
      
      speechRecognition.onerror = (event) => {
        console.log('❌ Speech recognition error:', event.error);
        isRecording = false;
        
        // Preserve text even on error
        notesField.value = originalNotesText;
        console.log('📝 Set notes field to stored text on error');
        updateRecordingUI();
      };
      
      speechAvailable = true;
      console.log('🎉 Speech recognition fully initialized and available');
    } else {
      console.log('❌ Speech recognition not available in this browser');
      speechAvailable = false;
    }
    
    updateMicButtonState();
  }
  
  function updateRecordingUI() {
    if (isRecording) {
      micButton.classList.add('recording');
      notesField.classList.add('recording');
      micButton.innerHTML = '🔴';
      micButton.title = 'Recording... (release to stop)';
    } else {
      micButton.classList.remove('recording');
      notesField.classList.remove('recording');
      micButton.innerHTML = speechAvailable ? '🎤' : '❌';
      micButton.title = speechAvailable ? 'Click to record speech or hold Alt+6' : 'Speech recognition not available';
    }
  }
  
  function updateMicButtonState() {
    micButton.disabled = !speechAvailable;
    updateRecordingUI();
  }
  
  function startSpeechRecognition() {
    console.log('🚀 startSpeechRecognition called - speechAvailable:', speechAvailable, 'isRecording:', isRecording);
    if (speechAvailable && !isRecording) {
      try {
        console.log('▶️ Calling speechRecognition.start()');
        speechRecognition.start();
      } catch (error) {
        console.log('💥 Error starting speech recognition:', error);
      }
    } else {
      console.log('⚠️ Cannot start - speechAvailable:', speechAvailable, 'isRecording:', isRecording);
    }
  }
  
  function stopSpeechRecognition() {
    console.log('🛑 stopSpeechRecognition called - speechAvailable:', speechAvailable, 'isRecording:', isRecording);
    if (speechAvailable && isRecording) {
      try {
        console.log('⏹️ Calling speechRecognition.stop()');
        speechRecognition.stop();
      } catch (error) {
        console.log('💥 Error stopping speech recognition:', error);
      }
    } else {
      console.log('⚠️ Cannot stop - speechAvailable:', speechAvailable, 'isRecording:', isRecording);
    }
  }
  
  // Initialize speech recognition
  initSpeechRecognition();
  
  // Initial display
  updateDisplay();
  
  // No autofocus to prevent jumping in Marimo notebooks
  
  // Gamepad support (variables already declared above)
  
  // Gamepad display now handled by simple indicator emoji
  
  // Gamepad connection events
  window.addEventListener('gamepadconnected', (e) => {
    console.log('Gamepad connected:', e.gamepad);
    gamepadConnected = true;
    gamepadIndex = e.gamepad.index;
    lastGamepadEvent = 'Connected';
    gamepadIndicator.style.display = 'inline';
  });
  
  window.addEventListener('gamepaddisconnected', (e) => {
    console.log('Gamepad disconnected:', e.gamepad);
    gamepadConnected = false;
    gamepadIndex = -1;
    lastGamepadEvent = 'Disconnected';
    gamepadIndicator.style.display = 'none';
  });
  
  // Gamepad polling for button presses
  let lastButtonStates = {};
  
  function pollGamepad() {
    if (!gamepadConnected) {
      requestAnimationFrame(pollGamepad);
      return;
    }
    
    const gamepads = navigator.getGamepads();
    const gamepad = gamepads[gamepadIndex];
    
    if (gamepad) {
      // Check for button presses
      gamepad.buttons.forEach((button, index) => {
        const buttonKey = `button_${index}`;
        const wasPressed = lastButtonStates[buttonKey] || false;
        const isPressed = button.pressed;
        
        // Update currently pressed buttons set
        if (isPressed) {
          currentlyPressedButtons.add(index);
        } else {
          currentlyPressedButtons.delete(index);
        }
        
        // Detect button press (transition from not pressed to pressed)
        if (isPressed && !wasPressed) {
          lastGamepadEvent = `Button ${index} pressed`;
          gamepadIndicator.style.display = 'inline'; // Show indicator on any button press
          // console.log(`Gamepad button ${index} pressed`);
          
          // Check for mapped gamepad actions
          const gamepadShortcuts = model.get('gamepad_shortcuts');
          if (gamepadShortcuts[buttonKey]) {
            // Handle speech push-to-talk
            if (gamepadShortcuts[buttonKey] === 'speech_notes') {
              console.log('🎮 Gamepad speech button pressed - starting recording');
              speechGamepadPressed = true;
              startSpeechRecognition();
            } else {
              // console.log(`Executing gamepad action: ${gamepadShortcuts[buttonKey]}`);
              handleAction(gamepadShortcuts[buttonKey]);
            }
          }
        }
        
        // Detect button release (transition from pressed to not pressed)
        if (!isPressed && wasPressed) {
          // Check for speech push-to-talk release
          const gamepadShortcuts = model.get('gamepad_shortcuts');
          if (gamepadShortcuts[buttonKey] === 'speech_notes' && speechGamepadPressed) {
            console.log('🎮 Gamepad speech button released - stopping recording');
            speechGamepadPressed = false;
            stopSpeechRecognition();
          }
        }
        
        lastButtonStates[buttonKey] = isPressed;
      });
      
      // Check for axis movements (significant changes)
      gamepad.axes.forEach((axis, index) => {
        const axisKey = `axis_${index}`;
        const lastValue = lastButtonStates[axisKey] || 0;
        const currentValue = axis;
        
        // Detect significant axis movement (threshold of 0.5)
        if (Math.abs(currentValue - lastValue) > 0.1) {
          lastGamepadEvent = `Axis ${index}: ${currentValue.toFixed(2)}`;
          gamepadIndicator.style.display = 'inline'; // Show indicator on axis movement
          // console.log(`Gamepad axis ${index} moved to ${currentValue.toFixed(2)}`);
        }
        
        lastButtonStates[axisKey] = currentValue;
      });
      
      // No need to update display here - gamepad actions handle their own updates
    }
    
    // Continue polling
    requestAnimationFrame(pollGamepad);
  }
  
  // Start gamepad polling
  pollGamepad();
  
  // Also check for gamepads that might already be connected
  const existingGamepads = navigator.getGamepads();
  for (let i = 0; i < existingGamepads.length; i++) {
    if (existingGamepads[i]) {
      console.log('Found existing gamepad:', existingGamepads[i]);
      gamepadConnected = true;
      gamepadIndex = i;
      lastGamepadEvent = 'Connected';
      gamepadIndicator.style.display = 'inline';
      break;
    }
  }
}

export default { render };
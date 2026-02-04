#!/usr/bin/env node
/**
 * Test suite for decision-logger.cjs
 */

const { classifyMode, captureDecision } = require('./decision-logger.cjs');

console.log('=== DECISION LOGGER TESTS ===\n');

// Test 1: Classification Logic
console.log('--- Test 1: Classification Logic ---');

const testCases = [
  {
    name: 'Permission-seeking response',
    response: 'Should I start building that feature for you?',
    expected: 'permission-seeking'
  },
  {
    name: 'Permission-seeking with "want me to"',
    response: 'Do you want me to run the tests now?',
    expected: 'permission-seeking'
  },
  {
    name: 'Reactive explanation (no tools)',
    response: 'The dopamine system works by tracking neurochemical states over time. It logs events to a JSONL file and updates the state based on triggers.',
    expected: 'reactive-explanation'
  },
  {
    name: 'Mixed (has question)',
    response: 'Here is the code. Does this look right?',
    expected: 'mixed'
  }
];

testCases.forEach(tc => {
  const result = classifyMode(tc.response);
  const pass = result === tc.expected;
  console.log(`${pass ? '✅' : '❌'} ${tc.name}`);
  console.log(`   Expected: ${tc.expected}, Got: ${result}`);
});

// Test 2: Tool call extraction
console.log('\n--- Test 2: Tool Call Extraction ---');

// Simulate a response with tool calls (using the format in responses)
const toolResponse = 'Building the system. <invoke name="Write"><param>test</param></invoke> <invoke name="exec"><param>ls</param></invoke>';
const { extractToolCalls } = require('./decision-logger.cjs');

// Note: extractToolCalls is not exported, test via captureDecision
const decision = captureDecision({
  userMessage: 'Build it',
  assistantResponse: toolResponse
});

console.log('Decision captured:');
console.log(JSON.stringify(decision, null, 2));

// Test 3: Confidence scoring
console.log('\n--- Test 3: Confidence Scoring ---');

const confidenceTests = [
  { response: 'Done. Fixed the bug. ✅', expectHigh: true },
  { response: 'Maybe this will work? Not sure about the edge cases.', expectHigh: false },
  { response: 'Building now. Will verify when complete.', expectHigh: true }
];

confidenceTests.forEach(ct => {
  const dec = captureDecision({ assistantResponse: ct.response });
  const isHigh = dec.confidence > 0.6;
  const pass = isHigh === ct.expectHigh;
  console.log(`${pass ? '✅' : '❌'} "${ct.response.substring(0, 40)}..."`);
  console.log(`   Confidence: ${dec.confidence.toFixed(2)}, Expected ${ct.expectHigh ? 'HIGH' : 'LOW'}`);
});

// Test 4: Check decision log creation
console.log('\n--- Test 4: Decision Log File ---');
const fs = require('fs');
const path = require('path');
const DECISION_LOG = path.join(__dirname, 'dopamine-system/decision-log.jsonl');

if (fs.existsSync(DECISION_LOG)) {
  const lines = fs.readFileSync(DECISION_LOG, 'utf8').split('\n').filter(l => l.trim());
  console.log(`✅ decision-log.jsonl exists with ${lines.length} entries`);
} else {
  console.log('⚠️  decision-log.jsonl does not exist yet (created on first capture)');
}

console.log('\n=== TESTS COMPLETE ===');

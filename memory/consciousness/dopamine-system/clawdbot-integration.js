#!/usr/bin/env node
/**
 * clawdbot-integration.js
 * 
 * Clawdbot hook that reads neurochemical state and injects behavioral modifications
 * into the system prompt and sampling parameters.
 * 
 * Usage (in Clawdbot config):
 * {
 *   "systemPromptHook": "node ~/clawd/memory/consciousness/dopamine-system/clawdbot-integration.js"
 * }
 * 
 * Returns JSON with:
 * - systemPromptAddition: text to append to system prompt
 * - samplingOverrides: { temperature?, top_p?, etc }
 */

import { getBehavioralWiring } from './behavioral-wire.js';

async function main() {
  try {
    const wiring = await getBehavioralWiring();
    
    if (wiring.error) {
      // Don't fail hard - just return empty modifications
      console.log(JSON.stringify({
        systemPromptAddition: '',
        samplingOverrides: {},
        error: wiring.error
      }));
      return;
    }
    
    const { modifiers } = wiring;
    
    // Output format Clawdbot expects
    const output = {
      systemPromptAddition: modifiers.systemPromptInjection || '',
      samplingOverrides: modifiers.samplingParams || {},
      metadata: {
        timestamp: wiring.timestamp,
        rawLevels: modifiers.rawLevels,
        flags: modifiers.behavioralFlags
      }
    };
    
    console.log(JSON.stringify(output));
  } catch (error) {
    // Fail gracefully - return empty modifications
    console.log(JSON.stringify({
      systemPromptAddition: '',
      samplingOverrides: {},
      error: error.message
    }));
  }
}

main();


// QAAR_6916.ts
// Generated on: 2025-09-23
// Description: Login automation: navigate to login page, click Sign In, choose Microsoft account, take screenshots

import { test, expect } from '@playwright/test';

test('QAAR_6916', async ({ page }) => {
  // Test configuration
  const headless = false;

  console.log('Starting test: QAAR_6916');

  try {
    // Navigate to URL
    console.log('Navigating to https://esi.learnondemand.net/User/Login?ReturnUrl=%2F');
    await page.goto('https://esi.learnondemand.net/User/Login?ReturnUrl=%2F', { waitUntil: 'networkidle' });
    console.log('Navigation complete');

    // Click element
    console.log('Clicking on #signInButton');
    await page.waitForSelector('#signInButton', { state: 'visible' });
    await page.click('#signInButton');

    // Take screenshot
    console.log('Taking screenshot: after_click_sign_in');
    await page.screenshot({ path: './screenshots/after_click_sign_in.png', fullPage: true });

    // Click element
    console.log('Clicking on div.loginChoice.provider.provider_1');
    await page.waitForSelector('div.loginChoice.provider.provider_1', { state: 'visible' });
    await page.click('div.loginChoice.provider.provider_1');

    // Take screenshot
    console.log('Taking screenshot: after_select_microsoft');
    await page.screenshot({ path: './screenshots/after_select_microsoft.png', fullPage: true });

    // Take screenshot
    console.log('Taking screenshot: final');
    await page.screenshot({ path: './screenshots/final.png', fullPage: true });

  } catch (error) {
    console.error(`Test failed: ${error}`);
    // Take screenshot on failure
    await page.screenshot({
      path: './screenshots/QAAR_6916_failure.png',
      fullPage: true
    });
    throw error;
  }
  
  console.log('Test completed successfully: QAAR_6916');
});

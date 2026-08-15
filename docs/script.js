/* ==============================================================================
   Speed2Audit Landing Page — Interactive Logic
   ============================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // Tab Switcher for Quickstart
  const tabButtons = document.querySelectorAll('.tab-btn');
  const codeSnippets = {
    docker: `# 1. Clone repository
git clone https://github.com/hugonotnice/speed2audit.git
cd speed2audit

# 2. Configure Gemini API key
cp .env.example .env
# Edit .env and paste your GEMINI_API_KEY

# 3. Start everything in 1 click
docker compose up -d

# Open Cockpit at http://localhost:8000`,
    uv: `# 1. Install dependencies
git clone https://github.com/hugonotnice/speed2audit.git
cd speed2audit
uv sync --all-groups

# 2. Start WAHA WhatsApp gateway
docker run -d --name waha -p 3000:3000 devlikeapro/waha

# 3. Launch Chainlit Cockpit
uv run chainlit run src/speed2audit/app.py -w`
  };

  const codeDisplay = document.getElementById('code-display');
  const copyBtn = document.getElementById('copy-btn');

  let currentSnippet = 'docker';

  function renderCode(type) {
    if (!codeDisplay) return;
    const lines = codeSnippets[type].split('\n');
    codeDisplay.innerHTML = lines.map(line => {
      if (line.startsWith('#')) {
        return `<div class="code-line"><span class="code-comment">${escapeHtml(line)}</span></div>`;
      } else if (line.trim() === '') {
        return `<div class="code-line">&nbsp;</div>`;
      } else {
        return `<div class="code-line"><span class="code-prompt">$</span> <span>${escapeHtml(line)}</span></div>`;
      }
    }).join('');
  }

  function escapeHtml(text) {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      tabButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const tab = btn.getAttribute('data-tab');
      currentSnippet = tab;
      renderCode(tab);
    });
  });

  // Copy to Clipboard
  if (copyBtn) {
    copyBtn.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(codeSnippets[currentSnippet]);
        const originalText = copyBtn.innerHTML;
        copyBtn.innerHTML = `✓ Copied!`;
        copyBtn.style.borderColor = 'var(--accent-emerald)';
        copyBtn.style.color = 'var(--accent-emerald)';
        
        setTimeout(() => {
          copyBtn.innerHTML = originalText;
          copyBtn.style.borderColor = '';
          copyBtn.style.color = '';
        }, 2000);
      } catch (err) {
        console.error('Failed to copy code: ', err);
      }
    });
  }

  // Initial render
  renderCode('docker');
});
